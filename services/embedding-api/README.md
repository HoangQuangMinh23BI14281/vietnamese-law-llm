# Embedding API Service

## Overview
The **Embedding API** is a specialized microservice dedicated to converting text into vector representations (embeddings). It uses **Sentence Transformers** models (specifically `huyydangg/DEk21_hcmute_embedding` by default) to generate high-quality semantic vectors optimized for Vietnamese legal text.

## Architecture
The service is built with **FastAPI** using strict **Clean Architecture**:
- **Presentation Layer**: HTTP Controllers/Routes.
- **Application Layer**: Use Cases (CreateEmbedding, BatchEmbedding).
- **Domain Layer**: Interface definitions (Ports).
- **Infrastructure Layer**: HuggingFace/SentenceTransformers Adapter implementation.

### Processing Flow
```mermaid
graph LR
    subgraph Client
        Sender[Gateway / Indexing]
    end

    subgraph Embedding Service
        Router[FastAPI Router]
        UseCase[Use Case]
        Adapter[HuggingFace Adapter]
        Model[Sentence Transformer Model]
    end

    Sender -->|POST /embed| Router
    Router --> UseCase
    UseCase --> Adapter
    Adapter -->|Tokenize & Encode| Model
    Model -->|Vector Array| Adapter
    Adapter -->|List[float]| Router
    Router -->|JSON| Sender
```

## Key Features
- **GPU Acceleration**: Automatically detects and uses CUDA (NVIDIA GPU) if available.
- **Batch Processing**: Supports batch embedding generation for high-throughput indexing operations.
- **Model Caching**: Downloads and caches models locally to avoid repeated downloads.
- **Environment Configurable**: Model selection is controlled via environment variables.

## Configuration
Environment variables:
- `MODEL_NAME`: The HuggingFace model ID to use (Default: `huyydangg/DEk21_hcmute_embedding`).
- `PORT`: Service port (Default: `5000`).

## API Endpoints

### `POST /embed`
Generate embedding for a single text string.

**Request:**
```json
{
  "text": "Điều 101 bộ luật hình sự"
}
```

**Response:**
```json
{
  "embedding": [0.012, -0.45, ..., 0.88]
}
```

### `POST /embed_batch`
Generate embeddings for a list of texts (More efficient).

**Request:**
```json
{
  "texts": ["Văn bản luật A", "Văn bản luật B"]
}
```

**Response:**
```json
{
  "embeddings": [
    [0.1, 0.2, ...],
    [0.3, 0.4, ...]
  ]
}
```

### `GET /health`
Returns service status and underlying model info.
