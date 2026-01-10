# Frontend Service

The Frontend Service provides the interactive user interface for the Vietnamese Law LLM Platform, enabling legal consultation (Chat) and document management (Knowledge Base Upload).

## Technical Overview

| Item | Value |
| :--- | :--- |
| Framework | Streamlit |
| Language | Python 3.10 |
| Port | 8501 |
| Key Libraries | streamlit, requests, pydantic |

## Architecture

| Layer | Path | Description |
| :--- | :--- | :--- |
| Domain | src/domain | Data schemas (Pydantic models) |
| Application | src/application | ChatService, UploadService |
| Infrastructure | src/infrastructure | GatewayAPI, IndexingAPI clients |
| Presentation | src/presentation | Views (chat_view, upload_view) |

## Key Features

1. Interactive chat interface with session history
2. Source citation display
3. Document upload for knowledge base
4. Visual feedback during processing

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| LLM_GATEWAY_URL | LLM Gateway Service URL | http://localhost:8001 |
| INDEXING_SERVICE_URL | Indexing Service URL | http://localhost:5001 |

## Running with Docker

```bash
docker-compose up -d frontend
```

## API Reference

This service is a UI application, not an API. Access via browser at http://localhost:8501.
