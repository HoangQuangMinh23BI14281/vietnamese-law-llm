# =============================================================================
# FRONTEND - Streamlit Web Interface
# Port: 8501 | GPU: Not required | Multi-Stage Build
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: Builder - Cài đặt dependencies
# -----------------------------------------------------------------------------
FROM python:3.10-slim AS builder

WORKDIR /build

# Cài đặt dependencies vào virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# STAGE 2: Runtime - Image production gọn nhẹ
# -----------------------------------------------------------------------------
FROM python:3.10-slim AS runtime

# Tối ưu Python runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy virtual environment từ builder
COPY --from=builder /opt/venv /opt/venv

# Copy source code
COPY src/ ./src/

EXPOSE 8501

# Streamlit config: headless mode, disable telemetry
CMD ["streamlit", "run", "src/main.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]