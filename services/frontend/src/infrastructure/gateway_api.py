import requests
from src.domain.schemas import ChatResponse

class GatewayAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def chat(self, query: str) -> ChatResponse:
        try:
            res = requests.post(f"{self.base_url}/chat", json={"query": query}, timeout=300)
            if res.status_code == 200:
                data = res.json()
                return ChatResponse(answer=data.get("answer"), sources=data.get("sources", []))
            return ChatResponse(answer=f" Lỗi Server: {res.status_code}", sources=[])
        except Exception as e:
            return ChatResponse(answer=f" Không thể kết nối AI: {str(e)}", sources=[])