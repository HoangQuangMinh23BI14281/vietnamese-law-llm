FROM python:3.9-slim

WORKDIR /app

# 1. Cài đặt dependencies trước (để tận dụng Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tạo thư mục model
RUN mkdir -p /app/models

# 2. Copy toàn bộ code vào container
COPY src/ ./src/

# [QUAN TRỌNG] Giúp Python tìm thấy module 'src'
ENV PYTHONPATH=/app

# 3. Chạy app
# Lưu ý: --host 0.0.0.0 là bắt buộc để truy cập từ bên ngoài container
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]