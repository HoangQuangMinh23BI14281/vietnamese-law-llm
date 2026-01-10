FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/models

WORKDIR /app

# Cài đặt thư viện trước để tận dụng cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CHỈ copy code, KHÔNG copy models
COPY src/ ./src/

# Thiết lập User (Sử dụng UID 1000 để khớp với đại đa số user WSL2/Linux)
RUN groupadd -r appgroup && useradd -r -u 1000 -g appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8001
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]