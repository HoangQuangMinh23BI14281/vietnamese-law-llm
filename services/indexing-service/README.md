# Indexing Service

## Overview
The **Indexing Service** is responsible for ingesting legal documents (mainly PDF), processing them into meaningful chunks, and indexing them into the Vector Database (Weaviate). This ensures that the RAG system has an up-to-date and searchable knowledge base.

## Architecture
This service uses a pipeline approach to transform raw files into vector embeddings.

### Indexing Pipeline
```mermaid
sequenceDiagram
    participant User as Frontend/Admin
    participant API as FastAPI
    participant Loader as Docling Loader
    participant Chunker as Legal Chunker
    participant Embed as Embedding API
    participant DB as Weaviate

    User->>API: Upload PDF File
    API->>Loader: Parse PDF
    Loader-->>API: Markdown Content
    
    API->>Chunker: Split Content
    Note over Chunker: Semantic Splitting via Regex<br/>(Article/Chapter detection)
    Chunker-->>API: List[Chunks]
    
    loop For each Chunk
        API->>Embed: Get Vector Embedding
        Embed-->>API: Vector [0.12, -0.5, ...]
        API->>DB: Store Object + Vector
    end
    
    API-->>User: Success (Indexed N chunks)
```

## Key Components
1.  **Docling Loader**: Uses `docling` library to intelligently parse PDF documents, preserving structure (headers, tables) and converting them to Markdown.
2.  **Legal Chunker**: A specialized chunking strategy optimized for Vietnamese Law. It splits text based on legal hierarchy (`Chương`, `Điều`, `Khoản`) rather than just character count.
3.  **Embedding Client**: Communicates with the `embedding-api` to convert text chunks into vector representations.
4.  **Weaviate Client**: Manages the schema and insertion of data into the Weaviate Vector DB.

## Configuration
Environment variables:
- `EMBEDDING_API_URL`: URL of the embedding service.
- `WEAVIATE_URL`: URL of the Weaviate instance.

## API Endpoints
### `POST /api/v1/indexing/upload`
Upload and index a PDF file.

**Request:** `multipart/form-data`
- `file`: The PDF file to upload.

**Response:**
```json
{
  "message": "Đã index thành công 150 chunks.",
  "filename": "luat-dat-dai.pdf"
}
```

### `GET /`
Service status check.
