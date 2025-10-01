import io
from contextlib import asynccontextmanager

from aiobotocore.session import get_session

from app.config.main import settings


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_like: io.BytesIO, object_name: str):
        try:
            ext = object_name.split(".")[-1].lower()
            content_types = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "gif": "image/gif",
                "bmp": "image/bmp",
                "webp": "image/webp",
                "tiff": "image/tiff",
                "svg": "image/svg+xml"
            }
            content_type = content_types.get(ext, "application/octet-stream")

            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file_like,
                    ACL="public-read",
                    ContentType=content_type
                )
        except Exception as e:  # noqa
            print(e)  # noqa
            
    async def delete_file(self, object_name: str):
        async with self.get_client() as client:
            await client.delete_object(Bucket=self.bucket_name, Key=object_name)

    async def get_file(self, object_name: str, destination_path: str):
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
            data = await response["Body"].read()
            with open(destination_path, "wb") as file:
                file.write(data)


s3_client = S3Client(
    access_key=settings.ACCESS_KEY_S3,
    secret_key=settings.SECRET_KEY_S3,
    endpoint_url=settings.ENDPOINT_URL_S3,
    bucket_name=settings.BUCKET_NAME_S3,
)
