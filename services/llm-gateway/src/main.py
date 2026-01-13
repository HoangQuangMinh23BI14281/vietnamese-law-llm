
import os
import logging
import sys
from fastapi import FastAPI
from dotenv import load_dotenv

from src.infrastructure.embedding_adapter import HttpEmbeddingAdapter
from src.infrastructure.vector_db_adapter import WeaviateAdapter
from src.infrastructure.llm_adapter import QwenLocalAdapter

from src.application.chat_service import ChatService
from src.presentation.router import router, set_chat_service

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
load_dotenv()

app = FastAPI(title="Vietnamese Law LLM Gateway")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://embedding-api:5000/embed")

embedder_adapter = HttpEmbeddingAdapter(api_url=EMBEDDING_API_URL)
weaviate_adapter = WeaviateAdapter(url=WEAVIATE_URL, class_name="LegalDocument")
llm_adapter = QwenLocalAdapter()


chat_service = ChatService(
    embedder=embedder_adapter,
    vector_db=weaviate_adapter,
    llm=llm_adapter
)

set_chat_service(chat_service)
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "llm-gateway-local"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)