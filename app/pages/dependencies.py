from fastapi import Request

from app.exceptions import RequestAttorneyException


async def check_valid_request(request: Request):
    if not request.headers.get("myHeader", None):
        raise RequestAttorneyException
