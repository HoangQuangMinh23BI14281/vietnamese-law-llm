# ==========================================
# Stage 1: Builder (Dùng để cài đặt thư viện)
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Cài đặt các công cụ build cần thiết (như gcc) phòng trường hợp
# có thư viện nào cần compile. Sau stage này sẽ vứt bỏ nên không sợ nặng.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Tạo virtual environment tại /opt/venv
RUN python -m venv /opt/venv
# Kích hoạt venv
ENV PATH="/opt/venv/bin:$PATH"

# Cài đặt dependencies vào venv
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runner (Ảnh thật sự để chạy)
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH"

# Cài đặt curl (cần thiết cho HEALTHCHECK) vì bản slim không có sẵn
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Tạo user non-root để bảo mật
RUN addgroup --system appgroup && adduser --system --group appuser

# --- COPY TỪ BUILDER ---
# Chỉ lấy thư mục venv đã cài sẵn thư viện
COPY --from=builder /opt/venv /opt/venv

# Copy source code
COPY src/ ./src/

# Cấp quyền cho user mới
RUN chown -R appuser:appgroup /app

# Chuyển sang user non-root
USER appuser

EXPOSE 8501

# Healthcheck để Kubernetes/Docker biết app còn sống hay chết
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]