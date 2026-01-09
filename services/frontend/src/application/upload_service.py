from src.infrastructure.indexing_api import IndexingAPI
from src.domain.schemas import UploadStatus

class UploadService:
    def __init__(self, api: IndexingAPI):
        self.api = api

    def process_upload(self, file) -> UploadStatus:
        if not file:
            return UploadStatus(success=False, message="Chưa chọn file", filename="")
        
        # Logic nghiệp vụ: Có thể thêm check dung lượng file ở đây nếu muốn
        if file.size > 50 * 1024 * 1024: # Ví dụ 50MB
             return UploadStatus(success=False, message="File quá lớn (>50MB)", filename=file.name)

        return self.api.upload_pdf(file.name, file.getvalue())