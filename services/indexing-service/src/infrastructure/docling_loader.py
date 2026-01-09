import logging
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)

class DoclingLoader:
    def __init__(self):
        # Khởi tạo converter của Docling
        self.converter = DocumentConverter()

    def load(self, file_path: str) -> str:
        """
        Đọc file PDF/Word và trả về Markdown text
        """
        try:
            logger.info(f"📄 Đang đọc file bằng Docling: {file_path}")
            conv_result = self.converter.convert(file_path)
            # Xuất ra markdown
            return conv_result.document.export_to_markdown()
        except Exception as e:
            logger.error(f"❌ Docling lỗi đọc file: {e}")
            return ""