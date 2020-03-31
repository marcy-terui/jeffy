import logging
import json
import uuid
import jsonschema
from typing import Dict, Callable

from jeffy.framework import get_app
from jeffy.encoding import Encoding
from jeffy.handlers.common import CommonHandlerMixin
from jeffy.handlers.rest_api import RestApiHandlerMixin
from jeffy.handlers.s3 import S3HandlerMixin
from jeffy.handlers.schedule import ScheduleHandlerMixin
from jeffy.handlers.sns import SnsHandlerMixin
from jeffy.handlers.sqs import SqsHandlerMixin
from jeffy.handlers.streams import StreamsHandlerMixin


class Handlers(
    CommonHandlerMixin,
    RestApiHandlerMixin,
    S3HandlerMixin,
    ScheduleHandlerMixin,
    SnsHandlerMixin,
    SqsHandlerMixin,
    StreamsHandlerMixin):
    """
    Jeffy event handler decorators.
    """
    def __init__(self):
        self.app = get_app()

    def capture_correlation_id(self, payload: Dict = {}) -> str:
        """
        Automatically generates and capurures the correlation ID.

        Parameters
        ----------
        payload: dict
            Payload event with including correlation attribute
        Returns
        -------
        correlation_id : str
        """
        if self.app.correlation_attr_name in payload:
            correlation_id = payload.get(self.app.correlation_attr_name)
        elif self.app.correlation_id_header in payload:
            correlation_id = payload.get(self.app.correlation_id_header)
        else:
            correlation_id = str(uuid.uuid4())
        self.app.logger.update_context({self.app.correlation_attr_name: correlation_id})
        self.app.correlation_id = correlation_id
        return correlation_id
