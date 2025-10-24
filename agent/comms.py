from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

class Img(BaseModel):
    image_url: Optional[str] = Field(None, description="URL of the image to be processed.")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data.")
    image_type: str

class Filter(BaseModel):
    video_url: Optional[List[str]] = []
    timestamp: Optional[Tuple]

    
class Request(BaseModel):
    user_id: str
    session_id: str
    query: str
    image: Optional[Img] = None
    filter: Optional[Filter] = None

class Response(BaseModel):
    response: str
    error: Optional[dict] = None
    image: Optional[Img] = None

