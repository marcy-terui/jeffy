import boto3
import json
from typing import Any

from jeffy.sdk import SdkBase


class Kinesis(SdkBase):
    """
    Kinesis Client.
    """

    _resource = None

    def get_resource(self) -> boto3.client:
        """
        Get boto3 client for Kinesis.

        Usage::
            >>> from jeffy.sdk.kinesis import Kinesis
            >>> Kinesis.get_resource().put_record(...)
        """
        if Kinesis._resource is None:
            Kinesis._resource = boto3.client('kinesis')
        return Kinesis._resource

    def put_record(self, stream_name: str, data: Any, partition_key: str, correlation_id: str = ''):
        """
        Put recourd to Kinesis Stream with correlation_id.

        Usage::
            >>> from jeffy.sdk.kinesis import Kinesis
            >>> Kinesis().put_record(...)
        """
        if correlation_id == '':
            correlation_id = self.app.correlation_id
        return self.get_resource().put_record(
            StreamName=stream_name,
            Data=json.dumps({
                self.app.correlation_attr_name: correlation_id,
                'item': data
            }),
            PartitionKey=partition_key,
        )
