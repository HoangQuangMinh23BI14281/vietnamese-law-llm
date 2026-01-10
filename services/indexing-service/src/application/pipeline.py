import logging
import os
from src.domain.models import ProcessingResult, LegalChunk # Import type

logger = logging.getLogger(__name__)

class IndexingPipeline:
    def __init__(self, loader, chunker, embedder, db):
        self.loader = loader
        self.chunker = chunker
        self.embedder = embedder
        self.db = db

    def run_pipeline(self, file_path: str):
        filename = os.path.basename(file_path)
        logger.info(f" Bắt đầu xử lý file: {filename}")

        try:
            # 1. Load
            raw_text = self.loader.load(file_path)
            if not raw_text:
                raise Exception("File rỗng hoặc không đọc được text")

            # 2. Chunk
            chunks = self.chunker.chunk(raw_text, filename)
            logger.info(f"✂️ Đã cắt thành {len(chunks)} chunks.")

            # 3. Embed & Validate Metadata
            vectors = []
            valid_chunks = []
            
            for chunk in chunks:
                text_content = chunk.text if hasattr(chunk, 'text') else chunk.get('text', '')
                
                # [UPDATE] Kiểm tra nhanh xem Metadata có đúng form không (Debug)
                meta = chunk.metadata if hasattr(chunk, 'metadata') else chunk.get('metadata', {})
                if 'article' in meta and meta['article']:
                     # Log sample 1 lần thôi để debug
                     if len(valid_chunks) == 0: 
                        logger.info(f" Sample Metadata: {meta}")

                try:
                    vec = self.embedder.get_embedding(text_content)
                    
                    if vec and len(vec) > 0:
                        vectors.append(vec)
                        valid_chunks.append(chunk)
                except Exception as e_embed:
                    logger.warning(f" Lỗi embedding chunk text '{text_content[:30]}...': {e_embed}")
                    continue # Bỏ qua chunk lỗi, chạy tiếp chunk sau

            # 4. Save Batch
            if valid_chunks:
                # Hàm save_chunks của DB adapter cần xử lý việc map metadata từ chunk vào Weaviate properties
                self.db.save_chunks(valid_chunks, vectors)
                logger.info(f" Đã lưu thành công {len(valid_chunks)} chunks có metadata vào Weaviate.")
            else:
                logger.warning(" Không có chunk nào hợp lệ để lưu.")

            return ProcessingResult(
                filename=filename,
                status="success",
                total_chunks=len(valid_chunks),
                message="Indexing completed successfully"
            )

        except Exception as e:
            logger.error(f" Lỗi Pipeline Fatal: {str(e)}", exc_info=True)
            return ProcessingResult(
                filename=filename,
                status="error",
                message=str(e),
                total_chunks=0
            )