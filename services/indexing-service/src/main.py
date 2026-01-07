import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel

# --- 1. Fix Path (Phải nằm trên cùng trước khi import src) ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- 2. Import các module nội bộ ---
from src.infrastructure.docling_loader import DoclingLoader
from src.processors.legal_chunker import LegalDocProcessor
from src.infrastructure.embedding_client import EmbeddingClient
from src.infrastructure.weaviate_client import WeaviateClient

app = FastAPI(title="Indexing Service")

# --- 3. Cấu hình & Khởi tạo ---
UPLOAD_DIR = "/app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Lấy cấu hình từ biến môi trường (Docker Compose sẽ truyền vào)
# Nếu không có biến môi trường thì dùng mặc định (localhost) để test cục bộ
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://host.docker.internal:5000/embed")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://host.docker.internal:8080")

print(f"🔌 Connecting to Embedding API at: {EMBEDDING_API_URL}")
print(f"🔌 Connecting to Weaviate at: {WEAVIATE_URL}")

# Khởi tạo các class xử lý (Singleton)
loader = DoclingLoader()
processor = LegalDocProcessor()
embedder = EmbeddingClient(api_url=EMBEDDING_API_URL)
weaviate_client = WeaviateClient(url=WEAVIATE_URL)

class IndexRequest(BaseModel):
    file_path: str 

# --- 4. Logic xử lý nền ---
def process_file_background(file_path: str):
    """
    Hàm xử lý chạy ngầm: Load PDF -> Chunk -> Embed -> Save to Weaviate
    """
    try:
        print(f"⏳ Bắt đầu xử lý file: {file_path}")
        
        # Bước 1: Extract Text (Docling)
        markdown = loader.load_to_markdown(file_path)
        
        # Bước 2: Chunking (Cắt nhỏ)
        chunks = processor.parse_and_chunk(markdown, source_name=os.path.basename(file_path))
        print(f"✅ Tách thành công {len(chunks)} chunks.")
        
        # Bước 3: Embedding (Tạo vector)
        print("🧠 Đang tạo embedding cho từng chunk...")
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            vector = embedder.get_embedding(chunk.text)
            if vector:
                chunk.embedding = vector
                valid_chunks.append(chunk)
            
            # Log tiến độ mỗi 10 chunk để đỡ spam
            if (i + 1) % 10 == 0:
                print(f"   ...Đã embed {i + 1}/{len(chunks)} chunks")

        # Bước 4: Save to DB (Weaviate)
        if valid_chunks:
            weaviate_client.save_chunks(valid_chunks)
            print(f"🎉 Hoàn tất! Đã lưu {len(valid_chunks)} chunks vào Weaviate.")
        else:
            print("⚠️ Cảnh báo: Không có chunk nào được tạo vector thành công.")
            
    except Exception as e:
        print(f"❌ LỖI NGHIÊM TRỌNG khi xử lý file {file_path}: {e}")
        import traceback
        traceback.print_exc()

# --- 5. API Endpoints ---
@app.post("/index-upload")
async def index_upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Nhận file PDF upload lên, lưu tạm và đẩy vào hàng đợi xử lý ngầm.
    """
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Lưu file ra ổ cứng
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Đẩy task vào background
        background_tasks.add_task(process_file_background, file_location)
        
        return {
            "message": "File received successfully. Indexing started in background.", 
            "filename": file.filename,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

@app.get("/health")
def health_check():
    return {
        "status": "active", 
        "service": "indexing-service",
        "configs": {
            "embedding_url": EMBEDDING_API_URL,
            "weaviate_url": WEAVIATE_URL
        }
    }