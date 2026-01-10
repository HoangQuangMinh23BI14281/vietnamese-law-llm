# Frontend Service

This is the user interface for the Vietnamese Law LLM Platform, built with **Streamlit**. It provides an interactive web-based interface for users to chat with the AI and for administrators to upload new legal documents.

## Overview

The Frontend service connects to the backend microservices to provide two main features:
1.  **Chat Interface (Hỏi Đáp)**: Allows users to ask questions. The app sends queries to the **LLM Gateway** and displays the response along with source references.
2.  **Knowledge Ingestion (Nạp Kiến Thức)**: Allows users to upload PDF documents. These are sent to the **Indexing Service** to be processed and added to the vector database.

## Architecture

The project is structured using checks and explicit layers even within the Streamlit app:
-   **Presentation**: `src/presentation` - UI components and Streamlit views (`render_chat_view`, `render_upload_view`).
-   **Application**: `src/application` - Logic binding UI actions to backend calls (`ChatService`, `UploadService`).
-   **Infrastructure**: `src/infrastructure` - HTTP Clients for `llm-gateway` and `indexing-service`.

## Prerequisites

-   Python 3.10+
-   Docker & Docker Compose

## Configuration

The service connects to backend APIs via environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LLM_GATEWAY_URL` | URL of the LLM Gateway | `http://localhost:8001` |
| `INDEXING_SERVICE_URL` | URL of the Indexing Service | `http://localhost:5001` |

## Installation & Running

### Using Docker

```bash
docker-compose up -d frontend
```

### Running Locally

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Streamlit**:

    ```bash
    streamlit run src/main.py --server.port=8501
    ```

## Usage

Access the web interface at `http://localhost:8501`.

-   **Tab 1: Nạp Kiến Thức**: Upload PDF files (e.g., Law documents).
-   **Tab 2: Hỏi Đáp**: Chat with the system regarding Vietnamese Law.
