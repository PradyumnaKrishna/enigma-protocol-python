from typing import List, Optional

from fastapi.websockets import WebSocket


class Chat:
    user: str
    connection: Optional[WebSocket]
    messages: List[dict]

    def __init__(self, user, connection):
        self.user = user
        self.connection = connection
        self.messages = []

    async def send_message(self, message: dict):
        if self.connection:
            await self.connection.send_json(message)

    async def send_pending_messages(self):
        for message in self.messages:
            await self.send_message(message)
        self.messages = []

    def is_alive(self) -> bool:
        if self.connection:
            return True
        return False
