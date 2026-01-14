import requests
import logging

# Tạo logger để ghi log chuẩn thay vì print
logger = logging.getLogger(__name__)

class EmbeddingClient:
    # 1. Đổi tên tham số từ api_url thành base_url để khớp với main.py
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
        """Gọi API batch theo từng cụm nhỏ để tránh block service quá lâu"""
        if not texts:
            return []
            
        all_embeddings = []
        batch_size = 32 # Chia nhỏ batch để interleaving với các request khác (như từ Chat)
        
        # Xử lý URL: chuyển http://.../embed -> http://.../embed/batch
        batch_url = self.base_url.rstrip("/") + "/batch"
        
        for i in range(0, len(texts), batch_size):
            current_batch = texts[i : i + batch_size]
            try:
                # logger.info(f"Sending sub-batch {i//batch_size + 1} ({len(current_batch)} texts)")
                response = requests.post(
                    batch_url, 
                    json={"texts": current_batch},
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                all_embeddings.extend(data.get("embeddings", []))
            except Exception as e:
                logger.error(f"Error calling Sub-Batch Embedding API: {e}")
                # Pipeline chính mong muốn độ dài khớp, nên tốt nhất là raise
                raise e
                
        return all_embeddings