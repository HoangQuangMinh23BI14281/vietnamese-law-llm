from fastapi import FastAPI
from src.presentation.routes import router
from src.infrastructure.huggingface_adapter import HuggingFaceEmbeddingAdapter
from src.application.use_cases import CreateEmbeddingUseCase, HealthCheckUseCase, BatchEmbeddingUseCase
import logging

# Cấu hình log
logging.basicConfig(level=logging.INFO)

# 1. KHỞI TẠO INFRASTRUCTURE (Load Model - tốn thời gian nhất nên làm 1 lần ở đây)
# Singleton instance
embedding_service = HuggingFaceEmbeddingAdapter()

# 2. KHỞI TẠO USE CASES
create_uc = CreateEmbeddingUseCase(embedding_service)
health_uc = HealthCheckUseCase(embedding_service)
batch_uc = BatchEmbeddingUseCase(embedding_service)

# Dependency Container đơn giản
def get_dependencies():
    return {
        "create": create_uc,
        "health": health_uc,
        "batch": batch_uc
    }

app = FastAPI(title="Vietnamese Law Embedding API ")
from src.presentation.routes import get_use_cases
app.dependency_overrides[get_use_cases] = get_dependencies

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)