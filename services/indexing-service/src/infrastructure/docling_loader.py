import os
from docling.document_converter import DocumentConverter

class DoclingLoader:
    def load_to_markdown(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
        
        print(f"🚀 Docling processing: {pdf_path}")
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document.export_to_markdown()