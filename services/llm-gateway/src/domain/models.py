from pydantic import BaseModel
from typing import List, Optional

# Entity đại diện cho tài liệu tìm được
class RetrievedDocument(BaseModel):
    title: str
    content: str
    score: float = 0.0

# Input từ người dùng
class ChatQuery(BaseModel):
    query: str

# Output trả về cho người dùng
class ChatResponse(BaseModel):
    answer: str
    sources: List[str]