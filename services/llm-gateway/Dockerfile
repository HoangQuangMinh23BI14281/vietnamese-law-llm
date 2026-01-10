# Sử dụng chung Base Image
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Chỉ định HuggingFace đọc model từ thư mục này
    HF_HOME=/app/models

WORKDIR /app

# 1. Cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. COPY MODEL QWEN VÀO
# Giả sử bạn để model Qwen trong thư mục 'models' tại thư mục build context
COPY models/ /app/models/

# 3. Copy Code
COPY src/ ./src/

# 4. Thiết lập User và Quyền
RUN groupadd -r appgroup && useradd -r -g appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]