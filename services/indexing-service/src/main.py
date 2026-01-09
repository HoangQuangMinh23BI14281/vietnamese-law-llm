import os
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- 1. CONFIG & SETUP ---
# Load biến môi trường từ file .env
load_dotenv()

# Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# --- 2. IMPORT MODULES (DDD LAYERS) ---
# Infrastructure: Các công cụ kết nối bên ngoài
from src.infrastructure.docling_loader import DoclingLoader
from src.infrastructure.embedding_client import EmbeddingClient
from src.infrastructure.weaviate_client import WeaviateClient

# Application: Logic nghiệp vụ chính
from src.application.chunker import LegalChunker
from src.application.pipeline import IndexingPipeline

# Presentation: API Router
from src.presentation.router import router as api_router, set_pipeline

# --- 3. KHỞI TẠO INFRASTRUCTURE (CÔNG CỤ) ---
# Lấy cấu hình từ biến môi trường (Docker Compose truyền vào)
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://embedding-api:5000/embed")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

logger.info(f"🔌 Connecting to Embedding API at: {EMBEDDING_API_URL}")
logger.info(f"🔌 Connecting to Weaviate at: {WEAVIATE_URL}")

# Tạo các object kết nối
docling_loader = DoclingLoader()
embedding_client = EmbeddingClient(base_url=EMBEDDING_API_URL)
weaviate_client = WeaviateClient(url=WEAVIATE_URL)

# --- 4. KHỞI TẠO APPLICATION (LOGIC) ---
# Tạo bộ cắt chunk (Logic cũ của bạn)
legal_chunker = LegalChunker()

# Tạo Pipeline hoàn chỉnh: Nối dây các công cụ lại với nhau
# Pipeline cần: Loader để đọc -> Chunker để cắt -> Embedder để hóa vector -> DB để lưu
indexing_pipeline = IndexingPipeline(
    loader=docling_loader,
    chunker=legal_chunker,
    embedder=embedding_client,
    db=weaviate_client
)

# --- 5. SETUP FASTAPI (PRESENTATION) ---
app = FastAPI(
    title="Vietnam Legal Indexing Service",
    description="Microservice chuyên trách việc đọc PDF, cắt lớp và lưu vào Vector DB",
    version="2.0.0"
)

# Cấu hình CORS (Cho phép Frontend hoặc Gateway gọi tới)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 6. DEPENDENCY INJECTION (QUAN TRỌNG) ---
# Bơm (Inject) pipeline đã khởi tạo vào trong Router
# Giúp Router có thể dùng được logic xử lý mà không cần khởi tạo lại
set_pipeline(indexing_pipeline)

# Đăng ký Router vào App
app.include_router(api_router)

# --- 7. HEALTH CHECK ENDPOINT ---
@app.get("/")
def root():
    return {
        "service": "indexing-service",
        "status": "running",
        "architecture": "DDD/Clean Architecture"
    }

if __name__ == "__main__":
    import uvicorn
    # Chạy server tại port 5001 (khớp với docker-compose)
    uvicorn.run("src.main:app", host="0.0.0.0", port=5001, reload=True)