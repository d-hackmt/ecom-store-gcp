# Build the Application
FROM python:3.11-slim
WORKDIR /app

# uv — fast Python package installer (astral.sh/uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install backend dependencies
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy source code (Backend + Frontend natively)
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
