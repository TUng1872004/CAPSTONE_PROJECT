# LLM Service

Serve multimodal large language models (LLMs) via a unified API. The service supports both local Hugging Face models (Moondream2) and hosted APIs (Gemini).

## Features
- Shared `BaseService` integration for logging, metrics, lifecycle, and model management
- Dynamic loading/unloading of Gemini API clients, OpenRouter API clients
- Multimodal inference: prompt + optional list of image paths → textual answer
- Health and Prometheus metrics endpoints for observability

## Endpoints
| Method | Path | Description |
| --- | --- | --- |
| POST | `/llm/load` | Load/configure an LLM handler (Gemini API client or Moondream2 checkpoint) |
| POST | `/llm/unload` | Unload the currently active handler |
| POST | `/llm/infer` | Run inference with `prompt` and `image_paths` |
| GET | `/llm/models` | List available models and show which one is loaded |
| GET | `/llm/status` | Retrieve system metrics and model metadata |
| GET | `/metrics` | Prometheus scrape endpoint |
| GET | `/health` | Health check |

## Configuration
The service reads settings from environment variables through `LLMServiceConfig`:
- `SERVICE_NAME`, `SERVICE_VERSION`, `PORT`, `CPU_FALLBACK`
- `GEMINI_API_KEY` (set to enable the Gemini API handler)
- `GEMINI_MODEL_NAME` (defaults to `gemini-1.5-flash`)
- `OPENROUTER_API_KEY` (set to enable the OpenRouter handler)
- `OPENROUTER_MODEL_NAME`, `OPENROUTER_BASE_URL`, `OPENROUTER_REFERER`, `OPENROUTER_TITLE`
- `MOONDREAM2_CHECKPOINT` (path or HF repo for the local checkpoint)
- `MAX_NEW_TOKENS`, `TEMPERATURE` (generation controls used by handlers)

Only handlers with valid configuration are exposed via `/llm/models`.

## Running locally
```bash
uvicorn service_llm.main:app --host 0.0.0.0 --port 8010
```

Additional requirements:
- Gemini API handler: install `google-generativeai` (`pip install google-generativeai`) and set `GEMINI_API_KEY`.
- Moondream2 local handler: install `transformers`, `torch`, and ensure the checkpoint (with processor + model) is available.
