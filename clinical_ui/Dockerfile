# EchoScribe-AI Review & Audit Interface Container
# Member 4 (Dinesh - IT Lead Deliverable)

FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY clinical_ui/ /app/clinical_ui/
COPY asr_pipeline/ /app/asr_pipeline/
COPY capture_engine/ /app/capture_engine/
COPY data/ /app/data/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

CMD ["python", "clinical_ui/server.py"]
