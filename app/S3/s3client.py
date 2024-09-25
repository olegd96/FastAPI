from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from app.config import settings
from PIL import Image

class S3client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ) -> None:
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

    async def upload_file(
            self,
            file_path: str,
    ):
        object_name = file_path.split("/")[-1]
        async with self.get_client() as client:
            with open(file_path, "rb") as file:
                await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file,
            )
                
    async def download_file(
            self,
            object_name: str,
    ):
        file_path = f"./booking/app/static/images/{object_name}"
        async with self.get_client() as client:
            response = await client.get_object(
            Bucket=self.bucket_name,
            Key=object_name,
            )
            data = await response['Body'].read()
        with open(file_path, "wb") as file:
            file.write(data)
        im = Image.open(file_path)
        
  

s3_client = S3client(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    endpoint_url=settings.S3_URL,
    bucket_name=settings.S3_BUCKET_NAME,
)  