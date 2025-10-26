from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, String, DateTime, JSON, Text, Index, ForeignKey, select, or_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from core.config.logging import run_logger

Base = declarative_base()


class ArtifactMetadata(BaseModel):
    """
    Pydantic model representing the metadata for an artifact stored in the database.
    This captures essential details about the artifact, its origin, and associated data.
    """
    artifact_id: str = Field(..., description="Unique identifier for the artifact (e.g., SHA-256 hash or UUID).")
    artifact_type: str = Field(..., description="The type of the artifact, such as 'video', 'json', 'image', or 'caption'. Determines the structure and purpose.")
    minio_url: str = Field(..., description="Full S3/Minio URL to the artifact file (e.g., 's3://bucket/path/to/file').")
    parent_artifact_id: str | None = Field(None, description="The ID of the immediate parent artifact from which this one was derived, enabling lineage tracking.")
    task_name: str = Field(..., description="The name of the task or workflow step that produced this artifact (e.g., 'autoshot_processing').")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp when the artifact metadata was created/inserted into the database.")


class ArtifactSchema(Base):
    __tablename__ = "artifacts_application"

    artifact_id: Mapped[str] = mapped_column(String(128), primary_key=True, index=True)
    artifact_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    minio_url: Mapped[str] = mapped_column(Text, nullable=False)
    parent_artifact_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    task_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), index=True)
    
    

class ArtifactLineageSchema(Base):
    """Track artifact lineage relationships"""
    __tablename__ = "artifact_lineage_application"

    id = Column(String(128), primary_key=True, default=lambda: uuid4().hex)
    parent_artifact_id = Column(
        String(128),
        ForeignKey("artifacts_application.artifact_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    child_artifact_id = Column(
        String(128),
        ForeignKey("artifacts_application.artifact_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transformation_type = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    



class ArtifactTracker:
    
    """
    Manages artifact metadata persistence and retrieval
    """

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
        run_logger.info("Artifact tracker initialized")
    
    async def save_artifact(self, metadata: ArtifactMetadata) -> str:
        async with self.get_session() as session:
            artifact = ArtifactSchema(
                artifact_id=metadata.artifact_id,
                artifact_type=metadata.artifact_type,
                minio_url=metadata.minio_url,
                parent_artifact_id=metadata.parent_artifact_id,
                task_name=metadata.task_name,
                created_at=metadata.created_at,
            )
            session.add(artifact)
            await session.flush()

            if metadata.parent_artifact_id:
                lineage = ArtifactLineageSchema(
                    parent_artifact_id=metadata.parent_artifact_id,
                    child_artifact_id=metadata.artifact_id,
                    transformation_type=metadata.task_name,
                )
                session.add(lineage)
            
            await session.commit()
            run_logger.info(f"Saved artifact {metadata.artifact_id}")
        
            return metadata.artifact_id

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
            )
    


    
    
    async def close(self) -> None:
        await self.engine.dispose()