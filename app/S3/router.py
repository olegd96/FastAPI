from fastapi import APIRouter
from app.S3.s3client import s3_client


router = APIRouter(
    prefix="/S3",
    tags=["S3 хранилище"],
)


@router.get("/s3post")
async def s3_upload():
    await s3_client.upload_file("app/static/images/6.jpg")
