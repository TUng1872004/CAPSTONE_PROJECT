"""Backward compatibility wrapper for legacy imports."""

from service_asr.core.config import ASRServiceConfig as Config, asr_service_config

config = asr_service_config

__all__ = ["Config", "config", "asr_service_config"]
