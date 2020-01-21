import boto3
import json
from typing import Any


class Kinesis():
    """
    Kinesis Client.
    """

    _resource = None

    @classmethod
    def get_resource(cls) -> boto3.client:
        """
        Get boto3 client for Kinesis.

        Usage::
            >>> from jeffy.sdk.kinesis import Kinesis
            >>> Kinesis.get_resource().put_record(...)
        """
        if Kinesis._resource is None:
            Kinesis._resource = boto3.client('kinesis')
        return Kinesis._resource

    @classmethod
    def put_record(cls, stream_name: str, data: Any, partition_key: str, correlation_id: str = ''):
        """
        Put recourd to Kinesis Stream with correlation_id.

        Usage::
            >>> from jeffy.sdk.kinesis import Kinesis
            >>> Sqs.put_record(...)
        """
        return cls.get_resource().put_record(
            StreamName=stream_name,
            Data=json.dumps({
                'correlation_id': correlation_id,
                'item': data
            }),
            PartitionKey=partition_key,
        )