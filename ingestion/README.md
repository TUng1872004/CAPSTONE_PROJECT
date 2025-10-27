# Ingestion Service — Video Processing Orchestration API

This service orchestrates end‑to‑end video processing: upload, segment detection (autoshot), ASR transcription, image frame extraction, LLM captioning, embedding generation, and optional persistence to a vector database (Milvus). It exposes a FastAPI REST surface, orchestrates tasks with Prefect, stores artifacts in MinIO (S3‑compatible), and tracks lineage/metadata in PostgreSQL. Microservices are discovered via Consul.


## Features

- FastAPI endpoints for upload, health, and management
- Prefect flow with parallel branches for efficient processing
- Artifact storage in MinIO with consistent key layout and presigned access
- Artifact lineage and status tracking in PostgreSQL
- Vector persistence and health checks for Milvus collections
- Microservice discovery via Consul with resilient HTTP clients (retries, timeouts)


## Architecture Overview

- API: FastAPI application (`main.py`) with lifecycle provisioning (`core/lifespan.py`).
- Orchestration: Prefect tasks and flow (`flow/video_processing.py`).
- Storage: MinIO S3 for artifacts (`core/storage.py`).
- Lineage: PostgreSQL tables for artifacts and parent/child graph (`core/pipeline/tracker.py`).
- Vector DB: Milvus collections for embeddings (image, image‑caption, segment‑caption).
- Microservices (discovered via Consul):
  - Autoshot (shot boundary detection)
  - ASR (speech‑to‑text)
  - LLM (captioning)
  - Image Embedding (feature vectors)
  - Text Embedding (sentence/text vectors)


## Quickstart (Docker Compose)

### Prerequisites

- Docker and Docker Compose
- (Recommended) NVIDIA GPU + NVIDIA Container Toolkit for GPU‑accelerated services
- Ports available: 8000 (API), 9000/9001 (MinIO), 4200 (Prefect), 8500 (Consul), 19530/9091 (Milvus)

### 1) Configure environment

Copy or create `.env` in `ingestion/` and set values for MinIO, PostgreSQL, Milvus, and service contexts. Example:

```
MINIO_HOST=localhost
MINIO_PORT=9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_USER=minioadmin
MINIO_PASSWORD=minioadmin
MINIO_SECURE=False

POSTGRE_DATABASE_URL=postgresql+asyncpg://prefect:prefect@localhost:5432/prefect

MILVUS_HOST=standalone
MILVUS_PORT=19530
MILVUS_USER=
MILVUS_PASSWORD=
MILVUS_DB_NAME=default

AUTOSHOT_CONTEXT=./prefect_agent/service_autoshot
ASR_CONTEXT=./prefect_agent/service_asr
IMAGE_EMBEDDING_CONTEXT=./prefect_agent/service_image_embedding
LLM_CONTEXT=./prefect_agent/service_llm
TEXT_EMBEDDING_CONTEXT=./prefect_agent/service_text_embedding

MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
LOCAL_DATA=service_data
```

Notes:
- Ensure `MILVUS_DB_NAME` is on its own line (no trailing text).
- If running without a GPU, configure each microservice to use CPU (see “Devices & Models”).

### 2) Start the stack

From `ingestion/`:

```
docker compose up -d --build
```

The compose file brings up: MinIO, Postgres, Consul, Milvus, Prefect server, and the microservice containers.

### 3) Start the API inside the container

The `ingestion-api` container mounts the source code as a volume. Start the FastAPI app inside it:

