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
            # Gửi request
            response = requests.post(
                self.base_url, 
                json={"text": text},
                timeout=30
            )
            response.raise_for_status()
            
            # Trả về kết quả
            return response.json()["embedding"]
            
        except requests.exceptions.RequestException as e:
            # Dùng logger.error thay vì print để dễ debug trong Docker
            logger.error(f"Error calling Embedding API at {self.base_url}: {e}")
            return []
        except KeyError:
            logger.error(f"API response format invalid (missing 'embedding' key)")
            return []