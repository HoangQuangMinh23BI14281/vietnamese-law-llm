import os
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

from src.infrastructure.docling_loader import DoclingLoader
from src.infrastructure.embedding_client import EmbeddingClient
from src.infrastructure.weaviate_client import WeaviateClient

from src.application.chunker import LegalChunker
from src.application.pipeline import IndexingPipeline

from src.presentation.router import router as api_router, set_pipeline

EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://embedding-api:5000/embed")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

logger.info(f"Connecting to Embedding API at: {EMBEDDING_API_URL}")
logger.info(f"Connecting to Weaviate at: {WEAVIATE_URL}")

docling_loader = DoclingLoader()
embedding_client = EmbeddingClient(base_url=EMBEDDING_API_URL)
weaviate_client = WeaviateClient(url=WEAVIATE_URL)

legal_chunker = LegalChunker()

indexing_pipeline = IndexingPipeline(
    loader=docling_loader,
    chunker=legal_chunker,
    embedder=embedding_client,
    db=weaviate_client
)

app = FastAPI(
    title="Vietnam Legal Indexing Service",
    description="Microservice chuyên trách việc đọc PDF, cắt lớp và lưu vào Vector DB",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

set_pipeline(indexing_pipeline)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "service": "indexing-service",
        "status": "running",
        "architecture": "DDD/Clean Architecture"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=5001, reload=True)