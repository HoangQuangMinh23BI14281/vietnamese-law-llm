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

            # 3. Embed & Validate Metadata (BATCH PROCESSING)
            vectors = []
            valid_chunks = []
            
            # Chuẩn bị list texts
            texts_to_embed = []
            chunks_to_embed = []
            
            for chunk in chunks:
                text_content = chunk.text if hasattr(chunk, 'text') else chunk.get('text', '')
                if text_content and len(text_content.strip()) > 0:
                    texts_to_embed.append(text_content)
                    chunks_to_embed.append(chunk)

            if texts_to_embed:
                logger.info(f"🚀 Đang gửi {len(texts_to_embed)} chunks tới Embedding Service (Batch Mode)...")
                try:
                    # Gọi Batch API 1 lần duy nhất
                    batch_vectors = self.embedder.get_embeddings_batch(texts_to_embed)
                    
                    if len(batch_vectors) == len(chunks_to_embed):
                        vectors = batch_vectors
                        valid_chunks = chunks_to_embed
                        logger.info(f"✅ Đã nhận được {len(vectors)} vectors.")
                    else:
                        logger.error(f"❌ Lỗi: Số lượng vector trả về ({len(batch_vectors)}) không khớp số lượng chunk ({len(chunks_to_embed)})")
                
                except Exception as e:
                    logger.error(f"❌ Lỗi Batch Embedding: {e}")

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