```
docker compose exec ingestion-api uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open docs at http://localhost:8000/docs

### 4) Verify health

```
curl http://localhost:8000/pipeline_check
curl http://localhost:8000/pipeline_check/storage
curl http://localhost:8000/pipeline_check/consul
```


## Prefect Agent Microservices Setup

The pipeline invokes several microservices located under `prefect_agent/`. Each service has its own `.env.example` you should copy to `.env` and customize. Docker Compose mounts each service directory and loads its `env_file`.

Services and locations:
- Autoshot (shot boundary detection): `prefect_agent/service_autoshot`
- ASR (speech‑to‑text): `prefect_agent/service_asr`
- LLM (captioning): `prefect_agent/service_llm`
- Image Embedding: `prefect_agent/service_image_embedding`
- Text Embedding: `prefect_agent/service_text_embedding`

Setup steps:
1) For each service directory, copy and edit the environment file:
   - `cp prefect_agent/service_autoshot/.env.example prefect_agent/service_autoshot/.env`
   - `cp prefect_agent/service_asr/.env.example prefect_agent/service_asr/.env`
   - `cp prefect_agent/service_llm/.env.example prefect_agent/service_llm/.env`
   - `cp prefect_agent/service_image_embedding/.env.example prefect_agent/service_image_embedding/.env`
   - `cp prefect_agent/service_text_embedding/.env.example prefect_agent/service_text_embedding/.env`

   Configure model checkpoints/API keys and optional `CPU_FALLBACK` in each `.env`.

2) Start the services (Compose targets):

```
docker compose up -d autoshot asr llm ie te
```

3) Confirm registration with Consul and service health:

```
curl http://localhost:8500/ui          # Consul UI
curl http://localhost:8000/pipeline_check/services/autoshot
curl http://localhost:8000/pipeline_check/services/asr
curl http://localhost:8000/pipeline_check/services/llm
curl http://localhost:8000/pipeline_check/services/image-embedding
curl http://localhost:8000/pipeline_check/services/text-embedding
```

GPU notes:
- Compose sets `gpus: all` and relevant NVIDIA variables for the microservices. Ensure the NVIDIA Container Toolkit is installed. If running CPU‑only, set `CPU_FALLBACK=true` (per service) and select CPU devices in the API task configs (see “Devices & Models”).


## API Usage

Base URL: `http://localhost:8000`

### Upload videos and start processing

Endpoint: `POST /uploads/`

Form fields:
- `files` (repeatable): video files, content types like `video/mp4`
- `user_id` (string): bucket namespace to store artifacts

Example:

```
curl -X POST "http://localhost:8000/uploads/" \
  -F "files=@/path/to/video1.mp4;type=video/mp4" \
  -F "files=@/path/to/video2.mp4;type=video/mp4" \
  -F "user_id=user123"
```

Response includes `run_id` and a suggested tracking URL.

### Management

- Get status: `GET /management/videos/{video_id}/status`
- Delete a video + descendants: `DELETE /management/videos/{video_id}`
- Delete a stage (and its descendants): `DELETE /management/videos/{video_id}/stages/{artifact_type}`
- Batch delete: `POST /management/videos/batch-delete` (JSON body: `["video_id_1", "video_id_2"]`)

### Health

- Overall: `GET /pipeline_check`
- Database: `GET /pipeline_check/database`
- Storage (MinIO): `GET /pipeline_check/storage`
- Consul services: `GET /pipeline_check/consul`
- Microservices:
  - `GET /pipeline_check/services/asr`
  - `GET /pipeline_check/services/autoshot`
  - `GET /pipeline_check/services/llm`
  - `GET /pipeline_check/services/image-embedding`
  - `GET /pipeline_check/services/text-embedding`
- Milvus collections:
  - `GET /pipeline_check/milvus/image-embeddings`
  - `GET /pipeline_check/milvus/text-caption-embeddings`
  - `GET /pipeline_check/milvus/segment-caption-embeddings`


## Data Flow & Tasks

The Prefect flow (`flow/video_processing.py`) executes the following stages, with parallel branches for throughput:

1. Video ingestion: register videos and persist originals to MinIO
2. Parallel:
   - Autoshot: detect shot boundaries; store segments JSON
   - ASR: transcribe audio; store transcripts JSON
3. Branch A: segment captions → text embeddings (segment level)
4. Branch B: extract frames → image captions → caption embeddings + image embeddings
5. (Optional) Persist embeddings to Milvus collections

Each stage uses a `BaseTask` implementation and an `ArtifactPersistentVisitor` to write outputs and lineage.


## Artifacts, Storage & Lineage

- Storage backend: MinIO (S3 API). Artifacts use consistent keys per type:
  - Videos: `videos/{video_name}.{ext}`
  - Autoshot segments: `autoshot/{video_name}.json`
  - ASR transcripts: `asr/{video_name}.json`
  - Images: `images/{video_name}/{frame_index}.webp` (if configured)
  - Image captions (JSON): `caption/image/{video_name}/{frame_index}.json`
  - Embeddings:
    - Image: `embedding/image/{video_name}/{frame_index}.npy`
    - Image caption: `embedding/image_caption/{video_name}/{frame_index}.npy`
    - Segment caption: `embedding/caption_segment/{video_name}/{start}_{end}.npy`

