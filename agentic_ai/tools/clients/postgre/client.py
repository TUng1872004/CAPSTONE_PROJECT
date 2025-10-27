from ingestion.core.pipeline.tracker import ArtifactMetadata, ArtifactSchema, ArtifactLineageSchema
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class PostgresClient:
    def __init__(
        self,
        database_url: str
    ):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False, pool_pre_ping=True, poolclass=NullPool) 
    
    def get_session(self) -> AsyncSession:
        sessionmaker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        return sessionmaker()

    async def initialize(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_artifact(self, artifact_id: str) -> ArtifactMetadata | None:
        async with self.get_session() as session:
            result = await session.get(ArtifactSchema, artifact_id)
            if not result:
                return None
            
            return ArtifactMetadata(
                artifact_id=result.artifact_id,
                artifact_type=result.artifact_type,
                minio_url=result.minio_url,
                parent_artifact_id=result.parent_artifact_id or None,
                task_name=result.task_name,
                created_at=result.created_at,
                user_id=result.user_id
            )
        

    



