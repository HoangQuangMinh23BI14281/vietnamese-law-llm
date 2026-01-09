FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

# Thiết lập thư mục làm việc
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Env config
ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--reload-dir", "/app/src"]