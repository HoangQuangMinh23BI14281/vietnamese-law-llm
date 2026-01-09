import requests
import logging
from typing import List
from src.domain.ports import EmbeddingPort

logger = logging.getLogger(__name__)

class HttpEmbeddingAdapter(EmbeddingPort):
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_embedding(self, text: str) -> List[float]:
        try:
            res = requests.post(self.api_url, json={"text": text}, timeout=10)
            if res.status_code == 200:
                return res.json()["embedding"]
            logger.error(f"Embedding API failed: {res.status_code}")
            return []
        except Exception as e:
            logger.error(f"Embedding Connection Error: {e}")
            return []