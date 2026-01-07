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