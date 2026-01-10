# src/application/chat_service.py
from typing import List, Optional
import logging
import re
from src.domain.models import ChatQuery, ChatResponse, RetrievedDocument
from src.domain.ports import EmbeddingPort, VectorDBPort, LLMPort

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, embedder: EmbeddingPort, vector_db: VectorDBPort, llm: LLMPort):
        self.embedder = embedder
        self.vector_db = vector_db
        self.llm = llm
        
        self.article_pattern = re.compile(
            r"\b(?:điều|khoản)\s+(\d+)\b(?!\s*(?:năm|tháng|ngày|giờ|phút|triệu|tỷ|nghìn|trăm|đồng|vnd|usd))", 
            re.IGNORECASE
        )

    def process_question(self, req: ChatQuery) -> ChatResponse:
        logger.info(f"🚀 [CRAG Start] Câu hỏi: {req.query}")
        
        # --- BƯỚC 1: ROUTING & INITIAL RETRIEVAL ---
        article_match = self.article_pattern.search(req.query)
        docs = []
        search_mode = "semantic"
        
        if article_match:
            # CASE A: Tìm chính xác
            article_num = article_match.group(1)
            target = f"Điều {article_num}"
            logger.info(f" Phát hiện ý định tìm cụ thể: {target}")
            
            docs = self.vector_db.search(
                query_text=target,
                vector=self.embedder.get_embedding(target),
                limit=5,
                where_filter={
                    "path": ["article"],
                    "operator": "Equal",
                    "valueString": target
                }
            )
            search_mode = "strict"
        else:
            # CASE B: Tìm ngữ nghĩa
            logger.info(" Tìm kiếm ngữ nghĩa rộng (Broad Search)...")
            docs = self.vector_db.search(
                query_text=req.query,
                vector=self.embedder.get_embedding(req.query),
                limit=8,
                alpha=0.5
            )

        # --- BƯỚC 2: GRADING (CHẤM ĐIỂM) ---
        is_relevant = self._grade_documents(req.query, docs, search_mode)
        
        # --- BƯỚC 3: CORRECTIVE ACTIONS (SỬA SAI) ---
        if not is_relevant:
            logger.warning(f" [Correction] Kết quả từ chế độ '{search_mode}' KHÔNG TỐT.")
            
            if search_mode == "strict":
                logger.info(" Chuyển sang Broad Search (Bỏ filter Điều)...")
                docs = self.vector_db.search(
                    query_text=req.query,
                    vector=self.embedder.get_embedding(req.query),
                    limit=8,
                    alpha=0.5
                )
                if not self._grade_documents(req.query, docs, "semantic"):
                    logger.info(" Broad Search vẫn chưa tốt -> Kích hoạt HyDE...")
                    docs = self._run_hyde_search(req.query)
            else:
                logger.info(" Semantic Search thất bại -> Kích hoạt HyDE...")
                docs = self._run_hyde_search(req.query)

        # --- BƯỚC 4: FINAL GENERATION ---
        return self._generate_final_response(req.query, docs)

    # ==========================================
    # CÁC HÀM PHỤ TRỢ (HELPER METHODS)
    # ==========================================

    def _grade_documents(self, query: str, docs: List, mode: str) -> bool:
        if not docs: 
            return False
            
        top_doc = docs[0].content[:500]
        
        # Prompt chấm điểm (Không cần sửa nhiều, chỉ cần YES/NO)
        sys_prompt = "You are a Relevance Grader. Output only YES or NO."
        
        prompt_logic = ""
        if mode == "strict":
            prompt_logic = "If the query is about time duration (e.g., '5 years') but the document is a Law Article 'Article 5', output NO."
        
        user_prompt = f"""
        Query: "{query}"
        Document: "{top_doc}..."
        
        {prompt_logic}
        
        Does the document help answer the query? 
        Answer exclusively with: YES or NO.
        """
        
        try:
            grade = self.llm.generate_answer(sys_prompt, user_prompt).strip().upper()
            logger.info(f" Grader ({mode}): {grade}")
            return "YES" in grade
        except:
            return True

    def _run_hyde_search(self, query: str):
        hyde_doc = self._generate_hyde_doc(query)
        logger.info(f" HyDE Document generated: {hyde_doc[:50]}...")
        hyde_vector = self.embedder.get_embedding(hyde_doc)
        return self.vector_db.search(
            query_text=hyde_doc,
            vector=hyde_vector,
            limit=10,
            alpha=0.7
        )

    def _generate_hyde_doc(self, query: str) -> str:
        # Prompt giả định
        sys_prompt = "Bạn là chuyên gia luật Việt Nam."
        user_prompt = f"Viết một đoạn văn ngắn giả định (bằng tiếng Việt) có chứa câu trả lời cho câu hỏi: {query}"
        return self.llm.generate_answer(sys_prompt, user_prompt)

    def _generate_final_response(self, query: str, docs: List) -> ChatResponse:
        if not docs:
            return ChatResponse(answer="Xin lỗi, tôi không tìm thấy thông tin pháp lý liên quan trong cơ sở dữ liệu.", sources=[])
            
        # Tạo context string gọn gàng hơn
        context_str = "\n".join([f"- {d.title}: {d.content}" for d in docs])
        sources = list(set([d.title for d in docs]))
        
        sys_prompt = "Bạn là trợ lý luật sư Việt Nam. Nhiệm vụ duy nhất của bạn là trả lời bằng Tiếng Việt."
        
        # Nhét yêu cầu Tiếng Việt xuống cuối cùng (Recency Bias - Model nhớ cái cuối tốt hơn)
        user_prompt = f"""
        TÀI LIỆU THAM KHẢO:
        {context_str}
        
        CÂU HỎI: "{query}"
        
        YÊU CẦU NGHIÊM NGẶT:
        1. Dựa vào tài liệu trên để trả lời.
        2. Sau khi suy nghĩ xong, CÂU TRẢ LỜI CUỐI CÙNG PHẢI VIẾT BẰNG TIẾNG VIỆT.
        3. Không được viết tiếng Anh ở kết quả cuối cùng.
        
        HÃY TRẢ LỜI BẰNG TIẾNG VIỆT NGAY DƯỚI ĐÂY:
        """
        
        # Gọi model
        answer = self.llm.generate_answer(sys_prompt, user_prompt)
        return ChatResponse(answer=answer, sources=sources)