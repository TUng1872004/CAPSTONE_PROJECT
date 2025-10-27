from pydantic import Field

from shared.config import ServiceConfig, LogLevel


class LLMServiceConfig(ServiceConfig):
    """Runtime configuration for the LLM service."""

    # Gemini API settings
    gemini_api_key: str | None = Field(
        default=None,
        description="API key for Google Gemini (set to enable the Gemini client handler)",
    )
    gemini_model_name: str = Field(
        default="gemini-flash-lite-latest",
        description="Gemini multimodal model identifier",
    )

    # OpenRouter API settings
    openrouter_api_key: str | None = Field(
        default=None,
        description="API key for OpenRouter (set to enable the OpenRouter handler)",
    )
    openrouter_model_name: str = Field(
        default="meta-llama/llama-3.1-405b-instruct",
        description="Default OpenRouter model identifier",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1/chat/completions",
        description="Endpoint for OpenRouter chat completions",
    )
    openrouter_referer: str | None = Field(
        default=None,
        description="Optional HTTP referer header required by OpenRouter policies",
    )
    openrouter_title: str | None = Field(
        default="Capstone LLM Service",
        description="X-Title header sent to OpenRouter",
    )

    log_level: LogLevel = Field(default=LogLevel.DEBUG)
    log_format: str = Field(default="console")
    log_retention: str = Field(default="30 days")
    log_file: str = Field(default="./logs/app.log")
    log_rotation: str = Field(default="100 MB")



llm_service_config = LLMServiceConfig()  # type: ignore[arg-type]
