from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class LegalChunk(BaseModel):
    text: str
    metadata: Dict[str, Any]  # Chứa chapter, article, filename...

class ProcessingResult(BaseModel):
    filename: str
    total_chunks: int
    status: str
    message: str