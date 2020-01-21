import boto3
import json
from typing import Any


class Sns():
    """
    SNS Client.
    """

    _resource = None

    @classmethod
    def get_resource(cls) -> boto3.client:
        """
        Get boto3 client for SNS.

        Usage::
            >>> from jeffy.sdk.sns import Sns
            >>> Sns.get_resource().publish(...)
        """
        if Sns._resource is None:
            Sns._resource = boto3.client('sns')
        return Sns._resource

    @classmethod
    def publish(cls, topic_arn: str, message: Any, subject: str, correlation_id: str = ''):
        """
        Send message to SNS Topic with correlationid.

        Usage::
            >>> from jeffy.sdk.sns import Sns
            >>> Sns.publish(...)
        """
        return cls.get_resource().publish(
            TopicArn=topic_arn,
            Message=json.dumps({
                'correlation_id': correlation_id,
                'item': message
            }),
            Subject=subject
        )
