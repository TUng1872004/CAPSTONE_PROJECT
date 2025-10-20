from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from loguru import logger
from prefect.logging import get_run_logger

class LogLevel(str):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"



class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='RUN_LOG_',
        case_sensitive=True,
        extra='ignore'
    )
    log_level: str = Field(LogLevel.DEBUG)
    log_format: str = Field("console",)
    log_retention: str = Field("30 days",)
    log_file: str = Field("./logs/app.log",)
    log_rotation: str = Field("100 MB",)



logger_config = LoggingConfig() #type:ignore


def configure_logging(config: LoggingConfig):
    logger.remove()
    logger.add(
        config.log_file,
        level=config.log_level,
        rotation=config.log_rotation,
        retention=config.log_retention,
        enqueue=True,
    )
    return logger

run_logger = configure_logging(logger_config)