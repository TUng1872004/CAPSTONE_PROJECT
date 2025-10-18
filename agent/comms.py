from typing import List, Optional
from pydantic import BaseModel, Field

class ReBody(BaseModel):
    image_url: Optional[str] = Field(..., description="URL of the image to be processed.")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data.")

    
class Request(BaseModel):
    user_id: str
    session_id: str
    query: str
    image: Optional[ReBody] = None
    filter: Optional[dict] = None

class Response(BaseModel):
    response: str
    error: Optional[dict] = None