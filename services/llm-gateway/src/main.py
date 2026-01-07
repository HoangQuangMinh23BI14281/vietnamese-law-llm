from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
import requests
import weaviate
import logging

# --- CONFIG ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLM-Gateway")

app = FastAPI(title="Vietnamese Law LLM Gateway")

# Env Vars
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://embedding-api:5000/embed")

# Init Clients
weaviate_client = weaviate.Client(WEAVIATE_URL)
groq_client = Groq(api_key=GROQ_API_KEY)

class ChatRequest(BaseModel):
    query: str

# Hàm gọi Embedding API
def get_embedding(text):
    try:
        res = requests.post(EMBEDDING_API_URL, json={"text": text}, timeout=10)
        return res.json()["embedding"] if res.status_code == 200 else None
    except Exception as e:
        logger.error(f"Embedding Error: {e}")
        return None

# Hàm tìm kiếm trong Weaviate
def search_vector(query_text, limit=4):
    vector = get_embedding(query_text)
    if not vector: return []
    
    try:
        response = (
            weaviate_client.query
            .get("LegalDocument", ["title", "content"])
            .with_near_vector({"vector": vector})
            .with_limit(limit)
            .do()
        )
        return response.get('data', {}).get('Get', {}).get('LegalDocument', [])
    except Exception as e:
        logger.error(f"Vector Search Error: {e}")
        return []

# --- MAIN CHAT ENDPOINT ---
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    logger.info(f"📩 Nhận câu hỏi: {req.query}")
    
    # 1. Tìm kiếm thông tin liên quan (RAG)
    docs = search_vector(req.query)
    
    # 2. Xây dựng context
    context_str = ""
    sources = []
    if docs:
        context_str += "\n--- THÔNG TIN PHÁP LUẬT THAM KHẢO ---\n"
        for i, d in enumerate(docs, 1):
            context_str += f"[{i}] {d.get('title')}: {d.get('content')}\n"
            sources.append(d.get('title'))
    else:
        context_str = "Không tìm thấy văn bản luật cụ thể trong cơ sở dữ liệu."

    # 3. Tạo Prompt cho LLM
    system_prompt = """Bạn là trợ lý pháp luật Việt Nam. 
    Nhiệm vụ của bạn là trả lời câu hỏi dựa trên thông tin tham khảo được cung cấp.
    Nếu thông tin không đủ, hãy nói rõ là bạn không biết chắc chắn, đừng bịa đặt điều luật."""
    
    user_prompt = f"Câu hỏi: {req.query}\n\n{context_str}"

    # 4. Gọi Groq LLM
    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        answer = completion.choices[0].message.content
        return {"answer": answer, "sources": list(set(sources))}
        
    except Exception as e:
        logger.error(f"Groq Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))