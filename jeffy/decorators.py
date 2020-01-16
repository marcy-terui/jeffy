import logging
import json
import base64
import os
import functools
import traceback
import uuid
import jsonschema
from typing import Dict, str, Callable

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class Decorators(object):
    def auto_logging(self, func: Callable) -> Callable:
        """
        Automatically logs payload event and return value of lambda
        and when error occurs.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.auto_logging
            ... def handler(event, context):
            ...     return event['body']['foo']
        """

        @functools.wraps(func)
        def wrapper(event, context):
            logger.info(event)
            try:
                result = func(event, context)
                logger.info(result)
                return result
            except Exception as e:
                logger.error(traceback.format_exc())
                raise e
        return wrapper

    def capture_correlation_id(self, payload: Dict = {}) -> str:
        """
        Automatically generates and capurures correlation_id.

        Parameters
        ----------
        payload: dict
            Payload event with including `x-correlationid` which should be passed
        Returns
        -------
        correlation_id : str
        """
        if payload.get('x-correlation-id') is None:
            correlation_id = str(uuid.uuid4())
        else:
            correlation_id = payload.get('x-correlation-id')
        logger.info('x-correlation-id:{}'.format(correlation_id))
        return correlation_id

    def schedule(self, func: Callable) -> Callable:
        """
        Decorator for schedule event. just captures correlation id before main process.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.schedule
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        @functools.wraps(func)
        def wrapper(event, context):
            event['CorrelationId'] = self.capture_correlation_id()
            try:
                func(event, context)
            except Exception as e:
                raise e
        return wrapper

    def sqs(self, func: Callable) -> Callable:
        """
        Decorator for sqs event. Automatically divide 'Records' for making it easy to treat it
        inside main process of Lambda.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.sqs
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        @functools.wraps(func)
        def wrapper(event, context):
            for record in event['Records']:
                message = json.loads(record['body'])
                message['x-correlation-id'] = self.capture_correlation_id(payload=message)
                try:
                    return func(message, context)
                except Exception as e:
                    raise e
        return wrapper

    def dynamodb_stream(self, func: Callable) -> Callable:
        """
        Decorator for Dynamodb stream event. Automatically divide 'Records' for making it easy to treat it
        inside main process of Lambda.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.dynamodb_stream
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        @functools.wraps(func)
        def wrapper(event, context):
            for record in event['Records']:
                record['dynamodb']['x-correlation-id'] = self.capture_correlation_id(payload=record['dynamodb'])
                try:
                    return func(record['dynamodb'], context)
                except Exception as e:
                    raise e
        return wrapper

    def kinesis_stream(self, func: Callable) -> Callable:
        """
        Decorator for Kinesis stream event. Automatically divide 'Records' for making it easy to treat it
        inside main process of Lambda.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.kinesis_stream
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        @functools.wraps(func)
        def wrapper(event, context):
            for record in event['Records']:
                payload = json.loads(base64.b64decode(record['kinesis']['data']).decode())
                payload['x-correlation-id'] = self.capture_correlation_id(payload=payload)
                try:
                    return func(payload, context)
                except Exception as e:
                    raise e
        return wrapper

    def sns(self, func: Callable) -> Callable:
        """
        Decorator for SNS event. Automatically divide 'Records' for making it easy to treat it
        inside main process of Lambda.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.sns
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        @functools.wraps(func)
        def wrapper(event, context):
            for record in event['Records']:
                message = json.loads(record['Sns']['Message'])
                message['x-correlation-id'] = self.capture_correlation_id(payload=message)
            try:
                return func(message, context)
            except Exception as e:
                raise e
        return wrapper

    def api(self, func: Callable, response_headers: Dict = {}) -> Callable:
        """
        Decorator for API Gateway event. Automatically parse string if the 'body' can be parsed as Dictionary.
        Automatically returs 500 error if unexpected error happens.

        Parameters
        ----------
        response_headers: dict
            Response headers when 500 error occurs.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.api()
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        @functools.wraps(func)
        def wrapper(event, context):
            try:
                event['x-correlation-id'] = self.capture_correlation_id(payload=event.get('headers'))
                if event.get('body') is not None:
                    event['body'] = json.loads(event.get('body'))
                return func(event, context)
            except TypeError:  # 入力がJSONでない場合
                return func(event, context)
            except json.decoder.JSONDecodeError:  # 入力がJSONでない場合
                return func(event, context)
            except Exception:
                return {
                    'statusCode': 500,
                    'headers': response_headers,
                    'body': json.dumps({
                        'error_message': 'Internal Server Error'
                    })
                }
        return wrapper

    def json_scheme_validator(self, json_scheme: Dict) -> Callable:
        """
        Decorator for Json scheme valiidator. Automatically validate body with following json scheme.

        Parameters
        ----------
        json_scheme: dict
            Json scheme definition for validation.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.json_scheme_validator(
            >>>     json_scheme={
            >>>         'type': 'object',
            >>>         'properties': {
            >>>             'message': {'type': 'string'}
            >>>         }
            >>>     }
            >>> )
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        def wrapper_wrapper(func):
            @functools.wraps(func)
            def wrapper(event, context):
                try:
                    jsonschema.validate(json.loads(event.get('body')), json_scheme)
                    return func(event, context)
                except (json.decoder.JSONDecodeError, jsonschema.ValidationError, TypeError) as e:
                    raise e
            return wrapper
        return wrapper_wrapper

    def api_json_scheme_validator(self, json_scheme: Dict, response_headers: Dict = {}) -> Callable:
        """
        Decorator for Json scheme valiidator for api. Automatically validate body with following json scheme.
        Returns 400 error if the validation failes.

        Parameters
        ----------
        json_scheme: dict
            Json scheme definition for validation.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.decorator.api_json_scheme_validator()
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        def wrapper_wrapper(func):
            @functools.wraps(func)
            def wrapper(event, context):
                try:
                    jsonschema.validate(json.loads(event.get('body')), json_scheme)
                    return func(event, context)
                except (json.decoder.JSONDecodeError, TypeError):
                    return {
                        'statusCode': 400,
                        'headers': response_headers,
                        'body': json.dumps({
                            'error_message': 'The request was not JSON format.'
                        })
                    }
                except jsonschema.ValidationError as e:
                    return {
                        'statusCode': 400,
                        'headers': response_headers,
                        'body': json.dumps({
                            'error_message': e.message
                        })
                    }
            return wrapper
        return wrapper_wrapper
