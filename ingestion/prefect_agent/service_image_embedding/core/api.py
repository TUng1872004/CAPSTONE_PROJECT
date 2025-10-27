from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from service_image_embedding.core.dependencies import get_service
from service_image_embedding.schema import ImageEmbeddingRequest, ImageEmbeddingResponse
from shared.schema import LoadModelRequest, ModelInfo, UnloadModelRequest

router = APIRouter()


@router.post("/load", response_model=ModelInfo)
async def load_model(request: LoadModelRequest, service=Depends(get_service)) -> ModelInfo:
    try:
        return await service.load_model(
            model_name=request.model_name,
            device=request.device,
        )
    except Exception as exc:  
        logger.exception("image_embedding_model_load_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/unload")
async def unload_model(request: UnloadModelRequest, service=Depends(get_service)) -> dict[str, str]:
    try:
        await service.unload_model(cleanup_memory=request.cleanup_memory)
        return {"status": "success", "message": "model unloaded"}
    except Exception as exc:  
        logger.exception("image_embedding_model_unload_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/infer", response_model=ImageEmbeddingResponse)
async def infer(request: ImageEmbeddingRequest, service=Depends(get_service)) -> ImageEmbeddingResponse:
    if service.loaded_model is None:
        raise HTTPException(status_code=400, detail="No model loaded. Load a model before inference.")

    try:
        return await service.infer(request)
    except Exception as exc:  
        logger.exception("image_embedding_inference_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/models")
async def list_models(service=Depends(get_service)) -> dict[str, object]:
    """List registered image embedding models and the currently loaded one."""
    loaded_info = service.loaded_model_info.model_dump(mode="json") if service.loaded_model_info else None
    return {
        "available_models": service.get_available_models(),
        "loaded_model": loaded_info,
    }


@router.get("/status")
async def status(service=Depends(get_service)) -> dict[str, object]:
    """Expose resource usage and model load status."""
    return service.get_system_status()
