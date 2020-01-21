import logging
import os
import traceback
from typing import Dict, Any


class Logger(object):
    """
    Jeffy logger class.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.getenv('JEFFY_LOG_LEVEL', 'INFO'))
        self.log_context = {
            'aws_region': os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION'),
            'function_name': os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
            'function_version': os.environ.get('AWS_LAMBDA_FUNCTION_VERSION'),
            'function_memory_size': os.environ.get('AWS_LAMBDA_FUNCTION_MEMORY_SIZE'),
            'log_group_name': os.environ.get('AWS_LAMBDA_LOG_GROUP_NAME'),
            'log_stream_name': os.environ.get('AWS_LAMBDA_LOG_STREAM_NAME')
        }

    def setup(self, attributes: Dict) -> None:
        """
        Inject addtional infomation to logs.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.log.setup(
            >>>     {
            >>>         "attribute1": "value1",
            >>>         "attribute2": "value2",
            >>>         "attribute3": "value3"
            >>>     }
            >>> )
        """
        self.log_context.update(attributes)

    def debug(self, message: Any) -> None:
        """
        Output debug log.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.log.debug('aaaa')
        """
        message_obj = {'message': message}
        message_obj.update(self.log_context)
        self.logger.info(message_obj)

    def info(self, message: Any) -> None:
        """
        Output info log.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            >>> @app.log.info('aaaa')
        """
        message_obj = {'message': message}
        message_obj.update(self.log_context)
        self.logger.info(message_obj)

    def error(self, error: Exception) -> None:
        """
        Output error log.

        Usage::
            >>> from jeffy.framework import setup
            >>> app = setup()
            ... def handler(event, context):
            ...     try:
            ...         return event['body']['foo']
            >>>     except Exception as e:
            >>>         app.log.error(e)
        """
        message_obj = {
            'error_message': error,
            'stack_trace': traceback.format_exc()
        }
        message_obj.update(self.log_context)
        self.logger.error(message_obj)
