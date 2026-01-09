import weaviate
import logging

logger = logging.getLogger(__name__)

class WeaviateClient:
    def __init__(self, url: str, class_name: str = "LegalDocument"):
        self.url = url
        self.class_name = class_name
        
        # Khởi tạo Client (V3)
        logger.info(f"🔌 Connecting to Weaviate at: {self.url}")
        self.client = weaviate.Client(
            url=self.url,
            timeout_config=(5, 15)
        )
        
        self._create_schema_if_not_exists()

    def _create_schema_if_not_exists(self):
        """
        Đảm bảo Schema trong code giống với Schema thực tế trong DB
        """
        if not self.client.schema.exists(self.class_name):
            schema = {
                "class": self.class_name,
                "vectorizer": "none", 
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "source", "dataType": ["text"]},
                    {"name": "chunk_id", "dataType": ["int"]},
                    {"name": "chapter", "dataType": ["text"]}
                ]
            }
            self.client.schema.create_class(schema)

    def save_chunks(self, chunks: list, vectors: list):
        try:
            # Dùng Batch context manager để import nhanh
            with self.client.batch as batch:
                batch.batch_size = 100
                
                for i, chunk in enumerate(chunks):
                    # Xử lý lấy text và metadata an toàn
                    text_content = chunk.text if hasattr(chunk, 'text') else chunk.get('text', '')
                    
                    # Lấy metadata
                    if hasattr(chunk, 'metadata'):
                        metadata = chunk.metadata
                    else:
                        metadata = chunk.get('metadata', {})

                    # 👇 [UPDATE 2] QUAN TRỌNG NHẤT: Mapping dữ liệu vào DB
                    properties = {
                        "text": text_content,
                        "source": metadata.get("source", metadata.get("filename", "unknown")),
                        "chunk_id": i,
                        "article": metadata.get("article", ""), # Lấy "Điều 34"
                        "chapter": metadata.get("chapter", "")  # Lấy chương
                    }
                    
                    # Thêm vào batch kèm vector
                    batch.add_data_object(
                        data_object=properties,
                        class_name=self.class_name,
                        vector=vectors[i]  
                    )
                    
            logger.info(f"💾 Saved {len(chunks)} chunks to Weaviate.")
            
        except Exception as e:
            logger.error(f"❌ Weaviate Save Error: {e}")
            raise e