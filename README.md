# 🎬 Video Deep Search

> Agentic Video QA system: **ingest videos → index with ML → search with multi-agent AI**. Designed for Vietnamese-language video understanding.

## How It Works

**"Index-Then-Act"** paradigm with 4 main services:

```
Frontend (React 19, :5173)
    ↕ Socket.IO + REST
Backend (FastAPI, :8010)
    ↕ HTTP
├── Ingestion Pipeline (Prefect + FastAPI, :8000)
│       ↕
│   5 GPU Microservices (Autoshot, ASR, LLM, ImageEmbed, TextEmbed)
│       ↕
│   Storage: Milvus (vectors) + MinIO (files) + PostgreSQL (metadata)
│
└── VideoDeepSearch Agent (LlamaIndex + Gemini 2.5, :8050)
        ↕
    Milvus + MinIO (search & retrieve)
```

### Phase 1 — Ingestion

Prefect-orchestrated pipeline transforms raw videos into searchable vectors:

1. **Download** → store video in MinIO
2. **Autoshot** → shot boundary detection (GPU) | **ASR** → speech-to-text (GPU) *(parallel)*
3. **Frame Extraction** → N keyframes per segment (OpenCV)
4. **LLM Captioning** → describe segments & frames (Gemini)
5. **Embedding** → OpenCLIP visual (512d) + mmbert text (768d) + BM25 sparse
6. **Persist** → Milvus collections: `image_milvus` (per-frame) + `segment_milvus` (per-segment)

### Phase 2 — Multi-Agent Search

LlamaIndex Workflow with Gemini 2.5 models:

```
Query → Greeter (route) → Planner (decompose) → Sub-Orchestrator → Workers → Final Response
```

- **Planner** splits queries into Visual (English) + Linguistic (Vietnamese) sub-tasks
- **Workers** use dual-mode execution: direct tool calls OR Python code generation in sandbox
- **Tools**: visual search, caption search, multimodal hybrid search, segment navigation, ASR retrieval, on-demand captioning, query enhancement

### Frontend

React 19 + Vite 7 + Tailwind CSS v4. ChatGPT-like streaming UI with video library management, drag-and-drop upload, Google OAuth.

### Backend

FastAPI + Socket.IO gateway. MongoDB (Beanie ODM) for users/sessions/messages. JWT auth. Proxies chat to the agent via WebSocket streaming.

---

## Tech Stack

| Layer | Stack |
|-------|-------|
| Frontend | React 19, Vite 7, Tailwind v4, Zustand, Socket.IO |
| Backend | FastAPI, Socket.IO, MongoDB (Beanie), MinIO, JWT |
| Ingestion | Prefect 3, OpenCV, yt-dlp, SQLAlchemy |
| Agent | LlamaIndex Workflows, Gemini 2.5 (Flash/Pro/Lite) |
| Vector DB | Milvus 2.6 (HNSW, hybrid dense+sparse) |
| Embeddings | OpenCLIP (512d), mmbert (768d), BM25 |
| ML Services | Autoshot, ASR, LLM, Image Embed, Text Embed (GPU) |
| Infra | Docker Compose, Consul, PostgreSQL, Redis, MinIO |

---

## Installation

### Prerequisites

- Python ≥ 3.12, Node.js ≥ 18, Docker + Docker Compose, NVIDIA GPU + CUDA
- [uv](https://docs.astral.sh/uv/) package manager
- API Keys: Google Gemini, Google OAuth, Moondream (optional)

### 1. Infrastructure

```bash
cd ingestion
docker compose up -d
# Starts: Milvus(:19530), MinIO(:9000), PostgreSQL(:5432), Consul(:8500),
#         Redis, Prefect(:4200), GPU microservices(:8001-8005)
```

### 2. Ingestion API

```bash
cd ingestion
cp .env.example .env   # configure API keys & service URLs
uv sync
uv run python main.py  # :8000
```

### 3. VideoDeepSearch Agent

```bash
cd videodeepsearch
cp .env.example .env   # configure Gemini key, Milvus, MinIO, PostgreSQL
uv sync
uv run python main.py  # :8050
```

### 4. Backend

```bash
cd backend
# configure .env: MongoDB, MinIO, agent URL
uv sync
uv run python main.py  # :8010
```

> Requires MongoDB running separately (default `localhost:27017`)

### 5. Frontend

```bash
cd frontend
npm install
# create .env: VITE_PRIMARY_URL, VITE_INGESTION_URL, VITE_GOOGLE_OAUTH_CLIENT_ID
npm run dev            # :5173
```

---

## Key Environment Variables

| Service | Variable | Description |
|---------|----------|-------------|
| All | `GOOGLE_API_KEY` | Gemini API key |
| Ingestion | `MILVUS_HOST/PORT` | Milvus vector DB |
| Ingestion | `MINIO_ENDPOINT` | MinIO S3 storage |
| Ingestion | `POSTGRE_DATABASE_URL` | PostgreSQL |
| Ingestion | `CONSUL_HOST/PORT` | Service discovery |
| Agent | `MILVUS_HOST/PORT` | Milvus connection |
| Agent | `MINIO_ENDPOINT` | MinIO connection |
| Backend | `MONGO_URI` | MongoDB |
| Frontend | `VITE_PRIMARY_URL` | Backend URL (`:8010`) |
| Frontend | `VITE_INGESTION_URL` | Ingestion URL (`:8000`) |
| Frontend | `VITE_GOOGLE_OAUTH_CLIENT_ID` | Google OAuth |

---

## API Endpoints (Key)

| Service | Method | Endpoint | Purpose |
|---------|--------|----------|---------|
| Backend | POST | `/api/user/login/google` | Google OAuth login |
| Backend | WS | `stream_chat` event | Real-time AI chat |
| Backend | POST | `/api/user/uploads` | Upload videos |
| Backend | GET | `/api/user/videos` | List videos |
| Ingestion | POST | `/uploads/` | Trigger ingestion |
| Ingestion | GET | `/management/videos/:id/status` | Ingestion progress |
| Ingestion | GET | `/pipeline_check` | Health check |
| Agent | WS | `/ws/start_workflow` | Multi-agent search |
| Agent | GET | `/health/ready` | Readiness check |

---

## Evaluation (TC/)

51 Vietnamese test questions across 8+ categories (visual retrieval, factual QA, temporal reasoning, cross-modal). BERT-based semantic similarity scoring against ground truth.

```bash
cd TC
python download.py    # download test videos
python construct.py   # manage QA pairs & agent traces
python sim.py         # compute similarity scores
```