- PostgreSQL schema:
  - `artifacts_application` — artifact records (id, type, minio_url, parent_artifact_id, task_name, timestamps)
  - `artifact_lineage_application` — parent/child relationships

Status (`/management/videos/{video_id}/status`) is computed from lineage to report completed stages and progress.


## Vector Database (Milvus)

Collections are configured during app startup (`core/lifespan.py`). Example defaults:

- `image_embeddings` — dim 512, metric COSINE, index HNSW
- `text_caption_embeddings` — dim 384, metric COSINE, index HNSW
- `segment_caption_embeddings` — dim 512, metric COSINE, index HNSW

Use health endpoints under `/pipeline_check/milvus/*` to verify collection existence and stats.


## Configuration Reference

Environment variables (read by Pydantic settings):

- MinIO (`MINIO_*`): `MINIO_HOST`, `MINIO_PORT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_USER`, `MINIO_PASSWORD`, `MINIO_SECURE` (False/True)
- PostgreSQL: `POSTGRE_DATABASE_URL` (e.g., `postgresql+asyncpg://user:pass@host:5432/db`)
- Milvus (`MILVUS_*`): `MILVUS_HOST`, `MILVUS_PORT`, `MILVUS_USER`, `MILVUS_PASSWORD`, `MILVUS_DB_NAME`
- Consul: `CONSUL_HOST`, `CONSUL_PORT`
- Prefect: `PREFECT_API_URL` (compose sets a default for internal use)

### Environment files

- `ingestion/.env` — Primary environment used by Docker Compose for variable interpolation and by the FastAPI app for settings. Required.
- `ingestion/.env.docker` — Optional, container‑oriented defaults. Not loaded automatically by Compose. You may copy values from here into `.env` or pass it explicitly with `--env-file` if you prefer that workflow.
- `prefect_agent/*/.env.example` — Per‑service examples. Copy to `.env` in each service folder and adjust (model names, API keys, device fallbacks). These are loaded by Compose via each service’s `env_file` entry.


## Devices & Models

By default, task settings in `core/lifespan.py` set devices to `cuda`. For CPU‑only environments, change `device="cpu"` for:

- AutoshotSettings
- ASRSettings
- LLMCaptionSettings
- ImageCaptionSettings
- ImageEmbeddingSettings
- TextEmbeddingSettings

Rebuild/restart services after changes.


## Development

### Run API locally (without Docker)

1) Create a virtual environment and install dependencies:

```
python -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install fastapi[standard] uvicorn  # API runtime
pip install -r <generated requirements if applicable>  # or `uv sync` if using uv
```

2) Start the app:

```
uvicorn main:app --reload --port 8000
```

Ensure external services (MinIO, Postgres, Consul, Milvus, Prefect) are running or reachable.

### Tests

Unit tests: some client tests live under `test/`. Integration tests require running microservices locally.

```
pip install pytest
pytest -q
```

To run client integration tests, export `INTEGRATION=1` and ensure microservices are reachable on the expected ports (see `test/test_client_integration.py`).


## Operations

- Logs: by default, application logs are written to `logs/app.log`.
- Health: `GET /pipeline_check` summarizes component status; use sub‑checks to diagnose issues.
- Cleanup: management endpoints support cascading deletes for a video or stage.


## Troubleshooting & Notes

- If the API container does not start the app automatically, use:
  `docker compose exec ingestion-api uvicorn main:app --host 0.0.0.0 --port 8000 --reload`.
- If you see missing imports (e.g., `fastapi`) inside the container, install them:
  `docker compose exec ingestion-api pip install fastapi[standard] uvicorn`.
- Ensure `MILVUS_DB_NAME` in `.env` has no trailing text; each variable should be on its own line.
- Service discovery depends on Consul; verify at `http://localhost:8500/ui` and via `GET /pipeline_check/consul`.
- For GPU execution, confirm the NVIDIA runtime is installed and available to containers; otherwise, switch task configs to `device="cpu"`.


## License

Internal project documentation. Licensing to be defined by the repository owner.
