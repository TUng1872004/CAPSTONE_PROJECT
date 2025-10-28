from ingestion.core.pipeline.tracker import ArtifactMetadata, ArtifactSchema, ArtifactLineageSchema
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base
from sqlalchemy import select


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

    

    async def get_children_artifact(
        self,
        artifact_id:str,
        filter_artifact_type: list[str] | None = None
    ) -> list[ArtifactMetadata]:
        """
        Return all the children of an artifact, with artifact type filtering
        """
        async with self.get_session() as session:
            visited: set[str] = set()
            results: list[ArtifactMetadata] = []
            async def fetch_children_recursive(
                current_id:str
            ):
                if current_id in visited:
                    return
                visited.add(current_id)
                lineage_query = select(
                    ArtifactLineageSchema.child_artifact_id
                ).where(
                    ArtifactLineageSchema.parent_artifact_id==current_id
                )
                lineage_result = await session.execute(lineage_query)
                child_ids = [
                    row[0] for row in lineage_result
                ]
                if not child_ids:
                    return
                
                artifact_query = select(ArtifactSchema).where(
                    ArtifactSchema.artifact_id.in_(child_ids)
                )

                if filter_artifact_type:
                    artifact_query = artifact_query.where(
                        ArtifactSchema.artifact_type.in_(filter_artifact_type)
                    )

                artifact_result = await session.execute(artifact_query)
                artifacts = artifact_result.scalars().all()

                for a in artifacts:
                    results.append(
                        ArtifactMetadata(
                            artifact_id=a.artifact_id,
                            artifact_type=a.artifact_type,
                            minio_url=a.minio_url,
                            parent_artifact_id=a.parent_artifact_id,
                            task_name=a.task_name,
                            created_at=a.created_at,
                            user_id=a.user_id,
                        )
                    )

                for a in artifacts:
                    await fetch_children_recursive(a.artifact_id)
            
            await fetch_children_recursive(current_id=artifact_id)
            return results

        

    



