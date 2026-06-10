FROM python:3.11-slim

WORKDIR /app

# Install Node.js and bake in the MongoDB MCP Server so it is present in the
# image — avoids a runtime `npx` download on Cloud Run cold start (network
# dependency / latency / egress-restriction failure risk).
RUN apt-get update && apt-get install -y --no-install-recommends \
        nodejs \
        npm \
    && npm install -g mongodb-mcp-server \
    && rm -rf /var/lib/apt/lists/*

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
