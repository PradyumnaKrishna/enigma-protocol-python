"""
Main module for the server.
"""

from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect

from . import __version__
from .chat import Chat
from .database import DataBase
from .exceptions import UserNotExists
from .models import ConnectResponse, LoginResponse, TransmissionData, VersionResponse

app = FastAPI(title="Enigma Procotol Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DataBase(file="users.db", table="users")

# store all active chats
# TODO: memory storage, look for better alternatives
chats: Dict[str, Chat] = {}


@app.get("/")
def home():
    """main homepage"""
    return {"status": "ok"}


@app.get("/login/{public_key}")
def login(public_key: str) -> LoginResponse:
    """
    create user and store public_key
    :param: public_key
    :return: user
    """
    identity = db.save_user(public_key)
    return LoginResponse(user=identity)


@app.get("/connect/{identity}")
def connect(identity: str) -> ConnectResponse:
    """
    connect to other user
    :param: identity
    :return: status, publicKey
    """
    public_key = db.get_public_key(identity)
    if public_key:
        return ConnectResponse(user=identity, publicKey=public_key)
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/version")
def version() -> VersionResponse:
    return VersionResponse(version=__version__)


@app.websocket("/connect/{identity}")
async def websocket_endpoint(websocket: WebSocket, identity: str):
    """
    Chat server connection for messages.
    """
    try:
        await websocket.accept()

        # Check if user exists, if not raise an exception.
        if not db.is_exist(identity):
            raise UserNotExists

        # Load chat from the chats storage.
        if identity not in chats:
            chat = Chat(user=identity, connection=websocket)
            chats[identity] = chat
        else:
            chat = chats[identity]
            chat.connection = websocket

        # Send all pending messages to the user.
        await chat.send_pending_messages()

        # Listen for incoming messages.
        while True:
            try:
                data = TransmissionData.model_validate(await websocket.receive_json())
            except ValueError:
                await websocket.send_json({"error": "Invalid data"})
                continue

            user = data.to
            if not db.is_exist(user):
                await websocket.send_json({"error": "User not found"})
                continue

            # Send message to the user.
            if user in chats:
                chat = chats[user]
                if chat.is_alive():
                    await chat.send_message(data.model_dump())
                else:
                    chat.messages.append(data.model_dump())
            else:
                chats[user] = Chat(user=user, connection=None)
                chats[user].messages.append(data.model_dump())

    except WebSocketDisconnect:
        # Cloase the connection from chat.
        chats[identity].connection = None
    except UserNotExists:
        await websocket.send_json({"error": "User not found"})
        await websocket.close(reason="User not found")
