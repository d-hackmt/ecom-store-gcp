# Ingestion service — all write endpoints (product CRUD/bulk upload, auth,
# cart writes, order placement). Build from the repo root:
#   docker build -f services/ingestion/Dockerfile -t clothstore-ingestion .
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Shared application code (this service only needs backend/, not Frontend/)
COPY backend/ ./backend
COPY services/ingestion/ ./services/ingestion
COPY services/__init__.py ./services/__init__.py

ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["uvicorn", "services.ingestion.main:app", "--host", "0.0.0.0", "--port", "8001"]
