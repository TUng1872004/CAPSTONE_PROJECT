
from fastapi import APIRouter, UploadFile, File
from app.core.config import settings
import shutil
import os

router = APIRouter(prefix="/api/uploads", tags=["upload"])



async def process_video(path: str, filename: str):
    # redis_client.publish("status", f"Processing {filename}")
    # Dummy metadata extraction (simulate frame tags)
    frames = [f"dog at frame {i}" for i in range(3)]


    
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # redis_client.publish("status", f"Uploaded {file.filename}")

    # Simulate frame extraction + Mongo insert
    await process_video(file_path, file.filename)

    return {
        "status": "uploaded",
        "url": f"http://localhost:8010/uploads/{file.filename}",
    }