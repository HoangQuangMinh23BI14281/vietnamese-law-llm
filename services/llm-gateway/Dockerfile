# =============================================================================
# LLM GATEWAY - RAG Query Service with Qwen/LLM
# Port: 8001 | GPU: Required | Optimized Single-Stage
# =============================================================================

# Sử dụng base image PyTorch (đã có sẵn PyTorch + CUDA)
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

# Tối ưu Python runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/model_cache

WORKDIR /app

# Cài đặt dependencies TRỰC TIẾP vào system python
# Việc này tránh cài đặt lại PyTorch vào trong venv, giúp giảm ~5GB+ dung lượng image
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Tạo thư mục cho model cache
RUN mkdir -p /app/model_cache

# Copy source code
COPY src/ ./src/

EXPOSE 8001

# Hot-reload enabled cho development
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--reload-dir", "/app/src"]