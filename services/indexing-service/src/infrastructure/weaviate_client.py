import weaviate
import os
from src.domain.models import LegalChunk

class WeaviateClient:
    def __init__(self, url=None):
        self.url = url or os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        self.client = weaviate.Client(
            url=self.url,
            timeout_config=(5, 15)  # Timeout connect/read
        )
        self.class_name = "LegalDocument"
        self._ensure_schema()

    def _ensure_schema(self):
        """Tạo bảng (Class) nếu chưa tồn tại"""
        if not self.client.schema.exists(self.class_name):
            schema = {
                "class": self.class_name,
                "vectorizer": "none", # Quan trọng: báo Weaviate ta tự cung cấp vector
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "chapter", "dataType": ["text"]},
                    {"name": "article", "dataType": ["text"]},
                    {"name": "source", "dataType": ["text"]},
                ]
            }
            self.client.schema.create_class(schema)
            print(f"📦 Created Weaviate schema: {self.class_name}")

    def save_chunks(self, chunks: list[LegalChunk]):
        """Lưu hàng loạt chunk vào DB"""
        print(f"💾 Saving {len(chunks)} chunks to Weaviate...")
        
        with self.client.batch as batch:
            batch.batch_size = 100
            for chunk in chunks:
                if not chunk.embedding:
                    continue # Bỏ qua nếu lỗi embedding
                
                # Metadata + Text
                properties = {
                    "text": chunk.text,
                    "chapter": chunk.metadata.get("chapter", ""),
                    "article": chunk.metadata.get("article", ""),
                    "source": chunk.metadata.get("source", "")
                }
                
                # Add object kèm vector
                batch.add_data_object(
                    data_object=properties,
                    class_name=self.class_name,
                    vector=chunk.embedding  # Vector từ Embedding Service
                )
        print("✅ Saved to Weaviate successfully!")