# src/application/chat_service.py
from typing import List, Optional
import logging
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.domain.models import ChatQuery, ChatResponse, RetrievedDocument
from src.domain.ports import EmbeddingPort, VectorDBPort, LLMPort

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, embedder: EmbeddingPort, vector_db: VectorDBPort, llm: LLMPort):
        self.embedder = embedder
        self.vector_db = vector_db
        self.llm = llm
        
        self.executor = ThreadPoolExecutor(max_workers=5) # Thread pool cho blocking calls

        self.article_pattern = re.compile(
            r"\b(?:điều|khoản)\s+(\d+)\b(?!\s*(?:năm|tháng|ngày|giờ|phút|triệu|tỷ|nghìn|trăm|đồng|vnd|usd))", 
            re.IGNORECASE
        )
        


    async def process_question(self, req: ChatQuery) -> ChatResponse:
        logger.info(f" [Async Service] Câu hỏi: {req.query}")
        


        # --- BƯỚC 1: PARALLEL RETRIEVAL ---
        docs = await self._parallel_retrieval(req.query)

        # --- BƯỚC 2: GRADING (CHẤM ĐIỂM) ---
        is_relevant = False
        if docs:
            is_relevant = await self._grade_documents(req.query, docs)
        
        # --- BƯỚC 3: CORRECTIVE ACTIONS (SỬA SAI) & FALLBACK ---
        if not is_relevant:
            logger.warning(f" [Correction] Documents not relevant.")
            
            # HyDE (Nếu không phải tin tức, thử HyDE trước)
            logger.info(" Kích hoạt HyDE...")
            hyde_docs = await self._run_hyde_search(req.query)
            
            if await self._grade_documents(req.query, hyde_docs):
                docs = hyde_docs
            else:
                # Nếu HyDE cũng fail -> Trả về không tìm thấy
                logger.info(" HyDE failed -> No results found.")
                return ChatResponse(answer="Xin lỗi, tôi không tìm thấy thông tin phù hợp trong cơ sở dữ liệu luật.", sources=[])

        # --- BƯỚC 4: FINAL GENERATION ---
        return await self._generate_final_response(req.query, docs)

    # ==========================================
    # INTERNAL ASYNC HELPERS
    # ==========================================



    async def _parallel_retrieval(self, query: str) -> List[RetrievedDocument]:
        LOOP = asyncio.get_running_loop()
        article_match = self.article_pattern.search(query)
        
        tasks = []

        # 1. Semantic Search (Luôn chạy)
        tasks.append(self._run_semantic_search(query))

        # 2. Strict Search (Chảy nếu có Điều khoản)
        if article_match:
            article_num = article_match.group(1)
            target = f"Điều {article_num}"
            logger.info(f" [Parallel] Detected Article: {target}")
            tasks.append(self._run_strict_search(target))

        # Chạy song song
        results = await asyncio.gather(*tasks)
        
        # Gộp kết quả
        all_docs = []
        for r in results:
            all_docs.extend(r)
            
        # Deduplicate (Loại trùng lặp dựa trên title + content)
        unique_docs = {}
        for d in all_docs:
            key = f"{d.title}_{len(d.content)}"
            if key not in unique_docs:
                unique_docs[key] = d
                
        return list(unique_docs.values())

    async def _run_semantic_search(self, query: str):
        LOOP = asyncio.get_running_loop()
        # Non-blocking embedding
        vector = await LOOP.run_in_executor(self.executor, self.embedder.get_embedding, query)
        
        # Non-blocking vector search
        return await LOOP.run_in_executor(
            self.executor, 
            lambda: self.vector_db.search(query_text=query, vector=vector, limit=8, alpha=0.5)
        )

    async def _run_strict_search(self, target: str):
        LOOP = asyncio.get_running_loop()
        vector = await LOOP.run_in_executor(self.executor, self.embedder.get_embedding, target)
        
        return await LOOP.run_in_executor(
            self.executor,
            lambda: self.vector_db.search(
                query_text=target,
                vector=vector,
                limit=5,
                where_filter={
                    "path": ["article"],
                    "operator": "Equal",
                    "valueString": target
                }
            )
        )



    async def _grade_documents(self, query: str, docs: List[RetrievedDocument]) -> bool:
        if not docs: return False
        LOOP = asyncio.get_running_loop()
        
        top_doc = docs[0].content[:800] # Tăng context lên chút
        sys_prompt = "You are a stricter Relevance Grader. Check if the document contains the answer to the query."
        user_prompt = (
            f"Query: {query}\n"
            f"Doc: {top_doc}\n"
            "Does the document contain enough information to answer the query? "
            "If it only contains related keywords but no answer, reply NO. "
            "Reply strictly YES or NO."
        )
        
        grade = await LOOP.run_in_executor(self.executor, self.llm.generate_answer, sys_prompt, user_prompt)
        logger.info(f" Grader: {grade.strip()}")
        return "YES" in grade.upper()

    async def _run_hyde_search(self, query: str):
        LOOP = asyncio.get_running_loop()
        
        # 1. Gen HyDE Doc
        sys_prompt = "Bạn là chuyên gia luật."
        user_prompt = f"Viết đoạn văn ngắn về: {query}"
        hyde_doc = await LOOP.run_in_executor(self.executor, self.llm.generate_answer, sys_prompt, user_prompt)
        
        # 2. Vector Search HyDE
        vector = await LOOP.run_in_executor(self.executor, self.embedder.get_embedding, hyde_doc)
        return await LOOP.run_in_executor(
            self.executor, 
            lambda: self.vector_db.search(query_text=hyde_doc, vector=vector, limit=8, alpha=0.7)
        )

    async def _generate_final_response(self, query: str, docs: List) -> ChatResponse:
        if not docs:
             return ChatResponse(answer="Xin lỗi, tôi không tìm thấy thông tin phù hợp.", sources=[])

        LOOP = asyncio.get_running_loop()
        context_str = "\n".join([f"- {d.title}: {d.content}" for d in docs])
        sources = list(set([d.title for d in docs]))

        sys_prompt = "Bạn là trợ lý luật sư Việt Nam. Trả lời bằng Tiếng Việt."
        user_prompt = f"TÀI LIỆU:\n{context_str}\n\nCÂU HỎI: {query}\n\nTrả lời chi tiết dựa trên tài liệu:"
        
        answer = await LOOP.run_in_executor(self.executor, self.llm.generate_answer, sys_prompt, user_prompt)
        return ChatResponse(answer=answer, sources=sources)