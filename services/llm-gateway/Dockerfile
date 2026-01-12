# =============================================================================
# LLM GATEWAY - RAG Query Service with Qwen/LLM
# Port: 8001 | GPU: Required | Multi-Stage Build
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: Builder - Cài đặt dependencies
# -----------------------------------------------------------------------------
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime AS builder

WORKDIR /build

# Cài đặt dependencies vào virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# STAGE 2: Runtime - Image production gọn nhẹ
# -----------------------------------------------------------------------------
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime AS runtime

# Tối ưu Python runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/model_cache \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy virtual environment từ builder
COPY --from=builder /opt/venv /opt/venv

# Tạo thư mục cho model cache (mount từ docker-compose)
RUN mkdir -p /app/model_cache

# Copy source code
COPY src/ ./src/

EXPOSE 8001

# Hot-reload enabled cho development
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--reload-dir", "/app/src"]