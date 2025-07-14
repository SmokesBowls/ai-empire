FROM python:3.11-slim-bullseye

WORKDIR /empire

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    espeak \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy empire files
COPY ai_empire_deployable/ ./ai_empire_deployable/
COPY ai-empire/ ./ai-empire/

# Install Python dependencies
COPY requirements_empire.txt .
RUN pip install --no-cache-dir -r requirements_empire.txt

# Install Ollama (but we'll use external Ollama for now)
# RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create logs directory
RUN mkdir -p /logs && chmod 777 /logs

# Set working directory for empire
WORKDIR /empire

# Expose all empire ports
EXPOSE 8000 8001 8002 8003 8004 8005 8009

# Default command
CMD ["./ai_empire_deployable/scripts/start_empire.sh"]
