# Sử dụng chung Base Image
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Chỉ định HuggingFace đọc model từ thư mục này
    HF_HOME=/app/models

WORKDIR /app

# 1. Cài đặt thư viện trước (ít thay đổi)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. COPY MODEL VÀO (Model nằm trong folder 'models' cùng cấp với Dockerfile)
# Copy vào folder /app/models bên trong container
COPY models/ /app/models/

# 3. Copy Code
COPY src/ ./src/

# 4. Thiết lập User và Quyền (Quan trọng nhất)
# Tạo user -> Chuyển toàn bộ quyền sở hữu /app (bao gồm code và models) cho appuser
RUN groupadd -r appgroup && useradd -r -g appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]