import boto3


class S3():
    """
    S3 Client.
    """

    _resource = None

    @classmethod
    def get_resource(cls):
        """
        Get boto3 client for S3.

        Usage::
            >>> from jeffy.sdk.sns import S3
            >>> S3.get_resource().upload_file(...)
        """
        if S3._resource is None:
            S3._resource = boto3.client('s3')
        return S3._resource

    @classmethod
    def upload_file(cls, file_path: str, bucket_name: str, object_name: str, correlation_id: str = ''):
        """
        Upload file to S3 bucket with correlationid.

        Usage::
            >>> from jeffy.sdk.s3 import S3
            >>> S3.upload_file(...)
        """
        return cls.get_resource().upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=object_name,
            ExtraArgs={'Metadata': {'correlation_id': correlation_id}}
        )
