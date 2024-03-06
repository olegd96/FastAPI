
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

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    messages = {'1': "Для регистрации выберите пункт меню 'Войти', затем в открывшемся окне пункт 'Зарегистрироваться'",
                '2': "Чтобы забронировать отель, найдите через пункт меню 'Поиск' интересующий отель и номера, добавьте в корзину. Перейдите в корзину, выберите желаемые позиции и нажмите кнопку 'Забронировать'",
                '3': "Вы можете отменить бронирование через пункт меню 'Мои бронирования'"}
    start_message = """Привет, я - демо-бот\r\n Я могу сообщить как пользоваться сервисом\r\n 
    Выбери нужный пункт:\r\n 1 - Регистрация в сервисе\n 2 - Бронирование отеля\r\n 3 - Отмена бронирования"""
    await manager.connect(websocket)
    await manager.send_personal_message(start_message, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(data, websocket)
            answer = messages.get(data, 'Выберите пункт из предложенных')
            await manager.send_personal_message(answer, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")