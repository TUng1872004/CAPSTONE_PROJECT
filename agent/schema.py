from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class Tool(str, Enum):
    OBJECT_DETECTOR = "object_detector"
    IMAGE_SEARCH = "image_search"
    VIDEO_SUMMARIZER = "video_summary"
    TEXT_ANALYZER = "text_analyzer"

class ReturnedItem(BaseModel):
    key: Optional[str] = Field(None, description="Key of the returned data.")
    value: Optional[str] = Field(None, description="Value of the returned data.")
    
class Result(BaseModel):
    answer: Optional[str] = Field(None, description="Main textual answer.")
    returned: Optional[List[ReturnedItem]] = Field(None, description="Structured output data.")
    
class Task(BaseModel):
    tool: Tool
    mission: str
    reasoning: str
    result: Optional[Result] = None
    
class Plan(BaseModel):
    query: str
    tasks: List[Task]
    

