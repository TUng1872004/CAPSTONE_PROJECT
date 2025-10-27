# ASR Service

FastAPI microservice that serves Chunkformer-based automatic speech recognition.

## Features
- Dynamic model management via the shared registry and `BaseService`
- Standard health and metrics endpoints
- REST API for model loading and transcription under `/asr`

## Endpoints
| Method | Path | Description |
| --- | --- | --- |
| POST | `/asr/load` | Load the Chunkformer model onto the requested device |
| POST | `/asr/unload` | Unload the currently loaded model |
| POST | `/asr/infer` | Transcribe a video file and return timestamped tokens |
| GET | `/asr/models` | List available ASR models and the currently loaded one |
| GET | `/asr/status` | Show system status and model metadata |
| GET | `/metrics` | Prometheus metrics |
| GET | `/health` | Service heartbeat |

## Configuration
The service pulls settings from environment variables using `ASRServiceConfig`:
- `SERVICE_NAME`
- `SERVICE_VERSION`
- `PORT`
- `CPU_FALLBACK`
- `CHUNKFORMER_MODEL_PATH`
- Optional tuning knobs: `TEMP_DIR`, `DEFAULT_CHUNK_SIZE`, `DEFAULT_LEFT_CONTEXT`, `DEFAULT_RIGHT_CONTEXT`, `DEFAULT_TOTAL_BATCH_DURATION`, `DEFAULT_SAMPLE_RATE`, `DEFAULT_NUM_EXTRACTION_WORKERS`, `DEFAULT_NUM_ASR_WORKERS`

## Running locally
```bash
uvicorn service_asr.main:app --host 0.0.0.0 --port 8002
```

Ensure the Chunkformer checkpoint directory referenced by `CHUNKFORMER_MODEL_PATH` contains `config.yaml`, `pytorch_model.bin`, and `vocab.txt`.
