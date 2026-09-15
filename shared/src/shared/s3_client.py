import os

from minio import Minio

from shared.singleton import Singleton


class S3Client(metaclass=Singleton):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = True) -> None:
        self.client: Minio = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def create_bucket(self, bucket_name: str) -> None:
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        self.client.fput_object(bucket_name, object_name, file_path)

    def get_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        self.client.fget_object(bucket_name, object_name, file_path)

    def list_objects(
            self,
            bucket_name: str,
            prefix: str = "",
            recursive: bool = False
        ) -> list:
        return list(
            self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive)
        )

    def delete_object(self, bucket_name: str, object_name: str) -> None:
        self.client.remove_object(bucket_name, object_name)

    def delete_bucket(self, bucket_name: str) -> None:
        self.client.remove_bucket(bucket_name)


def get_s3_client() -> S3Client:
    endpoint = os.getenv("S3_ENDPOINT", "localhost:9000")
    access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
    secure = os.getenv("S3_SECURE", "false").strip().lower() in {"1", "true", "yes", "on"}
    return S3Client(endpoint, access_key, secret_key, secure=secure)
