

import json
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, Response


router = APIRouter(
    prefix='/session',
    tags=["Сессия"],
)

@router.get("/a")
async def a(request: Request, response: Response):
    if not request.cookies.get("cart"):
        ident = str(uuid.uuid4())
        response.set_cookie("cart", ident, httponly=True)


@router.get("/b")
async def b(request: Request) -> PlainTextResponse:

    my_var = request.cookies.get("cart", None)
    
    return PlainTextResponse(my_var)