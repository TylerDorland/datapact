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

# Copy shared library first (build from repo root with -f flag)
COPY shared/datapact_common /app/shared/datapact_common

# Copy dependency files
COPY services/template-data-service/pyproject.toml services/template-data-service/poetry.lock* ./

# Update the path in pyproject.toml for Docker context
RUN sed -i 's|../../shared/datapact_common|/app/shared/datapact_common|g' pyproject.toml

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY services/template-data-service/src/ ./src/
COPY services/template-data-service/alembic.ini .
COPY services/template-data-service/alembic/ ./alembic/
COPY services/template-data-service/contract.yaml .
COPY services/template-data-service/startup.sh .

# Install the package itself
RUN poetry install --no-interaction --no-ansi --only-root

# Make startup script executable
RUN chmod +x startup.sh

# Run startup script (runs migrations then starts app)
CMD ["./startup.sh"]
