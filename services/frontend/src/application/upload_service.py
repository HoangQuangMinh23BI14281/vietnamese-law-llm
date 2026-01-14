from src.infrastructure.indexing_api import IndexingAPI
from src.domain.schemas import UploadStatus

class UploadService:
    def __init__(self, api: IndexingAPI):
        self.api = api

    def process_upload(self, file) -> UploadStatus:
        if not file:
            return UploadStatus(success=False, message="Chưa chọn file", filename="")
        
        if file.size > 50 * 1024 * 1024:
             return UploadStatus(success=False, message="File quá lớn (>50MB)", filename=file.name)

        return self.api.upload_pdf(file.name, file.getvalue())

    def is_service_ready(self) -> bool:
        return self.api.check_health()