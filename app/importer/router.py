import codecs
import csv
from app.exceptions import CannotProcessCSV, CannotAddDataToDatabase
from app.importer.utils import convert_csv_to_postgres_format, TABLE_MODEL_MAP

from app.dao.base import BaseDAO
from fastapi import APIRouter, Depends, UploadFile
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter (
    prefix="/import",
    tags=["Импорт данных"],
)

@router.post("/{table_name}", status_code=201)
async def add_db_data(table_name: str,
                      file: UploadFile,
                      user: Users = Depends(get_current_user)):
    ModelDAO = TABLE_MODEL_MAP[table_name]
    table_data = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'), delimiter=";")
    table_data = convert_csv_to_postgres_format(table_data)
    file.file.close()
    if not table_data:
        raise CannotProcessCSV
    added_data = await ModelDAO.add_bulk(table_data)
    if not added_data:
        raise CannotAddDataToDatabase