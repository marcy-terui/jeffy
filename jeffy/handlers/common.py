import functools
from typing import Callable

from jeffy.validator import Validator, NoneValidator


class CommonHandlerMixin(object):
    """
    Common event handler decorators.
    """
    def common(
        self,
        validator: Validator = NoneValidator()) -> Callable:
        """
        Automatically logs payload of events and errors with the correlation ID.

        Usage::
            >>> from jeffy.framework import get_app
            >>> app = get_app()
            >>> @app.handlers.event_logging
            ... def handler(event, context):
            ...     return event['body']['foo']
        """
        def _common(self, func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(event, context):
                self.capture_correlation_id(event)
                self.app.logger.info(event)
                try:
                    result = func(event, context)
                    self.app.logger.info(result)
                    return result
                except Exception as e:
                    self.app.logger.exception(e)
                    raise e
            return wrapper
        return _common
