from sentence_transformers import SentenceTransformer
import torch
import logging
import os
from src.domain.interfaces import IEmbeddingService

logger = logging.getLogger(__name__)

class HuggingFaceEmbeddingAdapter(IEmbeddingService):
    def __init__(self):
        # Lấy tên model từ biến môi trường, default nếu không có
        self.model_name = os.getenv("MODEL_NAME", "huyydangg/DEk21_hcmute_embedding")
        self.model_path = "./models"
        
        # Tự động chọn thiết bị
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"--- ĐANG KHỞI TẠO MODEL: {self.model_name} ---")
        logger.info(f"--- THIẾT BỊ SỬ DỤNG: {self.device.upper()} ---")

        try:
            self.model = SentenceTransformer(
                self.model_name, 
                device=self.device, 
                cache_folder=self.model_path
            )
            logger.info(" Model đã tải thành công.")
        except Exception as e:
            logger.error(f" Lỗi tải model: {str(e)}")
            raise e

    def embed(self, text: str) -> list:
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Xử lý batch nhiều text cùng lúc để tăng tốc độ"""
        if not texts:
            return []
        
        # encode trả về numpy array -> convert to list
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        return embeddings.tolist()

    def get_info(self) -> dict:
        return {
            "model_name": self.model_name,
            "device": self.device,
            "cuda_available": torch.cuda.is_available()
        }