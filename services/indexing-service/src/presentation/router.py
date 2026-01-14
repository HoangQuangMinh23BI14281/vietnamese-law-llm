import shutil
import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from src.application.pipeline import IndexingPipeline
# Import các Dependency sẽ được inject từ main (hoặc dùng thư viện DI)

router = APIRouter()

# Biến tạm để giữ pipeline (trong thực tế nên dùng Dependency Injection của FastAPI)
pipeline_instance: IndexingPipeline = None 

def set_pipeline(pipeline: IndexingPipeline):
    global pipeline_instance
    pipeline_instance = pipeline

@router.get("/health")
async def health_check():
    # Kiểm tra xem pipeline đã sẵn sàng chưa (nó phụ thuộc vào embedding service)
    # Trong thực tế có thể gọi ping tới embedding-api
    return {"status": "ready", "service": "indexing-service"}

@router.post("/index-upload")
async def index_document(file: UploadFile = File(...)):
    # 1. Lưu file tạm
    os.makedirs("data/uploads", exist_ok=True)
    file_path = f"data/uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Chạy Pipeline ĐỒNG BỘ (theo yêu cầu báo timing chính xác)
    if pipeline_instance:
        result = pipeline_instance.run_pipeline(file_path)
        return result
    else:
        return {"error": "Pipeline not initialized"}