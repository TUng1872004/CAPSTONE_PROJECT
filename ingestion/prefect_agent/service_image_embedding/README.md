# Image Embedding Service

FastAPI microservice that exposes a unified interface for generating image embeddings. The service follows the shared Prefect agent architecture and relies on the shared registry, configuration, logging, and monitoring utilities.

## Features
- Dynamic model loading/unloading via the shared `BaseService`
- GPU/CPU metrics exposure through the `/metrics` endpoint
- Health check at `/health`
- REST API for inference, model management, and status queries under `/image-embedding`

## Endpoints
| Method | Path | Description |
| --- | --- | --- |
| POST | `/image-embedding/load` | Load a configured embedding model onto the requested device |
| POST | `/image-embedding/unload` | Unload the currently loaded model |
| POST | `/image-embedding/infer` | Generate embeddings for one or more images |
| GET | `/image-embedding/models` | List available models and show the loaded one |
| GET | `/image-embedding/status` | Show system status and model information |
| GET | `/metrics` | Prometheus metrics |
| GET | `/health` | Service heartbeat |

## Configuration
The service reads its configuration from environment variables via `ImageEmbeddingConfig`. Required fields:
- `SERVICE_NAME`
- `SERVICE_VERSION`
- `PORT`
- `CPU_FALLBACK`
- `BEIT3_MODEL_CHECKPOINT`
- `BEIT3_TOKENIZER_CHECKPOINT`
- `OPEN_CLIP_MODEL_NAME`
- `OPEN_CLIP_PRETRAINED`

Optional logging settings are inherited from `LogConfig`.

## Running locally
```bash
uvicorn service_image_embedding.main:app --host 0.0.0.0 --port 8000
```

Ensure the checkpoints declared in the config are reachable from the runtime environment before loading their corresponding models.
