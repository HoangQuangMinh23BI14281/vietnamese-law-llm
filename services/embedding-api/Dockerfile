FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/models

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Chỉ copy code
COPY src/ ./src/

RUN groupadd -r appgroup && useradd -r -u 1000 -g appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]