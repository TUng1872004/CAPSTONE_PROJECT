from pydantic import BaseModel
from typing import Literal, Optional

class ModelInfo(BaseModel):
    """Standard model information"""
    model_name: str
    model_type: str  

class LoadModelRequest(BaseModel):
    """Request to load a model"""
    model_name: str
    device: Literal["cpu", "cuda"] = "cuda"

class UnloadModelRequest(BaseModel):
    cleanup_memory: bool = True
