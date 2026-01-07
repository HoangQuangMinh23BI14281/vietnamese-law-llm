from abc import ABC, abstractmethod
from typing import List

# Interface (Port): Định nghĩa "Hành động" mà hệ thống cần làm
# Service này không quan tâm ta dùng HuggingFace, OpenAI hay TensorFlow.
class IEmbeddingService(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def get_info(self) -> dict:
        pass