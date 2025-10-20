from functools import lru_cache
import asyncio
from typing import Callable, Type
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
from loguru import logger
import torch


def retry_with_backoff(
    max_attemps:int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    exponential_base: int = 2
):
    return retry(
        stop=stop_after_attempt(max_attemps),
        wait = wait_exponential(
            multiplier=min_wait,
            max=max_wait,
            exp_base=exponential_base
        ),
        before_sleep=before_sleep_log(logger, "WARNING"), #type:ignore
        after=after_log(logger, "INFO"),#type:ignore
        reraise=True,
    )



def retry_external_api(
    max_attempts: int = 3,
    min_wait: float = 2.0,
    max_wait: float = 30.0,
):
    """
    Decorator for external API calls with longer backoff.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=min_wait,
            max=max_wait,
            exp_base=2
        ),
        before_sleep=before_sleep_log(logger, "WARNING"),#type:ignore
        reraise=True,
    )

