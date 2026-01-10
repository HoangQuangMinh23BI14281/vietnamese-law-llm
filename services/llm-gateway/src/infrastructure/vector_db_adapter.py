import weaviate
import logging
from typing import List, Optional, Dict, Any
from src.domain.ports import VectorDBPort
from src.domain.models import RetrievedDocument

logger = logging.getLogger(__name__)

class WeaviateAdapter(VectorDBPort):
    def __init__(self, url: str, class_name: str = "LegalDocument"):
        self.url = url
        self.class_name = class_name
        logger.info(f" Connecting to Weaviate at: {self.url}")
        self.client = weaviate.Client(url)

    def search(
        self, 
        query_text: str, 
        vector: List[float], 
        limit: int = 10,
        alpha: float = 0.5, 
        properties: Optional[List[str]] = None, 
        where_filter: Optional[Dict[str, Any]] = None
    ):
        if not vector:
            logger.warning(" Vector rỗng, bỏ qua search.")
            return []
        
        if properties is None:
            properties = ["text", "source", "article^3", "chapter"] 

        try:
            logger.info(f" Querying Weaviate: '{query_text}' (Alpha={alpha}) | Filter: {where_filter is not None}")
            
            # Khởi tạo query object
            query_obj = (
                self.client.query
                .get(self.class_name, ["text", "source", "article", "chapter"])
                .with_hybrid(
                    query=query_text,
                    vector=vector,
                    alpha=alpha,            
                    properties=properties,
                )
            )

            if where_filter:
                query_obj = query_obj.with_where(where_filter)

            # Thực thi query
            response = (
                query_obj
                .with_additional(["score"])
                .with_limit(limit)
                .do()
            )
            
            raw_data = response.get('data', {}).get('Get', {}).get(self.class_name, [])
            
            # LOG DEBUG
            logger.info(f" Found {len(raw_data)} raw results.")
            for i, item in enumerate(raw_data):
                raw_score = item.get('_additional', {}).get('score', 0)
                try:
                    score_val = float(raw_score)
                except (ValueError, TypeError):
                    score_val = 0.0
                
                art = item.get('article', 'N/A')
                logger.info(f"   [{i}] Score: {score_val:.4f} | Article: {art} | Source: {item.get('source')}")

            results = []
            for item in raw_data:
                chap = item.get('chapter') or ""
                art = item.get('article') or ""
                txt = item.get('text') or ""

                full_content = f"Chương: {chap}\nĐiều: {art}\nNội dung: {txt}"
                
                results.append(RetrievedDocument(
                    title=item.get("source", "Tài liệu pháp luật"), 
                    content=full_content 
                ))
            
            return results

        except Exception as e:
            logger.error(f" Weaviate Error: {e}")
            return []