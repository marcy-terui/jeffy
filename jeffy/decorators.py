import logging
import json
import base64
import os
import functools
import traceback
import uuid
import jsonschema
from typing import Callable

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class Decorators(object):
    def auto_logging(self, func: Callable) -> Callable:
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

    def capture_correlation_id(self, payload=None):
        if payload.get('x-correlation-id') is None:
            correlation_id = str(uuid.uuid4())
        else:
            correlation_id = payload.get('x-correlation-id')
        logger.info('x-correlation-id:{}'.format(correlation_id))
        return correlation_id

    def schedule(self, func: Callable) -> Callable:
        """スケジュールイベントのデコレータ."""
        @functools.wraps(func)
        def wrapper(event, context):
            event['CorrelationId'] = self.capture_correlation_id()
            try:
                func(event, context)
            except Exception as e:
                raise e
        return wrapper

    def sqs(self, func):
        """SQSイベントのデコレータ."""
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

    def dynamodb_stream(self, func):
        """Dynamodbイベントのデコレータ."""
        @functools.wraps(func)
        def wrapper(event, context):
            for record in event['Records']:
                record['dynamodb']['x-correlation-id'] = self.capture_correlation_id(payload=record['dynamodb'])
                try:
                    return func(record['dynamodb'], context)
                except Exception as e:
                    raise e
        return wrapper

    def kinesis_stream(self, func):
        """KinesisStreamイベントのデコレータ."""
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

    def sns(self, func):
        """SNSイベントのデコレータ."""
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

    def api(self, func, response_headers={}):
        """APIのデコレータ."""
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

    def json_scheme_validator(self, json_scheme):
        """JSON Scheme Validatorのデコレータ."""
        def wrapper_wrapper(func):
            @functools.wraps(func)
            def wrapper(event, context):
                try:
                    jsonschema.validate(json.loads(event.get('body')), json_scheme)
                    return func(event, context)
                except TypeError as e:
                    raise e
                except json.decoder.JSONDecodeError as e:
                    raise e
                except jsonschema.ValidationError as e:
                    raise e
            return wrapper
        return wrapper_wrapper

    def api_json_scheme_validator(self, json_scheme, response_headers={}):
        """JSON Scheme Validatorのデコレータ."""
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

