from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from service_asr.core.dependencies import get_service
from service_asr.core.schema import ASRInferenceRequest, ASRInferenceResponse
from shared.schema import LoadModelRequest, ModelInfo, UnloadModelRequest

router = APIRouter()


@router.post("/load", response_model=ModelInfo)
async def load_model(request: LoadModelRequest, service=Depends(get_service)) -> ModelInfo:
    try:
        return await service.load_model(
            model_name=request.model_name,
            device=request.device,
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("asr_model_load_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/unload")
async def unload_model(request: UnloadModelRequest, service=Depends(get_service)) -> dict[str, str]:
    try:
        await service.unload_model(cleanup_memory=request.cleanup_memory)
        return {"status": "success", "message": "model unloaded"}
    except Exception as exc:  # pragma: no cover
        logger.exception("asr_model_unload_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/infer", response_model=ASRInferenceResponse)
async def infer(request: ASRInferenceRequest, service=Depends(get_service)) -> ASRInferenceResponse:
    if service.loaded_model is None:
        raise HTTPException(status_code=400, detail="No model loaded. Load a model before inference.")

    try:
        return await service.infer(request)
    except Exception as exc:  # pragma: no cover
        logger.exception("asr_inference_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/models")
async def models(service=Depends(get_service)) -> dict[str, object]:
    loaded = service.loaded_model_info.model_dump(mode="json") if service.loaded_model_info else None
    return {
        "available_models": service.get_available_models(),
        "loaded_model": loaded,
    }


@router.get("/status")
async def status(service=Depends(get_service)) -> dict[str, object]:
    return service.get_system_status()
