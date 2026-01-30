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
COPY services/notification-service/startup.sh .

# Install the package itself
RUN poetry install --no-interaction --no-ansi --only-root

# Make startup script executable
RUN chmod +x startup.sh

# Run startup script (runs migrations then starts app)
CMD ["./startup.sh"]
