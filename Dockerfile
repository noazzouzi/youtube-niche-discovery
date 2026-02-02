FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies (optional for live API mode)
COPY requirements.txt requirements-live-api.txt ./

# Install basic dependencies (uncomment for live API mode)
# RUN pip install --no-cache-dir -r requirements-live-api.txt

# Copy application
COPY production_server.py ./

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/status')"

# Run the application
CMD ["python", "production_server.py"]