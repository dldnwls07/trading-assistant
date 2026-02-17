# Multi-stage build for efficient image size
# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Runtime Environment
FROM python:3.11-slim

# Install system dependencies (git, gcc for some python packages)
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Backend Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend Code
COPY . .

# Copy Built Frontend Assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose Port (Render sets PORT env, but 8000 is default)
EXPOSE 8000

# Run Startup Script
CMD ["sh", "start_render.sh"]
