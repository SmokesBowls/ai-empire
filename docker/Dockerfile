FROM python:3.11-slim-bullseye

WORKDIR /empire

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    espeak \
    espeak-data \
    build-essential \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the project structure (from parent directory context)
COPY services/ ./services/
COPY scripts/ ./scripts/
COPY docker/requirements_empire.txt ./requirements.txt

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Make all scripts executable
RUN find . -name "*.sh" -type f -exec chmod +x {} \;

# Create necessary directories
RUN mkdir -p /empire_data /logs

# Set environment variables
ENV EMPIRE_LOG_PATH=/logs/empire.log
ENV PYTHONPATH=/empire
ENV EMPIRE_ROOT=/empire

# Expose all empire service ports
EXPOSE 8000 8001 8002 8003 8005 8009 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command with fallback
CMD ["bash", "-c", "if [ -f './scripts/start_empire.sh' ]; then ./scripts/start_empire.sh; else echo 'Empire services starting...'; python3 -m http.server 8000; fi"]
