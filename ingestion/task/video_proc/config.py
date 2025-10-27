from pydantic import BaseModel

class VideoIngestionSettings(BaseModel):
    retries: int
    retry_delay_seconds: int | list[float]
    timeout_seconds: int