import requests
import logging

# Tạo logger để ghi log chuẩn thay vì print
logger = logging.getLogger(__name__)

class EmbeddingClient:
    # 1. Đổi tên tham số từ api_url thành base_url để khớp với main.py
    # 2. Bỏ os.getenv ở đây, vì main.py đã lo việc đó rồi
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_embedding(self, text: str) -> list[float]:
        try:
            response = requests.post(
                self.base_url, 
                json={"text": text},
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Embedding API at {self.base_url}: {e}")
            return []
        except KeyError:
            logger.error(f"API response format invalid")
            return []

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Gọi API batch để lấy nhiều vector cùng lúc"""
        try:
            # Endpoint giả định là /embed/batch (cần cấu hình URL phù hợp, 
            # hoặc tự động detect nếu base_url kết thúc bằng /embed)
            
            # Xử lý URL: chuyển http://.../embed -> http://.../embed/batch
            batch_url = self.base_url.rstrip("/") + "/batch"
            
            response = requests.post(
                batch_url, 
                json={"texts": texts},
                timeout=60 # Batch lâu hơn đơn lẻ nên tăng timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("embeddings", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Batch Embedding API: {e}")
            return []