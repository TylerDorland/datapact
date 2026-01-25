FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.7.1
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Set Python path for development with volume mounts
ENV PYTHONPATH=/app/src

# Copy dependency files
COPY services/notification-service/pyproject.toml services/notification-service/poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY services/notification-service/src/ ./src/
COPY services/notification-service/alembic.ini .
COPY services/notification-service/alembic/ ./alembic/

# Install the package itself
RUN poetry install --no-interaction --no-ansi --only-root

# Run with uvicorn
CMD ["uvicorn", "notification_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
