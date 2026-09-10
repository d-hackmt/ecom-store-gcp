# Retrieval service — all read endpoints (product listing, profile/cart/order
# lookups, chatbot) plus the Frontend and uploaded files. Build from the repo root:
#   docker build -f services/retrieval/Dockerfile -t clothstore-retrieval .
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Shared application code + the Frontend this service serves statically
COPY backend/ ./backend
COPY services/retrieval/ ./services/retrieval
COPY services/__init__.py ./services/__init__.py
COPY Frontend/ ./Frontend

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "services.retrieval.main:app", "--host", "0.0.0.0", "--port", "8000"]
