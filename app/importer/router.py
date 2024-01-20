import csv
import shutil

from app.dao.base import BaseDAO
from fastapi import APIRouter, UploadFile
from app.tasks.tasks import process_table_data

router = APIRouter (
    prefix="/import",
    tags=["Импорт данных"],
)

@router.post("/{table_name}")
async def add_db_data(table_name: str,
                      file: UploadFile):
    im_path = f"app/static/datas/{file.filename}"
    with open(im_path, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    await process_table_data(table_name, im_path)