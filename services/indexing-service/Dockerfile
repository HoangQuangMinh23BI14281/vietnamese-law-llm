# ==========================================
# Stage 1: Builder (Cài đặt và Biên dịch)
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# 1. Cài gcc và công cụ build (Bắt buộc để build tree-sitter)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 2. Tạo Virtual Environment (Venv)
RUN python -m venv /opt/venv
# Kích hoạt Venv cho các lệnh bên dưới
ENV PATH="/opt/venv/bin:$PATH"

# 3. Cài đặt thư viện TRỰC TIẾP vào venv
# Vì đang ở Stage 1 có 'build-essential', việc biên dịch tree-sitter sẽ thành công tại đây.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runner (Chạy ứng dụng)
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# 1. Cài các thư viện hệ thống RUNTIME (Chỉ những thứ cần để CHẠY, không cần gcc)
# Ví dụ: libgl1 cho cv2, v.v.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH"

# 3. COPY TOÀN BỘ VENV TỪ BUILDER SANG
# Đây là bước quan trọng: Copy thư viện đã biên dịch xong sang
COPY --from=builder /opt/venv /opt/venv

# 4. Copy source code
COPY src/ ./src/

# 5. Tạo user non-root & thư mục data (như cũ)
RUN addgroup --system appgroup && adduser --system --group appuser && \
    mkdir -p /app/data/uploads && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5001"]