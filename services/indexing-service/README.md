# Indexing Service

This service is a specialized background worker and API responsible for ingesting legal documents (PDFs), processing them into semantic chunks, and indexing them into the Vector Database (Weaviate).

## Overview

The Indexing Service implements a complete data pipeline:
1.  **Ingestion**: Reads and parses PDF documents using `Docling`.
2.  **Chunking**: Splits texts into logical legal units (e.g., Articles, Clauses) using `LegalChunker`.
3.  **Embedding**: Calls the **Embedding API** to convert text chunks into vectors.
4.  **Storage**: Saves the text chunks, metadata, and vectors into **Weaviate**.

## Architecture

The service follows a Clean Architecture / DDD pattern:
-   **Presentation**: `src/presentation` - API endpoints for file upload.
-   **Application**: `src/application` - Orchestrates the `IndexingPipeline`.
-   **Domain**: `src/domain` - Data models like `LegalChunk` and `ProcessingResult`.
-   **Infrastructure**: `src/infrastructure` - Adapters for Docling, Weaviate, and Embedding API.

## Prerequisites

-   Python 3.10+
-   Docker & Docker Compose
-   Access to running **Embedding API** and **Weaviate** services.

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `WEAVIATE_URL` | URL of the Weaviate Vector DB | `http://weaviate:8080` |
| `EMBEDDING_API_URL` | URL of the Embedding Service | `http://embedding-api:5000/embed` |

## Installation & Running

### Using Docker

```bash
docker-compose up -d indexing-service
```

### Running Locally

1.  **Install Dependencies**:
    *   Note: You may need system dependencies like `build-essential` or `gcc` to build `tree-sitter` required by Docling.

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server**:

    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
    ```

## API Endpoints

### `POST /index-upload`
Upload a PDF document to start the indexing process.

**Form Data:**
-   `file`: The PDF file to be indexed.

**Response:**
```json
{
  "filename": "luat-dat-dai.pdf",
  "message": "Processing started in background"
}
```

*Note: The actual processing happens asynchronously. Check the service logs for progress.*

### `GET /`
Health check and status information.
