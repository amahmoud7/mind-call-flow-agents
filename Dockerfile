# Python Agent Dockerfile for Railway/Cloud Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Expose port (not strictly necessary for LiveKit agents but good practice)
EXPOSE 8080

# Run all agents simultaneously
# This allows all 4 agent types to be available for dispatch
CMD python run_all_agents.py
