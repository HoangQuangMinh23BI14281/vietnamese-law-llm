# Indexing Service

The Indexing Service acts as the Data Ingestion Pipeline for the platform, parsing legal documents (PDF/Word), chunking them into semantic units, and storing them in the Vector Database.

## Technical Overview

| Item | Value |
| :--- | :--- |
| Framework | FastAPI |
| Language | Python 3.10 |
| Port | 5001 |
| Key Libraries | docling, weaviate-client, requests |

## Architecture

| Layer | Path | Description |
| :--- | :--- | :--- |
| Domain | src/domain | Data models (LegalChunk, ProcessingResult) |
| Application | src/application | LegalChunker, IndexingPipeline |
| Infrastructure | src/infrastructure | DoclingLoader, WeaviateClient, EmbeddingClient |
| Presentation | src/presentation | FastAPI router for file upload |

## Key Features

1. PDF/Word parsing via Docling
2. Vietnamese legal structure recognition (Part/Chapter/Section/Article)
3. Metadata extraction (Article number, Chapter)
4. Batch vector storage to Weaviate
5. Background task processing

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| WEAVIATE_URL | Weaviate DB URL | http://weaviate:8080 |
| EMBEDDING_API_URL | Embedding Service URL | http://embedding-api:5000/embed |

## Running with Docker

```bash
docker-compose up -d indexing-service
```

## API Reference

### POST /index-upload

Request: multipart/form-data with file field.

Response:
```json
{"filename": "Luat_Dat_Dai.pdf", "message": "Processing started in background"}
```
