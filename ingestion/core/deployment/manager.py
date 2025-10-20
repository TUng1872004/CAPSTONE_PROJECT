from typing import Any
from pathlib import Path
from uuid import uuid4
from uuid import UUID
from prefect import get_client
from prefect.deployments import run_deployment
from prefect import State
from prefect.client.schemas.objects import StateType
from loguru import logger
from pydantic import BaseModel, Field


class DeploymentConfig(BaseModel):
    name: str = Field(..., description="Deployment name")
    flow_name: str = Field(..., description="Flow function name")
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    version: str | None = None
    work_pool_name: str | None = None
    work_queue_name: str | None = None



class FlowRunRequest(BaseModel):
    video_files: list[str] = Field(..., description="List of video file paths or URLs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FlowRunInfo(BaseModel):
    """Information about a flow run."""
    run_id: str
    flow_id: str
    flow_name: str
    deployment_id: str | None
    state_type: str
    state_name: str
    created_at: str
    updated_at: str
    parameters: dict[str, Any]


class DeploymentManager:
    
    def __init__(self, deployment_name: str = "video-processing-deployment"):
        self.deployment_name = deployment_name
    
    async def create_flow_run(
        self,
        video_files: list[str],
        metadata: dict[str, Any] | None = None
    ) -> FlowRunInfo:
        """
        Create a new flow run for video processing.
        
        Args:
            video_files: List of video file identifiers
            metadata: Optional metadata for the run
            
        Returns:
            FlowRunInfo with run details
        """
        run_id = str(uuid4())
        
        parameters = {
            "video_files": video_files,
            "run_id": run_id,
            "metadata": metadata or {}
        }
        
        try:
            flow_run = await run_deployment( #type:ignore
                name=self.deployment_name,
                parameters=parameters,
                timeout=0,  
                as_subflow=False
            )
            
            logger.info(
                f"Created flow run: {flow_run.id}",
                deployment=self.deployment_name,
                run_id=run_id
            )
            
            return FlowRunInfo(
                run_id=str(flow_run.id),
                flow_id=str(flow_run.flow_id),
                flow_name=flow_run.name or "unknown",
                deployment_id=str(flow_run.deployment_id) if flow_run.deployment_id else None,
                state_type=flow_run.state_type.value if flow_run.state_type else "UNKNOWN",
                state_name=flow_run.state_name or "unknown",
                created_at=flow_run.created.isoformat() if flow_run.created else "",
                updated_at=flow_run.updated.isoformat() if flow_run.updated else "",
                parameters=parameters
            )
            
        except Exception as e:
            logger.exception(f"Failed to create flow run: {e}")
            raise
    
    async def get_flow_run_status(self, run_id: UUID) -> FlowRunInfo | None:
        async with get_client() as client:
            try:
                flow_run = await client.read_flow_run(run_id)
                
                return FlowRunInfo(
                    run_id=str(flow_run.id),
                    flow_id=str(flow_run.flow_id),
                    flow_name=flow_run.name or "unknown",
                    deployment_id=str(flow_run.deployment_id) if flow_run.deployment_id else None,
                    state_type=flow_run.state_type.value if flow_run.state_type else "UNKNOWN",
                    state_name=flow_run.state_name or "unknown",
                    created_at=flow_run.created.isoformat() if flow_run.created else "",
                    updated_at=flow_run.updated.isoformat() if flow_run.updated else "",
                    parameters=flow_run.parameters or {}
                )
            except Exception as e:
                logger.error(f"Failed to get flow run {run_id}: {e}")
                return None
    
    async def cancel_flow_run(self, run_id: str) -> bool:
        async with get_client() as client:
            try:
                await client.set_flow_run_state(
                    flow_run_id=run_id,
                    state=State(type=StateType.CANCELLED, name="Cancelled")
                )
                logger.info(f"Cancelled flow run: {run_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to cancel flow run {run_id}: {e}")
                return False
            

    
