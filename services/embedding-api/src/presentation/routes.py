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
    import logging
    logger = logging.getLogger("embedding-api")
    logger.info("Received single embedding request")
    try:
        create_use_case = use_cases["create"]
        result = create_use_case.execute(request.text)
        logger.info("Completed single embedding request")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in single embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embed/batch")
def create_batch_embedding(request: BatchTextRequest, use_cases = Depends(get_use_cases)):
    """Endpoint xử lý nhiều text cùng lúc"""
    import logging
    logger = logging.getLogger("embedding-api")
    logger.info(f"Received batch embedding request: {len(request.texts)} texts")
    try:
        batch_use_case = use_cases["batch"]
        result = batch_use_case.execute(request.texts)
        logger.info(f"Completed batch embedding request: {len(request.texts)} texts")
        return result
    except Exception as e:
        logger.error(f"Error in batch embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def health_check(use_cases = Depends(get_use_cases)):
    return use_cases["health"].execute()

@router.get("/health")
def simple_health():
    return {"status": "ok"}