FROM python:3.10-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim AS runtime

# Tối ưu Python runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Cài runtime dependencies (chỉ những gì cần chạy, không cần build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment từ builder
COPY --from=builder /opt/venv /opt/venv

# Tạo thư mục uploads
RUN mkdir -p /app/data/uploads

# Copy source code
COPY src/ ./src/

EXPOSE 5001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5001"]