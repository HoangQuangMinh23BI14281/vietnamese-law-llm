# Embedding API Service

This service provides a standalone API for generating vector embeddings from text inputs. It utilizes `sentence-transformers` to compute encodings, enabling semantic search and retrieval capabilities for the platform.

## Overview

The Embedding API is designed to:
1.  **Vectorize Text**: Convert text strings into high-dimensional vector representations.
2.  **Serve Models**: Host embedding models (e.g., HuggingFace models) efficiently.
3.  **Support RAG**: Provide the embedding foundation for the Indexing Service and LLM Gateway.

## Architecture

The service implements a Clean Architecture pattern:
-   **Presentation**: `src/presentation` - FastAPI routes handling HTTP requests.
-   **Application**: `src/application` - Use cases like `CreateEmbeddingUseCase`.
-   **Domain**: `src/domain` - Interfaces and core logic.
-   **Infrastructure**: `src/infrastructure` - Implementation of embedding logic using `sentence-transformers`.

## Prerequisites

-   Python 3.10+
-   Docker & Docker Compose
-   GPU (optional but recommended for performance)

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `HF_HOME` | Directory for storing HuggingFace models | `/app/models` |
| `PORT` | Service port | `5000` |

## Installation & Running

### Using Docker

```bash
docker-compose up -d embedding-api
```

### Running Locally

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server**:

    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload
    ```

## API Endpoints

### `POST /embed`
Generates a vector embedding for the provided text.

**Request Body:**
```json
{
  "text": "Điều 5 Hiến pháp năm 2013 quy định về các dân tộc."
}
```

**Response:**
```json
{
  "embedding": [0.12, -0.05, 0.88, ...], (vector list)
  "model": "model-name"
}
```

### `GET /` or `GET /health`
Health check endpoints to verify service status and model readiness.
