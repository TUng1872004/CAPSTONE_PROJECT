from contextlib import asynccontextmanager
from fastapi import FastAPI
from beanie import init_beanie
from minio import Minio

from motor.motor_asyncio import AsyncIOMotorClient
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import MockLLM

from app.core.config import settings
from app.model.chat_history import ChatHistory
from app.service.agent import Agent
from app.service.chat import ChatService
from app.model.user import User
from app.service.user import UserService
from app.service.minio import Minio as MinioService
from app.model.group import Group
from app.model.session_video import SessionVideo
from app.model.video import Video
from app.model.session_message import SessionMessage

class AppState:
    """Global application state"""
    def __init__(self):
        self.mongo_client: AsyncIOMotorClient  = None # type: ignore

        self.agent: Agent = None # type: ignore
        self.chat_service: ChatService = None # type: ignore
        self.user_service: UserService = None # type: ignore
        # self.minio_service: MinioService = None # type: ignore


app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up application...")
    app_state.mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    database = app_state.mongo_client[settings.MONGO_DB]
    await init_beanie(database=database, document_models=[ChatHistory, User, Group, Video, SessionVideo, SessionMessage])  # type: ignore
    print("✓ MongoDB and Beanie initialized")

    minio_client = Minio(
        endpoint=settings.MINIO_PUBLIC_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )
    bucket_name = "avatars"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    minio_service = MinioService(minio_client)

    print("✓ MinIO initialDized")

    llm = MockLLM(max_tokens=2)
    app_state.agent = Agent(llm=llm)
    app_state.chat_service = ChatService()
    app_state.user_service = UserService(minio_service)
    print("✓ Services initialized")

    yield

    print("Shutting down application...")
    if app_state.mongo_client:
        app_state.mongo_client.close()
    print("✓ Application shutdown complete")
