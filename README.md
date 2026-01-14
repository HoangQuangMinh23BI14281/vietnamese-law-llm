# Vietnamese Law Basic RAG Application (Qwen-7B-Instruct + Weaviate)

## 1. Introduction
This project is a specialized Large Language Model (LLM) application designed to assist legal professionals and citizens in navigating the complex landscape of Vietnamese Law. Unlike generic AI models, this platform is built on a **Retrieval-Augmented Generation (RAG)** architecture, ensuring that every answer is grounded in specific legal documents, articles, and decrees.

The system addresses common issues with LLMs, such as hallucinations (making up laws), by enforcing a strict retrieval-first approach. It combines the reasoning capabilities of modern open-source LLMs (Qwen) with a high-performance Vector Database (Weaviate) to provide accurate, citation-backed legal advice.

### Key Objectives
- **Accuracy**: Minimize hallucinations by grounding answers in retrieved legal texts.
- **Transparency**: Every answer includes specific citations (e.g., "Article 100, Penal Code 2015").
- **Privacy**: Fully offline-capable architecture. Data does not leave your infrastructure.
- **Performance**: Optimized for consumer-grade hardware (supports single GPU deployment).

## 2. System Architecture

The platform is microservices-based, following **Clean Architecture** principles to ensuring scalability, maintainability, and testability.

### 2.1. Global Architecture Diagram

```mermaid
graph TD
    User([User])
    
    subgraph "Frontend Layer"
        UI[Streamlit Web App]
    end
    
    subgraph "Application Layer"
        Gateway[LLM Gateway / Orchestrator]
        Indexer[Indexing Service]
    end
    
    subgraph "Infrastructure Layer"
        Weaviate[(Weaviate Vector DB)]
        Embed[Embedding API]
        LocalLLM[Local LLM (Qwen)]
    end

    User <-->|HTTP/WebSocket| UI
    
    %% Query Flow
    UI -->|POST /chat| Gateway
    Gateway -->|Get Vector| Embed
    Gateway -->|Search| Weaviate
    Gateway -->|Generate| LocalLLM
    
    %% Indexing Flow
    UI -->|POST /upload| Indexer
    Indexer -->|Parse PDF| Indexer
    Indexer -->|Get Vector| Embed
    Indexer -->|Store| Weaviate
```

### 2.2. Service Communication
All services run in Docker containers and communicate via a dedicated Docker network (`app-network`).
- **Frontend** talks to **LLM Gateway** (for chat) and **Indexing Service** (for uploads).
- **LLM Gateway** talks to **Weaviate** (retrieval) and **Embedding API** (vectorization).
- **Indexing Service** talks to **Embedding API** (vectorization) and **Weaviate** (storage).
- **Embedding API** is a shared stateless service used by both Gateway and Indexer.

## 3. Detailed Component Breakdown

### 3.1. Frontend Service
The user interface is built with **Streamlit**, chosen for its rapid development capabilities and native support for data visualization.
- **Role**: Presentation layer.
- **Features**:
    - **Interactive Chat**: A familiar chat interface with persistent session history.
    - **Document Upload**: A drag-and-drop interface for admin users to add new legal PDF documents to the knowledge base.
    - **Progress Feedback**: Real-time spinners and status messages during long-running operations.
- **Tech Stack**: Python, Streamlit, Requests.

### 3.2. LLM Gateway (The Core)
This is the brain of the operation. It does not just "call an LLM"; it orchestrates a complex thinking process.
- **Role**: Business logic, query planning, retrieval, and generation.
- **Advanced RAG Features**:
    - **Hybrid Search**: Combines **Semantic Search** (vector similarity) with **Keyword Search** (BM25 or strict text matching) to handle queries asking for specific articles (e.g., "Điều 100").
    - **Relevance Grading**: A lightweight LLM pass checks if retrieved documents are actually relevant to the query. If not, it discards them to prevent "poisoning" the context.
    - **HyDE (Hypothetical Document Embeddings)**: If direct search fails, the system generates a hypothetical "perfect answer" and uses its vector to search, bridging the vocabulary gap between user questions and legal text.
- **Tech Stack**: FastAPI, PyTorch, Transformers (HuggingFace).

**Operational Flow (Chat)**:
1.  Receive User Query.
2.  **Smart Routing**: Determine if query is legal or casual conversation.
3.  **Parallel Retrieval**: Fetch documents using Vector Search + Keyword Search.
4.  **Grading**: LLM validates retrieved documents (`Yes/No`).
5.  **Generation**: Valid documents + Query -> LLM -> Final Answer with Citations.

### 3.3. Indexing Service
Responsible for keeping the knowledge base up-to-date.
- **Role**: ETL (Extract, Transform, Load) pipeline for legal documents.
- **Pipeline**:
    1.  **Ingestion**: Receives PDF files.
    2.  **Parsing**: Uses `docling` to extract text while preserving structure (headers, tables).
    3.  **Chunking**: Implements **Semantic Chunking** specific to Vietnamese Law. Instead of arbitrary fixed-size chunks, it splits text by legal hierarchy (`Chapter` -> `Article` -> `Clause`). This is critical for retrieval accuracy.
    4.  **Embedding**: Converts chunks to vectors.
    5.  **Storage**: Pushes object (Text + Metadata + Vector) to Weaviate.
- **Tech Stack**: FastAPI, Docling, Weaviate Client.

