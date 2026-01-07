import requests
import os

class EmbeddingClient:
    def __init__(self, api_url=None):
        # Mặc định gọi sang container embedding-api
        self.api_url = api_url or os.getenv("EMBEDDING_API_URL", "http://host.docker.internal:5000/embed")

    def get_embedding(self, text: str) -> list[float]:
        try:
            response = requests.post(
                self.api_url, 
                json={"text": text},
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"❌ Error getting embedding: {e}")
            return []