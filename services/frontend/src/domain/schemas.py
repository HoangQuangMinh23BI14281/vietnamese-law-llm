from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []

class UploadStatus(BaseModel):
    success: bool
    message: str
    filename: str