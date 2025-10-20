import sys
from pathlib import Path
from loguru import logger
from typing import Optional
from .config import LogLevel


class LoggerConfig:
    """Centralized logger configuration and setup"""

    @staticmethod
    def setup(
        service_name: str,
        level: LogLevel = LogLevel.INFO,
        log_format: str = "console",
        log_file: Optional[str] = None,
        rotation: str = "100 MB",
        retention: str = "30 days",
        compression: str = "zip",
        logs_dir: str = "logs",
        **extra_context
    ) -> None:
        """
        Configure loguru logger with standardized settings.

        Args:
            service_name: Service identifier
            level: Minimum log level
            log_format: 'json' or 'console'
            log_file: Explicit log file path (if None, use logs/{service_name}.log)
            rotation: Log rotation policy
            retention: Retention policy
            compression: Compression for rotated logs
            logs_dir: Directory for log files
            **extra_context: Additional context fields
        """
        logger.remove()

        if log_format == "json":
            format_string = LoggerConfig._json_format()
            serialize = True
        else:
            format_string = LoggerConfig._console_format()
            serialize = False

        logger.add(
            sys.stderr,
            format=format_string,
            level=level.value,
            colorize=(log_format == "console"),
            serialize=serialize,
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )

        log_path = Path(log_file) if log_file else Path(logs_dir) / f"{service_name}.log"
        logger.debug(f"{log_path=}")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_path,
            format=format_string,
            level=level.value,
            rotation=rotation,
            retention=retention,
            compression=compression,
            serialize=serialize,
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

        logger.configure(extra={"service_name": service_name, **extra_context})

        logger.info(
            "logger_initialized",
            service=service_name,
            level=level.value,
            format=log_format,
            file=str(log_path),
        )

    @staticmethod
    def _json_format() -> str:
        """Format string for JSON logs"""
        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    @staticmethod
    def _console_format() -> str:
        """Colorized console format"""
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    @staticmethod
    def add_context(**kwargs) -> None:
        """Add extra context to logs"""
        logger.configure(extra=kwargs)

    @staticmethod
    def get_logger():
        """Return the logger instance"""
        return logger


def setup_service_logger(
    service_name, 
    service_version,
    log_level,
    log_format,
    log_file,
    log_rotation,
    log_retention,
    **kwargs
    
) -> None:
    """Initialize logger from service config."""
    LoggerConfig.setup(
        service_name=service_name,
        level=log_level,
        log_format=log_format,
        log_file=log_file,
        rotation=log_rotation,
        retention=log_retention,
        service_version=service_version,
        **kwargs
    )
