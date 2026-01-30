FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1 && \
    poetry config virtualenvs.create false

# Set Python path for development with volume mounts
ENV PYTHONPATH=/app/src

# Copy dependency files
COPY services/dictionary-service/pyproject.toml services/dictionary-service/poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY services/dictionary-service/src/ ./src/

# Install the package itself
RUN poetry install --no-interaction --no-ansi --only-root

# Run with uvicorn
CMD ["uvicorn", "dictionary_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
