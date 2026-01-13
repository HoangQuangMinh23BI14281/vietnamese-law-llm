from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from src.application.use_cases import CreateEmbeddingUseCase, HealthCheckUseCase, BatchEmbeddingUseCase

# DTO (Data Transfer Object)
class TextRequest(BaseModel):
    text: str

class BatchTextRequest(BaseModel):
    texts: List[str]

router = APIRouter()

# Dependency Injection helper (sẽ được override ở main.py)
def get_use_cases():
    raise NotImplementedError

@router.post("/embed")
def create_embedding(request: TextRequest, use_cases = Depends(get_use_cases)):
    try:
        # Lấy UseCase từ dependency
        create_use_case = use_cases["create"]
        return create_use_case.execute(request.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embed/batch")
def create_batch_embedding(request: BatchTextRequest, use_cases = Depends(get_use_cases)):
    """Endpoint xử lý nhiều text cùng lúc"""
    try:
        batch_use_case = use_cases["batch"]
        return batch_use_case.execute(request.texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def health_check(use_cases = Depends(get_use_cases)):
    return use_cases["health"].execute()

@router.get("/health")
def simple_health():
    return {"status": "ok"}