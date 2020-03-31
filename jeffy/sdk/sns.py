import boto3
import json
from typing import Any

from jeffy.sdk import SdkBase


class Sns(SdkBase):
    """
    SNS Client.
    """

    _resource = None

    def get_resource(self) -> boto3.client:
        """
        Get boto3 client for SNS.

        Usage::
            >>> from jeffy.sdk.sns import Sns
            >>> Sns.get_resource().publish(...)
        """
        if Sns._resource is None:
            Sns._resource = boto3.client('sns')
        return Sns._resource

    def publish(self, topic_arn: str, message: Any, subject: str, correlation_id: str = ''):
        """
        Send message to SNS Topic with correlationid.

        Usage::
            >>> from jeffy.sdk.sns import Sns
            >>> Sns.publish(...)
        """
        if correlation_id == '':
            correlation_id = self.app.correlation_id
        return self.get_resource().publish(
            TopicArn=topic_arn,
            Message=json.dumps({
                self.app.correlation_attr_name: correlation_id,
                'item': message
            }),
            Subject=subject
        )
