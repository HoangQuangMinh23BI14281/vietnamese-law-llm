# Embedding API Service

The Embedding API Service handles vectorization for the platform, converting text input into high-dimensional vectors for semantic search and retrieval in the RAG pipeline.

## Technical Overview

| Item | Value |
| :--- | :--- |
| Framework | FastAPI |
| Language | Python 3.10 |
| Port | 5000 |
| Key Libraries | sentence-transformers, torch |

## Architecture

| Layer | Path | Description |
| :--- | :--- | :--- |
| Domain | src/domain | Interfaces (IEmbeddingService) |
| Application | src/application | Use cases (CreateEmbeddingUseCase) |
| Infrastructure | src/infrastructure | HuggingFaceEmbeddingAdapter |
| Presentation | src/presentation | FastAPI routes |

## Key Features

1. Text to Vector conversion
2. Vietnamese legal text optimized model (huyydangg/DEk21_hcmute_embedding)
3. Automatic GPU detection (CUDA)
4. Model caching to persistent volume

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| HF_HOME | HuggingFace cache directory | /app/models |

## Running with Docker

```bash
docker-compose up -d embedding-api
```

## API Reference

### POST /embed

Request:
```json
{"text": "Cong dan co quyen tu do kinh doanh..."}
```

Response:
```json
{"embedding": [0.012, -0.45, ...], "dimension": 768}
```
