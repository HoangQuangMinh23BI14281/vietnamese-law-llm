from src.infrastructure.gateway_api import GatewayAPI
from src.domain.schemas import ChatResponse

class ChatService:
    def __init__(self, api: GatewayAPI):
        self.api = api

    def send_message(self, query: str) -> str:
        # Gọi API
        response = self.api.chat(query)
        
        # Logic nghiệp vụ: Format câu trả lời để hiển thị đẹp
        formatted_text = response.answer
        if response.sources:
            formatted_text += "\n\n---\n**📚 Nguồn tham khảo:**\n"
            for src in response.sources:
                formatted_text += f"- {src}\n"
        
        return formatted_text