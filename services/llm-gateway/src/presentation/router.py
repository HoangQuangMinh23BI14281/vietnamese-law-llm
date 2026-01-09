import logging
from fastapi import APIRouter, HTTPException
from src.domain.models import ChatQuery, ChatResponse
from src.application.chat_service import ChatService

# Tạo Router
router = APIRouter()

# Biến global để hứng Service được inject từ main
chat_service_instance: ChatService = None

def set_chat_service(service: ChatService):
    """Hàm này giúp Main.py 'bơm' logic vào router"""
    global chat_service_instance
    chat_service_instance = service

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatQuery):
    if not chat_service_instance:
        raise HTTPException(status_code=500, detail="Service not initialized")
        
    try:
        # Presentation chỉ chuyển lời gọi vào Application Layer
        response = chat_service_instance.process_question(req)
        return response
    except Exception as e:
        logging.error(f"System Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")