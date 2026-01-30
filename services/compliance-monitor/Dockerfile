FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1 && \
    poetry config virtualenvs.create false

# Copy shared library first
COPY shared/datapact_common /app/shared/datapact_common

# Copy dependency files
COPY services/compliance-monitor/pyproject.toml services/compliance-monitor/poetry.lock* ./

# Update the path in pyproject.toml for Docker context
RUN sed -i 's|../../shared/datapact_common|/app/shared/datapact_common|g' pyproject.toml

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY services/compliance-monitor/src/ ./src/

# Install the package itself
RUN poetry install --no-interaction --no-ansi --only-root

# Default command runs the Celery worker
CMD ["celery", "-A", "compliance_monitor.celery_app", "worker", "--loglevel=info"]
