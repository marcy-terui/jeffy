import boto3

from jeffy.sdk import SdkBase


class S3(SdkBase):
    """
    S3 Client.
    """

    _resource = None

    def get_resource(self):
        """
        Get boto3 client for S3.

        Usage::
            >>> from jeffy.sdk.sns import S3
            >>> S3.get_resource().upload_file(...)
        """
        if S3._resource is None:
            S3._resource = boto3.client('s3')
        return S3._resource

    def upload_file(self, file_path: str, bucket_name: str, object_name: str, correlation_id: str = ''):
        """
        Upload file to S3 bucket with correlationid.

        Usage::
            >>> from jeffy.sdk.s3 import S3
            >>> S3.upload_file(...)
        """
        if correlation_id == '':
            correlation_id = self.app.correlation_id
        return self.get_resource().upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=object_name,
            ExtraArgs={
                'Metadata': {
                    self.app.correlation_attr_name: correlation_id
                }
            }
        )
