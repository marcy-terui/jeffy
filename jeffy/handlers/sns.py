import functools
from typing import Callable

from jeffy.encoding import Encoding
from jeffy.validator import Validator, NoneValidator


class SnsHandlerMixin(object):
    """
    SNS event handler decorators.
    """
    def sns(
        self,
        encoding: Encoding,
        validator: Validator = NoneValidator()) -> Callable:
        """
        Decorator for SNS event. Automatically divide 'Records' for making it easy to treat it
        inside main process of Lambda.

        Usage::
            >>> from jeffy.framework import get_app
            >>> from jeffy.encoding.json import JsonEncoding
            >>> app = get_app()
            >>> @app.handlers.sns(encoding=JsonEncoding())
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        def _sns(self, func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(event, context):
                for record in event['Records']:
                    message = encoding.decode(record['Sns']['Message'].encode('utf-8'))
                    validator.varidate(message)
                    self.capture_correlation_id(message)
                try:
                    return func(message, context)
                except Exception as e:
                    self.app.logger.exception(e)
                    raise e
            return wrapper
        return _sns
