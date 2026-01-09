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

@router.post("/index-upload")
async def index_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. Lưu file tạm
    os.makedirs("data/uploads", exist_ok=True)
    file_path = f"data/uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Chạy Pipeline dưới background (để trả lời UI ngay lập tức)
    if pipeline_instance:
        background_tasks.add_task(pipeline_instance.run_pipeline, file_path)
        return {"filename": file.filename, "message": "Processing started in background"}
    else:
        return {"error": "Pipeline not initialized"}