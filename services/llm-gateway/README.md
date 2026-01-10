# LLM Gateway Service

This service acts as the central gateway for the Vietnamese Law LLM Platform. It orchestrates the flow of information between the user, the Retrieval-Augmented Generation (RAG) system, and the LLM.

## Overview

The LLM Gateway is responsible for:
1.  **Receiving Chat Requests**: Exposes a REST API for clients to send queries.
2.  **RAG Orchestration**: Coordinates with:
    *   **Embedding API**: To vectorize user queries.
    *   **Vector DB (Weaviate)**: To retrieve relevant legal documents.
    *   **LLM (Qwen)**: To generate responses based on the retrieved context.
3.  **Local LLM Inference**: Runs a local Qwen model (e.g., `Qwen/Qwen3-0.6B`) for generating answers.

## Advanced RAG Techniques

This service implements several advanced RAG (Retrieval-Augmented Generation) techniques to ensure high accuracy and relevance:

### 1. Query Routing (Logical Branching)
The system analyzes the user's question to decide the best search strategy (`src/application/chat_service.py`):
*   **Strict Mode**: If the query cites specific articles (e.g., "Điều 5"), it executes a structured filter search to pinpoint that exact legal provision.
*   **Semantic Mode**: For general questions, it uses broad semantic search.

### 2. Hybrid Search
Utilizes **Weaviate's Hybrid Search** capability (`src/infrastructure/vector_db_adapter.py`):
*   Combines **Sparse Vectors** (BM25 keyword matching) and **Dense Vectors** (Embedding semantic matching).
*   Uses an alpha parameter (default 0.5) to balance between keyword exactness and semantic understanding.

### 3. CRAG (Corrective RAG)
Implements a self-corrective feedback loop:
*   **Relevance Grading**: An LLM-based evaluator checks if retrieved documents are relevant to the query.
*   **Fallback Mechanism**: If the initial search yields poor results (filtered by the Grader), the system automatically attempts alternative search strategies (e.g., switching from Strict to Broad search).

### 4. HyDE (Hypothetical Document Embeddings)
Used as a fallback when direct retrieval fails:
*   The LLM generates a "hypothetical" perfect answer based on the query.
*   This hypothetical answer is vector-embedded to search for real documents that are semantically similar to the ideal answer, rather than just matching the raw query questions.

### 5. Prompt Engineering
*   **Recency Bias Optimization**: Critical instructions (e.g., "Must answer in Vietnamese") are placed at the very end of the prompt to maximize adherence.
*   **Thinking Mode**: Supports parsing `<think>` tags from newer reasoning models to separate "chain-of-thought" from the final answer.

## Architecture

The project follows a Clean Architecture design with the following layers:
-   **Presentation**: FastAPI router handling HTTP requests (`src/presentation`).
-   **Application**: Business logic for chat processing (`src/application`).
-   **Domain**: Core data models and interface definitions (`src/domain`).
-   **Infrastructure**: Adapters for external services like Weaviate, Embedding API, and local LLM (`src/infrastructure`).

## Prerequisites

-   Python 3.10+
-   Docker & Docker Compose (for containerized deployment)
-   CUDA-compatible GPU (recommended for local LLM inference)

## Configuration

The service uses environment variables for configuration. You can set these in a `.env` file or via Docker environment variables.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `WEAVIATE_URL` | URL of the Weaviate Vector DB | `http://weaviate:8080` |
| `EMBEDDING_API_URL` | URL of the Embedding Service | `http://embedding-api:5000/embed` |
| `HF_HOME` | HuggingFace model cache directory | `/app/models` |

## Installation & Running

### Using Docker (Recommended)

This service is designed to run as part of the larger platform via Docker Compose.

```bash
# In the root of the project
docker-compose up -d llm-gateway
```

### Running Locally

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    *Note: You may need to install PyTorch with CUDA support separately if not covered by requirements.*

2.  **Run the Server**:

    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
    ```

## API Endpoints

### `POST /chat`
Process a user query and return a generated response.

**Request Body:**
```json
{
  "question": "Quy định về thuế thu nhập cá nhân?"
}
```

**Response:**
```json
{
  "answer": "Theo quy định hiện hành...",
  "sources": [...]
}
```

### `GET /health`
Health check endpoint.
