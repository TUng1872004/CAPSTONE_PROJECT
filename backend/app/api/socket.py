from email.mime import image
from beanie import PydanticObjectId
from fastapi import HTTPException
from fastapi.security import HTTPBearer
import jwt
import socketio

from app.schema.user import ALGORITHM, SECRET_KEY

sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins="*", logger=True, engineio_logger=True
)


import asyncio
from app.core.lifespan import app_state
from app.model.session_message import ImageBlock, SessionMessage, TextBlock, VideoBlock
from llama_index.core.base.llms.types import MessageRole


security = HTTPBearer(auto_error=False)


def optional_verify_token(credentials=security):
    if credentials is None:  # no token provided
        return None
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.InvalidTokenError:
        # You could either return None (treat as guest) or reject
        raise HTTPException(status_code=401, detail="Invalid token")


@sio.on("stream_chat")
async def handle_stream_chat(socket_id, data: dict):
    try:
        # socket_id is the socket id to chat
        # session id is the chat bot session id
        session_id = data.get("sessionId", None)
        user_id = data.get("userId")  # could be None for guest
        message = data.get("text")

        user_message = SessionMessage(
            session_id=None,
            role=MessageRole.USER,
            blocks=[
                TextBlock(text_content=message),
            ],
        )

        session_id = await app_state.chat_service.add_message(
            session_id, user_id, user_message
        )

        # tell client message received
        await sio.emit(
            "message_received",
            {
                "role": "user",
                "content": message,
                # "timestamp": user_message.timestamp.isoformat(),
                "session_id": session_id,
            },
            to=socket_id,
        )

        await sio.emit("stream_thinking", {"status": "AI is thinking..."}, to=socket_id)
        await asyncio.sleep(1)  # simulate delay for thinking
        await sio.emit(
            "stream_thinking", {"status": "AI is getting images..."}, to=socket_id
        )
        await asyncio.sleep(1)  # simulate delay for getting images

        # then response
        # stream response
        full_response = ""
        async for chunk in app_state.agent.stream_chat("message"):
            if chunk:
                full_response += chunk
                await sio.emit(
                    "stream_chunk",
                    {
                        "chunk": chunk,
                        "msg_type": "text",
                        "role": MessageRole.ASSISTANT.value,
                    },  # assistant
                    to=socket_id,
                )
                await asyncio.sleep(0.05)

        # stream videos reponse
        await sio.emit(
            "stream_chunk",
            {
                "chunk": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                "msg_type": "video",
                "role": MessageRole.ASSISTANT.value,
            },
            to=socket_id,
        )
        await sio.emit(
            "stream_chunk",
            {
                "chunk": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                "msg_type": "video",
                "role": MessageRole.ASSISTANT.value,
            },
            to=socket_id,
        )
        await asyncio.sleep(1)
        # stream images reponse
        await sio.emit(
            "stream_chunk",
            {
                "chunk": "Images I found for you:",
                "msg_type": "text",
                "role": MessageRole.ASSISTANT.value,
            },  # assistant
            to=socket_id,
        )

        await sio.emit(
            "stream_chunk",
            {
                "chunk": ["https://example.com/image1.jpg"],
                "msg_type": "image",
                "role": MessageRole.ASSISTANT.value,
            },
            to=socket_id,
        )
        await sio.emit(
            "stream_chunk",
            {
                "chunk": ["https://example.com/image2.jpg", "https://example.com/image3.jpg"],
                "msg_type": "image",
                "role": MessageRole.ASSISTANT.value,
            },
            to=socket_id,
        )
        await asyncio.sleep(0.5)

        # save message
        ai_message = SessionMessage(
            session_id=PydanticObjectId(session_id),
            role=MessageRole.ASSISTANT,
            blocks=[
                TextBlock(text_content=full_response),
                # list lấy từ stream ra
                VideoBlock(video_urls=["1.mp4", "2.mp4"]),
                TextBlock(text_content="Images I found for you:"),
                ImageBlock(image_urls=["1.jpg", "2.jpg", "3.jpg"]),
            ],
        )
        await app_state.chat_service.add_message(session_id, "ai", ai_message)

        # notify finish
        await sio.emit(
            "stream_end", {"timestamp": ai_message.timestamp.isoformat()}, to=socket_id
        )

    except Exception as e:
        await sio.emit("error", {"message": str(e)}, to=socket_id)
