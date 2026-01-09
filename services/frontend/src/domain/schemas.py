from pydantic import BaseModel
from typing import List, Optional

# Model cho Chat
class Message(BaseModel):
    role: str  # user | assistant
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []

# Model cho Upload
class UploadStatus(BaseModel):
    success: bool
    message: str
    filename: str