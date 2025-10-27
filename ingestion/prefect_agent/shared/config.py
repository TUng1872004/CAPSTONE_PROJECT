from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogConfig(BaseSettings):
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/console)")
    log_file: str = Field("./logs/app.log", description="Log file path (relative to cwd)")
    log_rotation: str = Field(default="100 MB", description="Log rotation size")
    log_retention: str = Field(default="30 days", description="Log retention period")


class ServiceConfig(BaseSettings):
    service_name: str = Field(..., description="Unique service identifier")
    service_version: str = Field(default="1.0.0", description="Service version")
    host: str = Field(default="0.0.0.0", description="Service bind address")
    port: int = Field(..., description="Service port")
    cpu_fallback: bool

    

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


