import aiofiles
from fastapi import APIRouter, UploadFile
import shutil

from app.tasks.tasks import process_pic



router = APIRouter(
    prefix="/images",
    tags=["Загрузка изображений"]
)


@router.post("/hotels")
async def add_hotel_images(name: int, file: UploadFile):
    im_path = f"static/images/{name}.webp"
    with open(im_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    process_pic.delay(im_path)

    
