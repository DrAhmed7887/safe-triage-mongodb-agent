FROM python:3.11-slim

WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy directories and code
COPY agent/ ./agent/
COPY backend/ ./backend/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Expose FastAPI port
EXPOSE 8080

# Run FastAPI production webserver
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
