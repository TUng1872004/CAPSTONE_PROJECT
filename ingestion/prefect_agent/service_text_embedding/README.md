# Text Embedding Service

FastAPI microservice that serves text embeddings using SentenceTransformer or mmBERT backends.

## Features
- Shared `BaseService` integration for logging, metrics, and model lifecycle management
- Dynamic model loading/unloading via the registry
- Health and Prometheus metrics endpoints
- REST API for inference and service introspection under `/text-embedding`

## Endpoints
| Method | Path | Description |
| --- | --- | --- |
| POST | `/text-embedding/load` | Load a configured text embedding model onto the requested device |
| POST | `/text-embedding/unload` | Unload the currently loaded model |
| POST | `/text-embedding/infer` | Generate embeddings for one or more texts |
| GET | `/text-embedding/models` | List available models and show the loaded one |
| GET | `/text-embedding/status` | Show system status and model information |
| GET | `/metrics` | Prometheus metrics |
| GET | `/health` | Service heartbeat |

## Configuration
The service reads environment variables via `TextEmbeddingConfig`. Notable fields:
- `SERVICE_NAME`
- `SERVICE_VERSION`
- `PORT`
- `CPU_FALLBACK`
- `SENTENCE_TRANSFORMER_MODEL`
- `SENTENCE_TRANSFORMER_BATCH_SIZE`
- `MMBERT_MODEL_NAME`
- `MMBERT_MAX_LENGTH`
- `MMBERT_BATCH_SIZE`

Only models with non-empty configuration values are exposed through the API.

## Running locally
```bash
uvicorn service_text_embedding.main:app --host 0.0.0.0 --port 8003
```

Ensure that Hugging Face checkpoints referenced in the configuration are accessible from the runtime environment.
