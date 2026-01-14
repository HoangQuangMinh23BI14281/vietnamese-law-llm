from abc import ABC, abstractmethod
from typing import List
from .models import RetrievedDocument

# Port cho Embedding Service
class EmbeddingPort(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass

# Port cho Vector Database (Weaviate)
class VectorDBPort(ABC):
    @abstractmethod
    def search(self, query_text: str, vector: List[float], limit: int = 10) -> List[RetrievedDocument]:
        pass

# Port cho LLM (Groq)
class LLMPort(ABC):
    @abstractmethod
    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        pass

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        pass

