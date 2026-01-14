import requests
from src.domain.schemas import UploadStatus

class IndexingAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def upload_pdf(self, filename: str, file_bytes: bytes) -> UploadStatus:
        try:
            files = {"file": (filename, file_bytes, "application/pdf")}
            res = requests.post(f"{self.base_url}/index-upload", files=files, timeout=600)
            
            if res.status_code == 200:
                data = res.json()
                return UploadStatus(success=True, message=data.get("message", "Xử lý thành công!"), filename=filename)
            return UploadStatus(success=False, message=f"Lỗi Server: {res.text}", filename=filename)
        except Exception as e:
            return UploadStatus(success=False, message=f"Lỗi kết nối: {str(e)}", filename=filename)

    def check_health(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/health", timeout=2)
            return res.status_code == 200 and res.json().get("status") == "ready"
        except:
            return False