
from datetime import datetime
import time
import uuid
from fastapi import  WebSocket, WebSocketDisconnect, APIRouter


router = APIRouter(
    prefix="/chat",
    tags=["WebSock",]
    )


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_message_json(self, message, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    messages = {'1': "Для регистрации выберите пункт меню 'Войти', затем в открывшемся окне пункт 'Зарегистрироваться'",
                '2': "Чтобы забронировать отель, найдите через пункт меню 'Поиск' интересующий отель и номера, добавьте в корзину. Перейдите в корзину, выберите желаемые позиции и нажмите кнопку 'Забронировать'",
                '3': "Вы можете отменить бронирование через пункт меню 'Мои бронирования'",
                '4': "Оценить бронирование можно по окончании дат визита в разделе 'Личный кабинет' во вкладке 'Архив бронирований'"}
    start_message = """Привет, я - демо-бот<br> Я могу сообщить как пользоваться сервисом<br>
    Выберите нужный пункт:<br> 1 - Регистрация в сервисе<br> 2 - Бронирование отеля<br> 3 - Отмена бронирования<br> 4 - Как оценить отель"""
    content = """
            <div class="tw-chat tw-chat-start" style="margin:4px;">
            <div class="tw-chat-header">
            Вы
            <time class="tw-text-xs tw-opacity-50">{time}</time>
            </div>
                <div class="tw-chat-bubble" >{message}</div>
              </div>
            """
    content1 = """
        <div class="tw-chat tw-chat-end" style="margin:4px;">
        <div class="tw-chat-header">
        Консультант
        <time class="tw-text-xs tw-opacity-50">{time}</time>
        </div>
        <div class="tw-chat-bubble" style="background-color:#dbeafe;color:black;"> {message}</div>
        </div>
        
    """
    await manager.connect(websocket)
    await manager.send_personal_message(content1.format(message=start_message, time=datetime.strftime(datetime.now(), "%d.%m %H:%M")), websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_personal_message(content.format( message=data["chat_message"], time=datetime.strftime(datetime.now(), "%d.%m %H:%M")), websocket)
            await manager.send_personal_message(content1.format( message=messages.get(data["chat_message"], "Выберите пункт из предложенных"), time=datetime.strftime(datetime.now(), "%d.%m %H:%M")), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")



