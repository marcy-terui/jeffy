import json
import boto3
from typing import Any


class Sqs():
    """
    SQS Client.
    """

    _resource = None

    @classmethod
    def get_resource(cls) -> boto3.client:
        """
        Get boto3 client for SQS.

        Usage::
            >>> from jeffy.sdk.sqs import Sqs
            >>> Sqs.get_resource().send_message(...)
        """
        if Sqs._resource is None:
            Sqs._resource = boto3.client('sqs')
        return Sqs._resource

    @classmethod
    def send_message(cls, message: Any, queue_url: str, correlation_id: str = ''):
        """
        Send message to SQS Queue with correlationid.

        Usage::
            >>> from jeffy.sdk.sqs import Sqs
            >>> Sqs.send_message(...)
        """
        try:
            return cls.get_resource().send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    'correlation_id': correlation_id,
                    'item': message
                })
            )
        except Exception as e:
            raise e
