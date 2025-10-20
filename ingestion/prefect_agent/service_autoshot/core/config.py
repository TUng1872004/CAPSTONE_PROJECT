from shared.config import ServiceConfig, LogLevel
from dotenv import load_dotenv
from typing import Optional
from pydantic import Field

load_dotenv() 

class AutoshotConfig(ServiceConfig):
    autoshot_model_path: str
    log_level: LogLevel = Field(LogLevel.INFO)
    log_format: str = Field("console",)
    log_retention: str = Field("30 days",)
    log_file: str = Field("./logs/app.log",)
    log_rotation: str = Field("100 MB",)


autoshot_config = AutoshotConfig() #type:ignore
