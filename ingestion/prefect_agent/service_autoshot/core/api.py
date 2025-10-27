from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from service_autoshot.schema import AutoShotRequest, AutoShotResponse
from service_autoshot.core.dependency import get_service
from shared.schema import LoadModelRequest, UnloadModelRequest, ModelInfo

router = APIRouter()

@router.post(
    '/load', response_model=ModelInfo
)
async def load_model(
    request: LoadModelRequest, service=Depends(get_service)
):
    try:
        model_info = await service.load_model(
            model_name=request.model_name,
            device=request.device
        )
        return model_info
    except Exception as e:
        logger.exception("Failed to load the model", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    '/unload'
)
async def unload_model(request: UnloadModelRequest, service=Depends(get_service)):
    try:
        await service.unload_model(cleanup_memory=request.cleanup_memory)
        return {"status": "success", "message": "Model unloaded"}
    except Exception as e:
        logger.exception("Failed to unload model", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/infer', response_model=AutoShotResponse)
async def infer(request: AutoShotRequest, service=Depends(get_service)):
    if service.loaded_model is None:
        raise HTTPException(
            status_code=400,
            detail="No model loaded. Please load a model first."
        )
    
    try:
        result = await service.infer(request)
        return result
    except Exception as e:
        logger.exception("Inference failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/models")
async def list_models(service=Depends(get_service)):
    """List available models"""
    return {
        "available_models": service.get_available_models(),
        "loaded_model": service.loaded_model_info.model_dump() if service.loaded_model_info else None
    }

@router.get("/status")
async def get_status(service=Depends(get_service)):
    """Get service status"""
    return service.get_system_status()