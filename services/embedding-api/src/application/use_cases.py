from src.domain.interfaces import IEmbeddingService

class CreateEmbeddingUseCase:
    def __init__(self, service: IEmbeddingService):
        # Dependency Injection thông qua Interface
        self.service = service

    def execute(self, text: str) -> dict:
        if not text:
            raise ValueError("Text cannot be empty")
            
        vector = self.service.embed(text)
        
        # Trả về format chuẩn
        return {
            "embedding": vector,
            "dimension": len(vector)
        }

class HealthCheckUseCase:
    def __init__(self, service: IEmbeddingService):
        self.service = service

    def execute(self):
        info = self.service.get_info()
        return {"status": "active", **info}

class BatchEmbeddingUseCase:
    def __init__(self, service: IEmbeddingService):
        self.service = service

    def execute(self, texts: list[str]) -> dict:
        if not texts:
            return {"embeddings": []}
            
        vectors = self.service.embed_batch(texts)
        return {
            "embeddings": vectors,
            "count": len(vectors),
            "dimension": len(vectors[0]) if vectors else 0
        }