### 3.4. Embedding API
A dedicated, high-performance microservice for computing vector embeddings.
- **Role**: Text-to-Vector conversion.
- **Model**: Uses `huyydangg/DEk21_hcmute_embedding` (Sentence Transformer), fine-tuned for Vietnamese.
- **Performance**:
    - **GPU Acceleration**: Auto-detects CUDA availability.
    - **Batch Processing**: Supports `/embed_batch` to process hundreds of chunks in parallel, significantly speeding up the indexing process.
- **Tech Stack**: FastAPI, Sentence-Transformers, PyTorch.

### 3.5. Vector Database (Weaviate)
Weaviate is an open-source vector search engine.
- **Role**: Long-term memory storage.
- **Schema**:
    - Class: `LegalDocument`
    - Properties: `text`, `source` (filename), `article` (number), `chapter` (number).
- **Configuration**: Running in standalone mode with persistent volume storage.

## 4. Technical Decisions & Optimizations

### 4.1. Clean Architecture
We explicitly chose strictly layered architecture for the Python services (Gateway, Indexing).
- **Domain Layer**: Contains plain Python objects (Pydantic models) and abstract interfaces (Ports). No external dependencies.
- **Application Layer**: Contains Use Cases (e.g., `ChatUseCase`, `UploadFileUseCase`). Orchestrate the flow of data.
- **Infrastructure Layer**: Contains the "messy" implementation details (DB drivers, API clients, concrete classes).
- **Presentation Layer**: The Web API (FastAPI) or UI (Streamlit).

**Why?** This allows us to swap components easily. For example, switching from Weaviate to Qdrant, or from Qwen to Llama 3, only requires changing one adapter file in the Infrastructure layer, without touching the core business logic.

### 4.2. Docker Optimization
Initial builds were over 20GB due to PyTorch duplication. We solved this by:
- **Single Stage Builds**: Using `pytorch/pytorch` base images directly for GPU services.
- **Usage of .dockerignore**: Excluding virtual environments, git history, and cache folders.
- **Shared Volumes**: Mounting large model cache directories (`/app/model_cache`) to the host machine. This prevents re-downloading 10GB+ of models every time the container restarts.

### 4.3. Observability
The platform is designed to be monitored (Deployment Pending).
- **Langfuse** (Integration Ready): For tracing LLM chains and debugging prompts.
- **Prometheus/Grafana**: For monitoring system resource usage (GPU VRAM, CPU, RAM) and API latency.

## 5. Deployment Guide

### Prerequisites
- **Docker & Docker Compose**: Installed and running.
- **NVIDIA GPU (Recommended)**: With updated drivers and `nvidia-container-toolkit` for Docker.
- **RAM**: Minimum 16GB (32GB recommended for smooth operation).
- **Disk Space**: At least 50GB free for models and vector data.

### 5.1. Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/HoangQuangMinh23BI14281/vietnamese-law-llm.git
    cd vietnamese-law-llm-platform
    ```

2.  **Environment Setup**:
    No manual `.env` file creation is strictly required for local dev as `docker-compose.yml` has sensible defaults. However, you can check `docker-compose.yml` to customize:
    - `MODEL_NAME`: Change LLM model.
    - `EMBEDDING_MODEL_NAME`: Change embedding model.

3.  **Download Models (Optional)**:
    The services will auto-download models on first launch. For faster startup, you can pre-download models into the `models_cache_` directories.

### 5.2. Running the Application
Start the entire stack with Docker Compose:

```bash
docker-compose up -d --build
```

This commands builds images for 4 services and pulls Weaviate.

**Verify Status**:
```bash
docker-compose ps
```
Ensure all 5 containers (`frontend`, `llm-gateway`, `indexing-service`, `embedding-api`, `weaviate`) are `Up`.

### 5.3. Accessing the Services
- **Frontend UI**: Open your browser at `http://localhost:8501`.
- **LLM Gateway API Docs**: `http://localhost:8001/docs`.
- **Embedding API Docs**: `http://localhost:5000/docs`.
- **Indexing Service Docs**: `http://localhost:5001/docs`.
- **Weaviate Console**: `http://localhost:8080`.

## 6. Development Workflow

### CI/CD Pipeline
We use GitHub Actions for continuous integration.
- **Configuration**: `.github/workflows/ci-cd.yaml`
- **Triggers**: Pushes to `main`.
- **Actions**:
    1.  **Smart Change Detection**: Only rebuilds services that have code changes.
    2.  **Disk Space Optimization**: Cleans runner environment before building.
    3.  **Build & Push**: Builds Docker images and pushes to GitHub Container Registry (GHCR).

### Adding New Dependencies
1.  Navigate to the service directory (e.g., `services/llm-gateway`).
2.  Add package to `requirements.txt`.
3.  Rebuild: `docker-compose up -d --build llm-gateway`.

### Troubleshooting
- **Connection Refused**: Ensure services are fully started. LLM loading takes time (30-60s). Check logs: `docker logs -f llm-gateway`.
- **CUDA/GPU Errors**: Verify `nvidia-smi` works on host and `nvidia-container-toolkit` is installed.
- **No Space Left**: Prune old docker images `docker system prune -a`.

## 7. Future Roadmap
- [ ] **Kubernetes Support**: Complete the Helm Charts in `k8s/` for GKE deployment.
- [ ] **Advanced RAG**: Implement GraphRAG for better understanding of legal relationships.
- [ ] **Auth**: Add user authentication (OIDC) to the Frontend.
- [ ] **Fine-tuning**: Fine-tune Qwen on specific Vietnamese legal datasets for better style alignment.

## 8. License
This project is licensed under the MIT License.
