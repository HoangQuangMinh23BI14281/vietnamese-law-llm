# LLM Gateway Service

The LLM Gateway is the central brain of the Vietnamese Law LLM Platform. It orchestrates the Retrieval-Augmented Generation (RAG) process, managing interactions between the User, Vector Database, Embedding Service, and Local LLM.

## Technical Overview

| Item | Value |
| :--- | :--- |
| Framework | FastAPI |
| Language | Python 3.10 |
| Port | 8001 |
| Key Libraries | transformers, torch, weaviate-client |

## Architecture

| Layer | Path | Description |
| :--- | :--- | :--- |
| Domain | src/domain | Interfaces (Ports) and data models |
| Application | src/application | Business logic (ChatService, RAG pipeline) |
| Infrastructure | src/infrastructure | Adapters for LLM, Weaviate, Embedding API |
| Presentation | src/presentation | FastAPI router |

## Key Features

1. Adaptive Query Routing (Strict vs Semantic search)
2. Hybrid Search (BM25 + Vector via Weaviate)
3. CRAG (Corrective RAG with LLM-based grading)
4. HyDE (Hypothetical Document Embeddings fallback)
5. Local LLM Inference (Qwen model)

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| WEAVIATE_URL | Weaviate DB URL | http://weaviate:8080 |
| EMBEDDING_API_URL | Embedding Service URL | http://embedding-api:5000/embed |
| HF_HOME | HuggingFace cache directory | /app/models |

## Running with Docker

```bash
docker-compose up -d llm-gateway
```

## API Reference

### POST /chat

Request:
```json
{"query": "Quy dinh ve thu hoi dat?"}
```

Response:
```json
{"answer": "Theo Dieu 62...", "sources": ["Luat Dat dai 2013"]}
```
