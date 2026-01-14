from src.infrastructure.gateway_api import GatewayAPI
from src.domain.schemas import ChatResponse

class ChatService:
    def __init__(self, api: GatewayAPI):
        self.api = api

    def send_message(self, query: str) -> str:
        response = self.api.chat(query)
        
        formatted_text = response.answer
        if response.sources:
            formatted_text += "\n\n---\n**Nguồn tham khảo:**\n"
            for src in response.sources:
                formatted_text += f"- {src}\n"
        
        return formatted_text

    def is_service_ready(self) -> bool:
        return self.api.check_health()