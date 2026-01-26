# DataPact: Contract-Driven Data Governance Platform

## Project Instructions for Claude Code

This document provides comprehensive instructions for building the DataPact platform—a contract-driven data governance framework. Follow these instructions to build the system incrementally.

---

## ⚠️ Development Environment: Docker Required

**All services must run in Docker containers.** Do not run services directly on the host machine.

### Why Docker?
- Consistent environment across all developers
- PostgreSQL and Redis are containerized dependencies
- Service-to-service communication uses Docker networking
- Production parity from day one

### Package Management: Poetry

**Use Poetry for all Python dependency management.** Do not use pip, requirements.txt, or setup.py.

Each service has its own `pyproject.toml`:

```toml
[tool.poetry]
name = "contract-service"
version = "0.1.0"
description = "DataPact Contract Service"
authors = ["Your Team"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.25"}
asyncpg = "^0.29.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
alembic = "^1.13.0"
httpx = "^0.26.0"
celery = {extras = ["redis"], version = "^5.3.0"}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^4.1.0"
ruff = "^0.1.0"
mypy = "^1.8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**Key Poetry Commands (inside Docker container):**

| Task | Command |
|------|---------|
| Install dependencies | `poetry install` |
| Add a dependency | `poetry add fastapi` |
| Add dev dependency | `poetry add --group dev pytest` |
| Update dependencies | `poetry update` |
| Show installed packages | `poetry show` |
| Run a command | `poetry run pytest` |

### Database Migrations: Alembic

**Use Alembic for all database schema changes.** Never modify the database schema manually.

Each service with a database has its own Alembic configuration:

```
services/contract-service/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_watchers.py
│       └── ...
```

**Key Alembic Commands (inside Docker container):**

| Task | Command |
|------|---------|
| Create migration | `alembic revision --autogenerate -m "description"` |
| Apply all migrations | `alembic upgrade head` |
| Rollback one migration | `alembic downgrade -1` |
| Rollback all migrations | `alembic downgrade base` |
| Show current revision | `alembic current` |
| Show migration history | `alembic history` |

**Example: Creating a new migration**

```bash
# Shell into the container
docker-compose exec contract-service bash

# Generate migration from model changes
alembic revision --autogenerate -m "add notification preferences to subscribers"

# Review the generated migration in alembic/versions/
# Then apply it
alembic upgrade head
```

**Alembic env.py configuration:**

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
import asyncio

from alembic import context
from contract_service.config import settings
from contract_service.models import Base  # Import all models

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Development Workflow

```bash
# 1. Start infrastructure (database + redis)
docker-compose up -d postgres redis

# 2. Build and start all services
docker-compose up --build

# 3. Or start specific services
docker-compose up contract-service compliance-monitor

# 4. View logs
docker-compose logs -f contract-service

# 5. Run migrations (inside container)
docker-compose exec contract-service alembic upgrade head

# 6. Run tests (inside container)
docker-compose exec contract-service pytest

# 7. Stop everything
docker-compose down
```

### Adding Dependencies with Poetry

```bash
# Shell into the container first
docker-compose exec contract-service bash

# Add a runtime dependency
poetry add pydantic-settings

# Add a dev dependency
poetry add --group dev pytest-mock

# Update all dependencies
poetry update

# Generate/update poetry.lock (committed to git)
poetry lock
```

### Creating Database Migrations with Alembic

```bash
# Shell into the container
docker-compose exec contract-service bash

# Initialize Alembic (only once per service)
alembic init alembic

# After modifying SQLAlchemy models, generate migration
alembic revision --autogenerate -m "add subscriber notification preferences"

# Apply pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

### Key Docker Commands

| Task | Command |
|------|---------|
| Rebuild after code changes | `docker-compose up --build` |
| Restart a single service | `docker-compose restart contract-service` |
| Shell into container | `docker-compose exec contract-service bash` |
| View running containers | `docker-compose ps` |
| Clean up everything | `docker-compose down -v --rmi local` |

### Service URLs (when running)

| Service | URL |
|---------|-----|
| Contract Service | http://localhost:8001 |
| Dictionary Service | http://localhost:8002 |
| Template Data Service | http://localhost:8003 |
| Notification Service | http://localhost:8004 |
| Frontend | http://localhost:3000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| MailHog (email testing) | http://localhost:8025 |

---

## Project Overview

DataPact is a microservices-based platform that enforces data contracts between data publishers and subscribers. The system consists of:

1. **Contract Service** — Central registry for data contracts with validation and versioning
2. **Compliance Monitor** — Background service that validates data services against their contracts
3. **Dictionary Service** — Aggregates contracts into a searchable data dictionary with ERD generation
4. **Notification Service** — Alerting system that notifies interested parties of compliance issues and changes
5. **Frontend** — React dashboard for visualizing contracts, compliance, dictionary, and ERD
6. **Template Data Microservice** — Reference implementation for data services that comply with contracts

> **Note:** See `ALERTING_SYSTEM.md` for notification service specs and `FRONTEND.md` for frontend specs.

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11+ |
| **Package Manager** | **Poetry** | **1.7+** |
| API Framework | FastAPI | 0.109+ |
| Data Validation | Pydantic | 2.x |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy | 2.x |
| **Migrations** | **Alembic** | **1.13+** |
| Task Queue | Celery | 5.x |
| Message Broker | Redis | 7+ |
| HTTP Client | httpx | 0.26+ |
| Testing | pytest, pytest-asyncio | latest |
| Containerization | Docker, Docker Compose | latest |
| Linting | ruff | latest |
| Type Checking | mypy | latest |

> **Important:** Use Poetry for all dependency management. Use Alembic for all database migrations. Do not use pip/requirements.txt or manual SQL for schema changes.

---

## Repository Structure

Create a monorepo with the following structure:

```
datapact/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
├── pyproject.toml                    # Workspace-level dependencies (optional)
│
├── services/
│   ├── contract-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml            # Poetry dependencies
│   │   ├── poetry.lock               # Locked versions (commit this!)
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/             # Migration files
│   │   ├── src/
│   │   │   └── contract_service/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── config.py
│   │   │       ├── database.py
│   │   │       ├── models/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── contract.py
│   │   │       │   ├── field.py
│   │   │       │   ├── quality.py
│   │   │       │   ├── access.py
│   │   │       │   └── subscriber.py
│   │   │       ├── schemas/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── contract.py
│   │   │       │   ├── field.py
│   │   │       │   ├── quality.py
│   │   │       │   ├── access.py
│   │   │       │   └── subscriber.py
│   │   │       ├── api/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── routes/
│   │   │       │   │   ├── __init__.py
│   │   │       │   │   ├── contracts.py
│   │   │       │   │   ├── fields.py
│   │   │       │   │   ├── subscribers.py
│   │   │       │   │   ├── validation.py
│   │   │       │   │   └── webhooks.py
│   │   │       │   └── dependencies.py
│   │   │       ├── services/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── contract_service.py
│   │   │       │   ├── validation_service.py
│   │   │       │   ├── github_service.py
│   │   │       │   └── notification_service.py
│   │   │       └── utils/
│   │   │           ├── __init__.py
│   │   │           └── yaml_parser.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_contracts.py
│   │       ├── test_validation.py
│   │       └── test_webhooks.py
│   │
│   ├── compliance-monitor/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── compliance_monitor/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── config.py
│   │   │       ├── celery_app.py
│   │   │       ├── tasks/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── schema_check.py
│   │   │       │   ├── quality_check.py
│   │   │       │   └── availability_check.py
│   │   │       ├── checks/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── base.py
│   │   │       │   ├── schema_validator.py
│   │   │       │   ├── freshness_checker.py
│   │   │       │   └── completeness_checker.py
│   │   │       └── reporters/
│   │   │           ├── __init__.py
│   │   │           ├── slack.py
│   │   │           └── email.py
│   │   └── tests/
│   │
│   ├── dictionary-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── dictionary_service/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── config.py
│   │   │       ├── api/
│   │   │       │   ├── __init__.py
│   │   │       │   └── routes/
│   │   │       │       ├── __init__.py
│   │   │       │       ├── dictionary.py
│   │   │       │       ├── search.py
│   │   │       │       └── erd.py
│   │   │       ├── services/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── aggregator.py
│   │   │       │   ├── search_service.py
│   │   │       │   └── erd_generator.py
│   │   │       └── templates/
│   │   │           └── erd.mermaid.jinja2
│   │   └── tests/
│   │
│   ├── notification-service/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── notification_service/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── config.py
│   │   │       ├── celery_app.py
│   │   │       ├── database.py
│   │   │       ├── models/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── notification.py
│   │   │       │   └── watcher.py
│   │   │       ├── schemas/
│   │   │       │   ├── __init__.py
│   │   │       │   └── events.py
│   │   │       ├── api/
│   │   │       │   ├── __init__.py
│   │   │       │   └── routes/
│   │   │       │       ├── __init__.py
│   │   │       │       ├── events.py
│   │   │       │       ├── notifications.py
│   │   │       │       └── preferences.py
│   │   │       ├── services/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── router.py
│   │   │       │   ├── recipient_resolver.py
│   │   │       │   └── template_renderer.py
│   │   │       ├── channels/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── base.py
│   │   │       │   └── email.py
│   │   │       ├── templates/
│   │   │       │   └── email/
│   │   │       │       ├── base.html
│   │   │       │       ├── schema_drift.html
│   │   │       │       ├── quality_breach.html
│   │   │       │       ├── pr_blocked.html
│   │   │       │       ├── contract_updated.html
│   │   │       │       └── deprecation_warning.html
│   │   │       └── tasks/
│   │   │           ├── __init__.py
│   │   │           └── send_notification.py
│   │   └── tests/
│   │
│   └── template-data-service/
│       ├── Dockerfile
│       ├── pyproject.toml
│       ├── alembic.ini
│       ├── alembic/
│       ├── contract.yaml                # Example contract file
│       ├── src/
│       │   └── data_service/
│       │       ├── __init__.py
│       │       ├── main.py
│       │       ├── config.py
│       │       ├── database.py
│       │       ├── models/
│       │       ├── schemas/
│       │       ├── api/
│       │       │   ├── __init__.py
│       │       │   └── routes/
│       │       │       ├── __init__.py
│       │       │       ├── health.py
│       │       │       ├── schema.py
│       │       │       ├── metrics.py
│       │       │       └── data.py
│       │       └── metrics/
│       │           ├── __init__.py
│       │           ├── collector.py
│       │           └── freshness.py
│       └── tests/
│
├── shared/
│   └── datapact_common/
│       ├── pyproject.toml
│       ├── src/
│       │   └── datapact_common/
│       │       ├── __init__.py
│       │       ├── contract_schema.py    # Shared contract Pydantic models
│       │       ├── exceptions.py
│       │       └── constants.py
│       └── tests/
│
├── scripts/
│   ├── init-db.sh
│   ├── run-migrations.sh
│   └── seed-example-data.py
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        ├── components/
        ├── hooks/
        ├── pages/
        ├── types/
        └── lib/
```

---

## Phase 1: Foundation

### Task 1.1: Project Initialization

Create the repository structure, root `pyproject.toml`, and shared library.

**Root pyproject.toml:**
```toml
[project]
name = "datapact"
version = "0.1.0"
description = "Contract-driven data governance platform"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
```

**shared/datapact_common/src/datapact_common/contract_schema.py:**

This defines the canonical contract format used across all services:

```python
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    UUID = "uuid"
    JSON = "json"
    ARRAY = "array"


class AuthType(str, Enum):
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    JWT = "jwt"


class MetricType(str, Enum):
    FRESHNESS = "freshness"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    AVAILABILITY = "availability"
    UNIQUENESS = "uniqueness"


class FieldConstraint(BaseModel):
    """Constraint on a field value."""
    type: str  # e.g., "min", "max", "regex", "enum", "expression"
    value: Any
    message: str | None = None


class ContractField(BaseModel):
    """Definition of a single field in the contract schema."""
    name: str = Field(..., min_length=1, max_length=255)
    data_type: DataType
    description: str | None = None
    nullable: bool = True
    is_pii: bool = False
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_reference: str | None = None  # format: "contract_name.field_name"
    example_value: Any | None = None
    constraints: list[FieldConstraint] = Field(default_factory=list)


class QualityMetric(BaseModel):
    """Quality SLA definition."""
    metric_type: MetricType
    threshold: str  # e.g., "99.5%", "15 minutes", "99.9%"
    measurement_method: str | None = None
    alert_on_breach: bool = True


class AccessConfig(BaseModel):
    """Access configuration for the dataset."""
    endpoint_url: str
    methods: list[str] = Field(default_factory=lambda: ["GET"])
    auth_type: AuthType = AuthType.NONE
    required_scopes: list[str] = Field(default_factory=list)
    rate_limit: str | None = None  # e.g., "1000 req/min"


class Subscriber(BaseModel):
    """Subscriber registration."""
    team: str
    use_case: str | None = None
    fields_used: list[str] = Field(default_factory=list)
    contact_email: str | None = None


class Publisher(BaseModel):
    """Publisher information."""
    team: str
    owner: str
    repository_url: str | None = None
    contact_email: str | None = None


class ContractDefinition(BaseModel):
    """
    Complete data contract definition.
    This is the canonical schema for all contracts in the system.
    """
    name: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z][a-z0-9_]*$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")  # semver
    description: str | None = None
    status: str = "active"  # active, deprecated, draft
    
    publisher: Publisher
    schema_fields: list[ContractField] = Field(..., alias="schema")
    quality: list[QualityMetric] = Field(default_factory=list)
    access: AccessConfig | None = None
    subscribers: list[Subscriber] = Field(default_factory=list)
    
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True


class ContractValidationResult(BaseModel):
    """Result of validating a service against its contract."""
    contract_name: str
    contract_version: str
    is_valid: bool
    checked_at: datetime
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
```

---

### Task 1.2: Contract Service Database Schema

Create the PostgreSQL schema using SQLAlchemy models and Alembic migrations.

**services/contract-service/src/contract_service/models/contract.py:**

```python
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    
    # Publisher info
    publisher_team = Column(String(255), nullable=False, index=True)
    publisher_owner = Column(String(255), nullable=False)
    repository_url = Column(String(500))
    contact_email = Column(String(255))
    
    # Metadata
    tags = Column(JSONB, default=list)
    metadata_ = Column("metadata", JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    fields = relationship("ContractField", back_populates="contract", cascade="all, delete-orphan")
    quality_metrics = relationship("QualityMetric", back_populates="contract", cascade="all, delete-orphan")
    access_config = relationship("AccessConfig", back_populates="contract", uselist=False, cascade="all, delete-orphan")
    subscribers = relationship("Subscriber", back_populates="contract", cascade="all, delete-orphan")
    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="contract", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_contracts_publisher_team_status", "publisher_team", "status"),
    )


class ContractField(Base):
    __tablename__ = "contract_fields"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    description = Column(Text)
    nullable = Column(Boolean, default=True)
    is_pii = Column(Boolean, default=False, index=True)
    is_primary_key = Column(Boolean, default=False)
    is_foreign_key = Column(Boolean, default=False)
    foreign_key_reference = Column(String(500))
    example_value = Column(Text)
    constraints = Column(JSONB, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    contract = relationship("Contract", back_populates="fields")
    
    __table_args__ = (
        Index("ix_contract_fields_contract_name", "contract_id", "name", unique=True),
        Index("ix_contract_fields_pii", "is_pii"),
    )


class QualityMetric(Base):
    __tablename__ = "quality_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    metric_type = Column(String(100), nullable=False)
    threshold = Column(String(100), nullable=False)
    measurement_method = Column(Text)
    alert_on_breach = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    contract = relationship("Contract", back_populates="quality_metrics")


class AccessConfig(Base):
    __tablename__ = "access_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    endpoint_url = Column(String(500), nullable=False)
    methods = Column(JSONB, default=["GET"])
    auth_type = Column(String(100), default="none")
    required_scopes = Column(JSONB, default=list)
    rate_limit = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    contract = relationship("Contract", back_populates="access_config")


class Subscriber(Base):
    __tablename__ = "subscribers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    team = Column(String(255), nullable=False, index=True)
    use_case = Column(Text)
    fields_used = Column(JSONB, default=list)
    contact_email = Column(String(255))
    
    subscribed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    contract = relationship("Contract", back_populates="subscribers")
    
    __table_args__ = (
        Index("ix_subscribers_contract_team", "contract_id", "team", unique=True),
    )


class ContractVersion(Base):
    __tablename__ = "contract_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    version = Column(String(50), nullable=False)
    contract_snapshot = Column(JSONB, nullable=False)
    change_summary = Column(Text)
    changed_by = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    contract = relationship("Contract", back_populates="versions")
    
    __table_args__ = (
        Index("ix_contract_versions_contract_version", "contract_id", "version"),
    )


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    check_type = Column(String(100), nullable=False)  # schema, freshness, availability, etc.
    status = Column(String(50), nullable=False)  # pass, fail, warning
    details = Column(JSONB, default=dict)
    error_message = Column(Text)
    
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    contract = relationship("Contract", back_populates="compliance_checks")
    
    __table_args__ = (
        Index("ix_compliance_checks_contract_type_time", "contract_id", "check_type", "checked_at"),
    )
```

---

### Task 1.3: Contract Service API

Implement the FastAPI application with all CRUD routes.

**services/contract-service/src/contract_service/main.py:**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contract_service.config import settings
from contract_service.database import engine, Base
from contract_service.api.routes import contracts, fields, subscribers, validation, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist (dev only)
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="DataPact Contract Service",
    description="Central registry for data contracts",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["contracts"])
app.include_router(fields.router, prefix="/api/v1/contracts", tags=["fields"])
app.include_router(subscribers.router, prefix="/api/v1/contracts", tags=["subscribers"])
app.include_router(validation.router, prefix="/api/v1/contracts", tags=["validation"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "contract-service"}
```

**services/contract-service/src/contract_service/api/routes/contracts.py:**

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from contract_service.api.dependencies import get_db
from contract_service.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
)
from contract_service.services.contract_service import ContractCRUD

router = APIRouter()


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract: ContractCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new data contract."""
    crud = ContractCRUD(db)
    
    # Check if contract with same name exists
    existing = await crud.get_by_name(contract.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contract with name '{contract.name}' already exists",
        )
    
    return await crud.create(contract)


@router.get("", response_model=ContractListResponse)
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str | None = Query(None),
    publisher_team: str | None = Query(None),
    tag: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all contracts with optional filtering."""
    crud = ContractCRUD(db)
    contracts, total = await crud.list(
        skip=skip,
        limit=limit,
        status=status,
        publisher_team=publisher_team,
        tag=tag,
    )
    return ContractListResponse(contracts=contracts, total=total, skip=skip, limit=limit)


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a contract by ID."""
    crud = ContractCRUD(db)
    contract = await crud.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )
    return contract


@router.get("/name/{name}", response_model=ContractResponse)
async def get_contract_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a contract by name."""
    crud = ContractCRUD(db)
    contract = await crud.get_by_name(name)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract '{name}' not found",
        )
    return contract


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: UUID,
    contract_update: ContractUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a contract. Creates a new version."""
    crud = ContractCRUD(db)
    contract = await crud.update(contract_id, contract_update)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deprecate_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Deprecate a contract (soft delete)."""
    crud = ContractCRUD(db)
    success = await crud.deprecate(contract_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )


@router.get("/{contract_id}/versions")
async def get_contract_versions(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get version history for a contract."""
    crud = ContractCRUD(db)
    versions = await crud.get_versions(contract_id)
    return {"versions": versions}
```

---

### Task 1.4: Template Data Microservice

Create a reference implementation that complies with the contract system.

**Required endpoints every data microservice must implement:**

```python
# services/template-data-service/src/data_service/api/routes/health.py

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Standard health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "data-service",
    }
```

```python
# services/template-data-service/src/data_service/api/routes/schema.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect

from data_service.database import get_db
from data_service.config import settings

router = APIRouter()


@router.get("/schema")
async def get_schema(db: AsyncSession = Depends(get_db)):
    """
    Return the current database schema.
    This endpoint is polled by the Compliance Monitor.
    """
    async with db.begin():
        conn = await db.connection()
        
        # Get raw connection for inspection
        raw_conn = await conn.get_raw_connection()
        inspector = inspect(raw_conn.dbapi_connection)
        
        tables = {}
        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": str(col.get("default")) if col.get("default") else None,
                    "primary_key": col.get("primary_key", False),
                })
            
            # Get foreign keys
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                fks.append({
                    "columns": fk["constrained_columns"],
                    "references": f"{fk['referred_table']}.{fk['referred_columns'][0]}",
                })
            
            tables[table_name] = {
                "columns": columns,
                "foreign_keys": fks,
            }
    
    return {
        "service": settings.service_name,
        "contract_name": settings.contract_name,
        "tables": tables,
    }
```

```python
# services/template-data-service/src/data_service/api/routes/metrics.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from data_service.database import get_db
from data_service.metrics.collector import MetricsCollector

router = APIRouter()


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Return quality metrics for compliance monitoring.
    This endpoint is polled by the Compliance Monitor.
    """
    collector = MetricsCollector(db)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "freshness": await collector.get_freshness_metrics(),
        "completeness": await collector.get_completeness_metrics(),
        "row_count": await collector.get_row_count(),
        "availability": {
            "status": "up",
            "uptime_percentage": 99.9,  # Would come from actual monitoring
        },
    }
```

```python
# services/template-data-service/src/data_service/metrics/collector.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta


class MetricsCollector:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_freshness_metrics(self) -> dict:
        """Calculate data freshness based on updated_at timestamps."""
        # This assumes tables have an updated_at column
        # Adjust query based on actual schema
        result = await self.db.execute(
            text("""
                SELECT 
                    MAX(updated_at) as last_update,
                    NOW() - MAX(updated_at) as time_since_update
                FROM main_table
            """)
        )
        row = result.fetchone()
        
        if row and row.last_update:
            return {
                "last_update": row.last_update.isoformat(),
                "seconds_since_update": row.time_since_update.total_seconds(),
                "is_fresh": row.time_since_update < timedelta(minutes=15),
            }
        
        return {"last_update": None, "seconds_since_update": None, "is_fresh": False}
    
    async def get_completeness_metrics(self) -> dict:
        """Calculate completeness for required fields."""
        # This would check for NULL values in required fields
        result = await self.db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(required_field_1) as field_1_count,
                    COUNT(required_field_2) as field_2_count
                FROM main_table
            """)
        )
        row = result.fetchone()
        
        if row and row.total_rows > 0:
            return {
                "total_rows": row.total_rows,
                "field_completeness": {
                    "required_field_1": row.field_1_count / row.total_rows * 100,
                    "required_field_2": row.field_2_count / row.total_rows * 100,
                },
            }
        
        return {"total_rows": 0, "field_completeness": {}}
    
    async def get_row_count(self) -> int:
        """Get total row count."""
        result = await self.db.execute(text("SELECT COUNT(*) FROM main_table"))
        return result.scalar() or 0
```

---

### Task 1.5: Docker Configuration

**docker-compose.yml:**

```yaml
version: "3.8"

services:
  # Shared PostgreSQL for all services (dev only - use separate DBs in prod)
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: datapact
      POSTGRES_PASSWORD: datapact_dev
      POSTGRES_DB: datapact
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U datapact"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  contract-service:
    build:
      context: ./services/contract-service
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://datapact:datapact_dev@postgres:5432/contracts
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: development
    ports:
      - "8001:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./services/contract-service/src:/app/src

  compliance-monitor:
    build:
      context: ./services/compliance-monitor
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://datapact:datapact_dev@postgres:5432/contracts
      REDIS_URL: redis://redis:6379/0
      CONTRACT_SERVICE_URL: http://contract-service:8000
    depends_on:
      - contract-service
      - redis
    volumes:
      - ./services/compliance-monitor/src:/app/src

  dictionary-service:
    build:
      context: ./services/dictionary-service
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://datapact:datapact_dev@postgres:5432/contracts
      CONTRACT_SERVICE_URL: http://contract-service:8000
    ports:
      - "8003:8000"
    depends_on:
      - contract-service
    volumes:
      - ./services/dictionary-service/src:/app/src

  # Example data service
  template-data-service:
    build:
      context: ./services/template-data-service
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://datapact:datapact_dev@postgres:5432/template_data
      CONTRACT_SERVICE_URL: http://contract-service:8000
      SERVICE_NAME: template-data-service
      CONTRACT_NAME: example_dataset
    ports:
      - "8010:8000"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:

  # --- Add these services after Phase 5 & 6 ---
  
  # Notification Service (add in Phase 5)
  notification-service:
    build:
      context: ./services/notification-service
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://datapact:datapact_dev@postgres:5432/contracts
      REDIS_URL: redis://redis:6379/1
      CONTRACT_SERVICE_URL: http://contract-service:8000
      NOTIFICATION_SMTP_HOST: mailhog
      NOTIFICATION_SMTP_PORT: 1025
      NOTIFICATION_SMTP_USE_TLS: "false"
    ports:
      - "8004:8000"
    depends_on:
      - contract-service
      - redis
    volumes:
      - ./services/notification-service/src:/app/src

  notification-worker:
    build:
      context: ./services/notification-service
      dockerfile: Dockerfile
    command: celery -A notification_service.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql+asyncpg://datapact:datapact_dev@postgres:5432/contracts
      REDIS_URL: redis://redis:6379/1
      CONTRACT_SERVICE_URL: http://contract-service:8000
      NOTIFICATION_SMTP_HOST: mailhog
      NOTIFICATION_SMTP_PORT: 1025
      NOTIFICATION_SMTP_USE_TLS: "false"
    depends_on:
      - notification-service
      - redis

  # Local email testing UI (shows sent emails)
  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI to view emails

  # Frontend (add in Phase 6)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - contract-service
      - dictionary-service
    environment:
      - VITE_API_BASE_URL=http://localhost:8001

volumes:
  postgres_data:
```

**services/contract-service/Dockerfile:**

```dockerfile
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

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no dev dependencies in production)
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY src/ ./src/
COPY alembic.ini .
COPY alembic/ ./alembic/

# Install the package itself
RUN poetry install --no-interaction --no-ansi --only-root

# Run with uvicorn
CMD ["uvicorn", "contract_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Development Dockerfile (with dev dependencies):**

For development, you may want a separate Dockerfile or use build args:

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

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

COPY pyproject.toml poetry.lock* ./

# Install ALL dependencies including dev
RUN poetry install --no-interaction --no-ansi --no-root

COPY src/ ./src/
COPY alembic.ini .
COPY alembic/ ./alembic/

RUN poetry install --no-interaction --no-ansi --only-root

CMD ["uvicorn", "contract_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## Phase 2: Compliance Monitoring

### Task 2.1: Celery Worker Setup

**services/compliance-monitor/src/compliance_monitor/celery_app.py:**

```python
from celery import Celery
from celery.schedules import crontab

from compliance_monitor.config import settings

celery_app = Celery(
    "compliance_monitor",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "check-all-schemas": {
        "task": "compliance_monitor.tasks.schema_check.check_all_schemas",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "check-all-quality": {
        "task": "compliance_monitor.tasks.quality_check.check_all_quality",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "check-all-availability": {
        "task": "compliance_monitor.tasks.availability_check.check_all_availability",
        "schedule": crontab(minute="*"),  # Every minute
    },
}
```

### Task 2.2: Schema Validation

**services/compliance-monitor/src/compliance_monitor/checks/schema_validator.py:**

```python
from typing import Any
from datapact_common.contract_schema import ContractDefinition, ContractField


class SchemaValidator:
    """Validates a service's actual schema against its contract."""
    
    def __init__(self, contract: ContractDefinition):
        self.contract = contract
        self.errors: list[str] = []
        self.warnings: list[str] = []
    
    def validate(self, actual_schema: dict[str, Any]) -> bool:
        """
        Compare actual schema from /schema endpoint against contract.
        Returns True if valid, False otherwise.
        """
        self.errors = []
        self.warnings = []
        
        # Build lookup of expected fields
        expected_fields = {f.name: f for f in self.contract.schema_fields}
        
        # Get actual columns from the schema response
        actual_tables = actual_schema.get("tables", {})
        
        # Flatten all columns across tables for comparison
        # In a real implementation, you'd want table-level matching
        actual_columns = {}
        for table_name, table_info in actual_tables.items():
            for col in table_info.get("columns", []):
                actual_columns[col["name"]] = col
        
        # Check for missing fields
        for field_name, field_def in expected_fields.items():
            if field_name not in actual_columns:
                self.errors.append(f"Missing required field: {field_name}")
                continue
            
            actual_col = actual_columns[field_name]
            
            # Type checking (simplified - would need type mapping)
            if not self._types_compatible(field_def.data_type.value, actual_col["type"]):
                self.errors.append(
                    f"Type mismatch for {field_name}: "
                    f"expected {field_def.data_type.value}, got {actual_col['type']}"
                )
            
            # Nullable checking
            if not field_def.nullable and actual_col.get("nullable", True):
                self.errors.append(
                    f"Field {field_name} should be NOT NULL but is nullable"
                )
        
        # Check for extra fields (warning, not error)
        for col_name in actual_columns:
            if col_name not in expected_fields:
                self.warnings.append(f"Undocumented field in schema: {col_name}")
        
        return len(self.errors) == 0
    
    def _types_compatible(self, contract_type: str, db_type: str) -> bool:
        """Check if database type is compatible with contract type."""
        # Simplified type mapping - expand as needed
        type_mapping = {
            "string": ["varchar", "text", "char", "character varying"],
            "integer": ["int", "integer", "bigint", "smallint", "serial", "bigserial"],
            "float": ["float", "real", "double precision"],
            "decimal": ["decimal", "numeric"],
            "boolean": ["bool", "boolean"],
            "date": ["date"],
            "datetime": ["timestamp", "timestamp without time zone"],
            "timestamp": ["timestamp", "timestamp with time zone", "timestamptz"],
            "uuid": ["uuid"],
            "json": ["json", "jsonb"],
            "array": ["array"],
        }
        
        db_type_lower = db_type.lower()
        expected_types = type_mapping.get(contract_type, [])
        
        return any(t in db_type_lower for t in expected_types)
    
    def get_result(self) -> dict:
        """Return validation result as dict."""
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
        }
```

### Task 2.3: Compliance Check Task

**services/compliance-monitor/src/compliance_monitor/tasks/schema_check.py:**

```python
import httpx
from celery import shared_task

from compliance_monitor.celery_app import celery_app
from compliance_monitor.config import settings
from compliance_monitor.checks.schema_validator import SchemaValidator
from datapact_common.contract_schema import ContractDefinition


@celery_app.task(bind=True, max_retries=3)
def check_schema(self, contract_id: str):
    """Check a single contract's schema compliance."""
    try:
        # Fetch contract from Contract Service
        with httpx.Client() as client:
            contract_resp = client.get(
                f"{settings.contract_service_url}/api/v1/contracts/{contract_id}"
            )
            contract_resp.raise_for_status()
            contract_data = contract_resp.json()
            
            # Get access endpoint from contract
            endpoint = contract_data.get("access", {}).get("endpoint_url")
            if not endpoint:
                return {"status": "skipped", "reason": "No endpoint configured"}
            
            # Fetch actual schema from data service
            schema_resp = client.get(f"{endpoint}/schema", timeout=30)
            schema_resp.raise_for_status()
            actual_schema = schema_resp.json()
        
        # Validate
        contract = ContractDefinition(**contract_data)
        validator = SchemaValidator(contract)
        is_valid = validator.validate(actual_schema)
        result = validator.get_result()
        
        # Record result
        _record_compliance_check(
            contract_id=contract_id,
            check_type="schema",
            status="pass" if is_valid else "fail",
            details=result,
        )
        
        # Alert on failure
        if not is_valid:
            _send_alert(contract_data, result)
        
        return result
        
    except httpx.HTTPError as e:
        self.retry(exc=e, countdown=60)
    except Exception as e:
        _record_compliance_check(
            contract_id=contract_id,
            check_type="schema",
            status="error",
            details={"error": str(e)},
        )
        raise


@celery_app.task
def check_all_schemas():
    """Scheduled task to check all active contracts."""
    with httpx.Client() as client:
        resp = client.get(
            f"{settings.contract_service_url}/api/v1/contracts",
            params={"status": "active", "limit": 100},
        )
        resp.raise_for_status()
        contracts = resp.json().get("contracts", [])
    
    for contract in contracts:
        check_schema.delay(contract["id"])


def _record_compliance_check(
    contract_id: str,
    check_type: str,
    status: str,
    details: dict,
):
    """Record compliance check result in Contract Service."""
    with httpx.Client() as client:
        client.post(
            f"{settings.contract_service_url}/api/v1/contracts/{contract_id}/compliance",
            json={
                "check_type": check_type,
                "status": status,
                "details": details,
            },
        )


def _send_alert(contract: dict, result: dict):
    """Send alert for compliance failure."""
    # Implement Slack/email notification
    pass
```

---

## Phase 3: Dictionary Service

### Task 3.1: Field Aggregation

**services/dictionary-service/src/dictionary_service/services/aggregator.py:**

```python
from typing import Any
import httpx

from dictionary_service.config import settings


class DictionaryAggregator:
    """Aggregates all contracts into a unified data dictionary."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.contract_service_url)
    
    async def get_full_dictionary(self) -> dict[str, Any]:
        """Build complete data dictionary from all contracts."""
        # Fetch all contracts
        resp = await self.client.get("/api/v1/contracts", params={"limit": 500})
        resp.raise_for_status()
        contracts = resp.json().get("contracts", [])
        
        dictionary = {
            "datasets": [],
            "fields": [],
            "teams": set(),
            "pii_fields": [],
        }
        
        for contract in contracts:
            # Add dataset entry
            dictionary["datasets"].append({
                "name": contract["name"],
                "description": contract.get("description"),
                "publisher": contract["publisher_team"],
                "owner": contract["publisher_owner"],
                "status": contract["status"],
                "version": contract["version"],
                "subscriber_count": len(contract.get("subscribers", [])),
            })
            
            dictionary["teams"].add(contract["publisher_team"])
            
            # Add field entries
            for field in contract.get("fields", []):
                field_entry = {
                    "name": field["name"],
                    "dataset": contract["name"],
                    "data_type": field["data_type"],
                    "description": field.get("description"),
                    "is_pii": field.get("is_pii", False),
                    "nullable": field.get("nullable", True),
                    "example": field.get("example_value"),
                    "publisher_team": contract["publisher_team"],
                }
                dictionary["fields"].append(field_entry)
                
                if field.get("is_pii"):
                    dictionary["pii_fields"].append(field_entry)
            
            # Track subscriber teams
            for sub in contract.get("subscribers", []):
                dictionary["teams"].add(sub["team"])
        
        dictionary["teams"] = sorted(dictionary["teams"])
        dictionary["summary"] = {
            "total_datasets": len(dictionary["datasets"]),
            "total_fields": len(dictionary["fields"]),
            "total_teams": len(dictionary["teams"]),
            "pii_field_count": len(dictionary["pii_fields"]),
        }
        
        return dictionary
    
    async def search_fields(
        self,
        query: str,
        data_type: str | None = None,
        is_pii: bool | None = None,
    ) -> list[dict]:
        """Search fields across all contracts."""
        dictionary = await self.get_full_dictionary()
        
        results = []
        query_lower = query.lower()
        
        for field in dictionary["fields"]:
            # Text match on name or description
            name_match = query_lower in field["name"].lower()
            desc_match = (
                field.get("description") and 
                query_lower in field["description"].lower()
            )
            
            if not (name_match or desc_match):
                continue
            
            # Filter by data type
            if data_type and field["data_type"] != data_type:
                continue
            
            # Filter by PII
            if is_pii is not None and field["is_pii"] != is_pii:
                continue
            
            results.append(field)
        
        return results
    
    async def close(self):
        await self.client.aclose()
```

### Task 3.2: ERD Generator

**services/dictionary-service/src/dictionary_service/services/erd_generator.py:**

```python
from typing import Any
import httpx
from jinja2 import Template

from dictionary_service.config import settings


MERMAID_TEMPLATE = """erDiagram
{% for dataset in datasets %}
    {{ dataset.name }} {
{% for field in dataset.fields %}
        {{ field.data_type }} {{ field.name }}{% if field.is_primary_key %} PK{% endif %}{% if field.is_foreign_key %} FK{% endif %}

{% endfor %}
    }
{% endfor %}

{% for rel in relationships %}
    {{ rel.from_dataset }} {{ rel.cardinality }} {{ rel.to_dataset }} : "{{ rel.label }}"
{% endfor %}
"""


class ERDGenerator:
    """Generates Entity Relationship Diagrams from contracts."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.contract_service_url)
    
    async def generate_mermaid(self) -> str:
        """Generate Mermaid ERD syntax from all contracts."""
        resp = await self.client.get("/api/v1/contracts", params={"limit": 500})
        resp.raise_for_status()
        contracts = resp.json().get("contracts", [])
        
        datasets = []
        relationships = []
        
        # Build dataset entities
        for contract in contracts:
            dataset = {
                "name": self._sanitize_name(contract["name"]),
                "fields": [],
            }
            
            for field in contract.get("fields", []):
                dataset["fields"].append({
                    "name": self._sanitize_name(field["name"]),
                    "data_type": self._map_type(field["data_type"]),
                    "is_primary_key": field.get("is_primary_key", False),
                    "is_foreign_key": field.get("is_foreign_key", False),
                })
                
                # Track foreign key relationships
                if field.get("is_foreign_key") and field.get("foreign_key_reference"):
                    ref_parts = field["foreign_key_reference"].split(".")
                    if len(ref_parts) == 2:
                        relationships.append({
                            "from_dataset": self._sanitize_name(contract["name"]),
                            "to_dataset": self._sanitize_name(ref_parts[0]),
                            "cardinality": "}o--||",  # Many to one
                            "label": field["name"],
                        })
            
            datasets.append(dataset)
        
        # Add publisher/subscriber relationships
        for contract in contracts:
            for subscriber in contract.get("subscribers", []):
                # Check if subscriber team owns any contracts
                for other in contracts:
                    if other["publisher_team"] == subscriber["team"]:
                        relationships.append({
                            "from_dataset": self._sanitize_name(other["name"]),
                            "to_dataset": self._sanitize_name(contract["name"]),
                            "cardinality": "..>",  # Uses/depends on
                            "label": "subscribes",
                        })
        
        # Render template
        template = Template(MERMAID_TEMPLATE)
        return template.render(datasets=datasets, relationships=relationships)
    
    async def generate_json(self) -> dict[str, Any]:
        """Generate ERD as JSON structure."""
        resp = await self.client.get("/api/v1/contracts", params={"limit": 500})
        resp.raise_for_status()
        contracts = resp.json().get("contracts", [])
        
        nodes = []
        edges = []
        
        for contract in contracts:
            nodes.append({
                "id": contract["name"],
                "type": "dataset",
                "label": contract["name"],
                "publisher": contract["publisher_team"],
                "fields": [f["name"] for f in contract.get("fields", [])],
            })
            
            # Foreign key edges
            for field in contract.get("fields", []):
                if field.get("foreign_key_reference"):
                    ref_parts = field["foreign_key_reference"].split(".")
                    if len(ref_parts) == 2:
                        edges.append({
                            "from": contract["name"],
                            "to": ref_parts[0],
                            "type": "foreign_key",
                            "label": field["name"],
                        })
            
            # Subscriber edges
            for subscriber in contract.get("subscribers", []):
                edges.append({
                    "from": subscriber["team"],
                    "to": contract["name"],
                    "type": "subscription",
                    "use_case": subscriber.get("use_case"),
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for Mermaid syntax."""
        return name.replace("-", "_").replace(" ", "_")
    
    def _map_type(self, data_type: str) -> str:
        """Map contract types to ERD display types."""
        mapping = {
            "string": "string",
            "integer": "int",
            "float": "float",
            "decimal": "decimal",
            "boolean": "bool",
            "date": "date",
            "datetime": "datetime",
            "timestamp": "timestamp",
            "uuid": "uuid",
            "json": "json",
        }
        return mapping.get(data_type, data_type)
    
    async def close(self):
        await self.client.aclose()
```

---

## Phase 4: GitHub Integration

### Task 4.1: Webhook Handler

**services/contract-service/src/contract_service/api/routes/webhooks.py:**

```python
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel

from contract_service.config import settings
from contract_service.services.github_service import GitHubService

router = APIRouter()


class PRWebhookPayload(BaseModel):
    action: str
    number: int
    pull_request: dict
    repository: dict


@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    """Handle GitHub webhook events for PR-based contract enforcement."""
    
    # Verify webhook signature
    body = await request.body()
    if settings.github_webhook_secret:
        expected_sig = "sha256=" + hmac.new(
            settings.github_webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        
        if not hmac.compare_digest(x_hub_signature_256 or "", expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    # Handle different event types
    if x_github_event == "pull_request":
        return await _handle_pull_request(payload)
    elif x_github_event == "push":
        return await _handle_push(payload)
    
    return {"status": "ignored", "event": x_github_event}


async def _handle_pull_request(payload: dict):
    """Handle pull request events."""
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    
    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "action": action}
    
    github = GitHubService()
    
    # Get changed files
    changed_files = await github.get_pr_files(
        owner=repo["owner"]["login"],
        repo=repo["name"],
        pr_number=pr["number"],
    )
    
    # Check if schema files changed
    schema_files = [f for f in changed_files if _is_schema_file(f["filename"])]
    contract_files = [f for f in changed_files if _is_contract_file(f["filename"])]
    
    if not schema_files:
        # No schema changes, nothing to enforce
        return {"status": "no_schema_changes"}
    
    if not contract_files:
        # Schema changed but no contract update
        await github.create_check_run(
            owner=repo["owner"]["login"],
            repo=repo["name"],
            head_sha=pr["head"]["sha"],
            name="DataPact Contract Check",
            status="completed",
            conclusion="failure",
            output={
                "title": "Contract Update Required",
                "summary": "Schema changes detected but no contract.yaml update found.",
                "text": (
                    "This PR modifies database schema files but does not include "
                    "an update to the data contract. Please update `contract.yaml` "
                    "to reflect the schema changes.\n\n"
                    f"Changed schema files:\n"
                    + "\n".join(f"- {f['filename']}" for f in schema_files)
                ),
            },
        )
        return {"status": "blocked", "reason": "missing_contract_update"}
    
    # Validate contract changes match schema changes
    validation_result = await _validate_contract_matches_schema(
        github, repo, pr, schema_files, contract_files
    )
    
    if validation_result["valid"]:
        await github.create_check_run(
            owner=repo["owner"]["login"],
            repo=repo["name"],
            head_sha=pr["head"]["sha"],
            name="DataPact Contract Check",
            status="completed",
            conclusion="success",
            output={
                "title": "Contract Valid",
                "summary": "Contract update matches schema changes.",
            },
        )
        return {"status": "approved"}
    else:
        await github.create_check_run(
            owner=repo["owner"]["login"],
            repo=repo["name"],
            head_sha=pr["head"]["sha"],
            name="DataPact Contract Check",
            status="completed",
            conclusion="failure",
            output={
                "title": "Contract Validation Failed",
                "summary": validation_result["message"],
                "text": "\n".join(validation_result.get("errors", [])),
            },
        )
        return {"status": "blocked", "reason": "validation_failed"}


async def _handle_push(payload: dict):
    """Handle push events (merged PRs)."""
    ref = payload.get("ref", "")
    repo = payload.get("repository", {})
    
    # Only process pushes to main/master
    if ref not in ["refs/heads/main", "refs/heads/master"]:
        return {"status": "ignored", "ref": ref}
    
    # Check if contract file was updated
    commits = payload.get("commits", [])
    contract_updated = any(
        _is_contract_file(f)
        for commit in commits
        for f in commit.get("modified", []) + commit.get("added", [])
    )
    
    if contract_updated:
        # Sync contract to Contract Service
        github = GitHubService()
        contract_content = await github.get_file_content(
            owner=repo["owner"]["login"],
            repo=repo["name"],
            path="contract.yaml",
            ref=ref.split("/")[-1],
        )
        
        # Update contract in database
        # (Implementation in contract_service)
        
    return {"status": "processed"}


def _is_schema_file(filename: str) -> bool:
    """Check if file is a database schema file."""
    schema_patterns = [
        "alembic/versions/",
        "migrations/",
        "schema.sql",
        "models.py",
        "models/",
    ]
    return any(p in filename for p in schema_patterns)


def _is_contract_file(filename: str) -> bool:
    """Check if file is a contract file."""
    return filename.endswith("contract.yaml") or filename.endswith("contract.yml")


async def _validate_contract_matches_schema(
    github: GitHubService,
    repo: dict,
    pr: dict,
    schema_files: list,
    contract_files: list,
) -> dict:
    """Validate that contract changes properly reflect schema changes."""
    # This would parse the schema changes and contract changes
    # and verify they're consistent
    # Simplified implementation:
    return {"valid": True}
```

---

## Testing Requirements

### Unit Tests

Each service should have comprehensive unit tests:

```python
# services/contract-service/tests/test_contracts.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from contract_service.main import app
from contract_service.models.contract import Contract


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_contract():
    return {
        "name": "test_orders",
        "version": "1.0.0",
        "description": "Test orders dataset",
        "publisher": {
            "team": "commerce",
            "owner": "orders-service",
        },
        "schema": [
            {
                "name": "order_id",
                "data_type": "uuid",
                "description": "Unique order identifier",
                "nullable": False,
                "is_primary_key": True,
            },
            {
                "name": "total",
                "data_type": "decimal",
                "nullable": False,
            },
        ],
        "quality": [
            {
                "metric_type": "freshness",
                "threshold": "15 minutes",
            },
        ],
    }


@pytest.mark.asyncio
async def test_create_contract(client, sample_contract):
    response = await client.post("/api/v1/contracts", json=sample_contract)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_orders"
    assert len(data["fields"]) == 2


@pytest.mark.asyncio
async def test_get_contract(client, sample_contract):
    # Create first
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]
    
    # Then retrieve
    response = await client.get(f"/api/v1/contracts/{contract_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "test_orders"


@pytest.mark.asyncio
async def test_duplicate_contract_name(client, sample_contract):
    await client.post("/api/v1/contracts", json=sample_contract)
    response = await client.post("/api/v1/contracts", json=sample_contract)
    assert response.status_code == 409
```

### Integration Tests

```python
# services/compliance-monitor/tests/test_schema_validation.py

import pytest
from compliance_monitor.checks.schema_validator import SchemaValidator
from datapact_common.contract_schema import ContractDefinition


@pytest.fixture
def sample_contract():
    return ContractDefinition(
        name="test_dataset",
        version="1.0.0",
        publisher={"team": "test", "owner": "test-svc"},
        schema=[
            {"name": "id", "data_type": "uuid", "nullable": False},
            {"name": "name", "data_type": "string", "nullable": False},
            {"name": "created_at", "data_type": "timestamp", "nullable": False},
        ],
    )


def test_valid_schema(sample_contract):
    actual_schema = {
        "tables": {
            "main_table": {
                "columns": [
                    {"name": "id", "type": "uuid", "nullable": False},
                    {"name": "name", "type": "varchar(255)", "nullable": False},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                ]
            }
        }
    }
    
    validator = SchemaValidator(sample_contract)
    assert validator.validate(actual_schema) is True
    assert len(validator.errors) == 0


def test_missing_field(sample_contract):
    actual_schema = {
        "tables": {
            "main_table": {
                "columns": [
                    {"name": "id", "type": "uuid", "nullable": False},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                ]
            }
        }
    }
    
    validator = SchemaValidator(sample_contract)
    assert validator.validate(actual_schema) is False
    assert "Missing required field: name" in validator.errors


def test_type_mismatch(sample_contract):
    actual_schema = {
        "tables": {
            "main_table": {
                "columns": [
                    {"name": "id", "type": "integer", "nullable": False},  # Wrong type
                    {"name": "name", "type": "varchar(255)", "nullable": False},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                ]
            }
        }
    }
    
    validator = SchemaValidator(sample_contract)
    assert validator.validate(actual_schema) is False
    assert any("Type mismatch" in e for e in validator.errors)
```

---

## Development Workflow

### Initial Setup

```bash
# Clone and setup
git clone <repo>
cd datapact

# Copy environment file
cp .env.example .env

# Build all containers
docker-compose build

# Start infrastructure first
docker-compose up -d postgres redis

# Wait for postgres to be ready, then run migrations
docker-compose run --rm contract-service alembic upgrade head

# Start all services
docker-compose up

# Or start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### Adding a New Contract

```bash
# Via API
curl -X POST http://localhost:8001/api/v1/contracts \
  -H "Content-Type: application/json" \
  -d @contract.json

# Via CLI (future)
datapact contract create --file contract.yaml
```

---

## Iteration Checklist

Use this checklist to track progress:

### Phase 1: Foundation
- [ ] Repository structure created
- [ ] Shared library implemented (`datapact_common`)
- [ ] Contract Service database schema
- [ ] Contract Service CRUD API
- [ ] Template Data Microservice with `/schema`, `/metrics`, `/health`
- [ ] Docker Compose configuration
- [ ] Basic unit tests

### Phase 2: Compliance
- [ ] Celery worker setup
- [ ] Schema validation logic
- [ ] Quality metric checks (freshness, completeness)
- [ ] Compliance check recording
- [ ] Scheduled monitoring tasks
- [ ] Slack/email alerting

### Phase 3: Dictionary
- [ ] Field aggregation service
- [ ] Search API
- [ ] ERD generation (Mermaid)
- [ ] ERD generation (JSON for UI)
- [ ] Dictionary API endpoints

### Phase 4: GitHub Integration
- [ ] Webhook handler
- [ ] PR file analysis
- [ ] Check run creation
- [ ] Contract sync on merge
- [ ] Branch protection guidance

### Phase 5: Alerting System
- [ ] Notification service scaffold
- [ ] Database schema (notifications, watchers)
- [ ] Event schema definitions
- [ ] Recipient resolver logic
- [ ] Email templates (schema_drift, quality_breach, pr_blocked, contract_updated, deprecation)
- [ ] SMTP email sender
- [ ] Celery task for async sending
- [ ] Event emission from Compliance Monitor
- [ ] Event emission from Contract Service
- [ ] Event emission from GitHub webhook handler
- [ ] Notification preferences API
- [ ] Watcher management API
- [ ] Deduplication logic
- [ ] Rate limiting

### Phase 6: Frontend
- [ ] Project scaffold (Vite + React + TypeScript)
- [ ] Tailwind CSS + shadcn/ui setup
- [ ] API client configuration
- [ ] Type definitions
- [ ] React Query hooks
- [ ] Layout components (Sidebar, Header)
- [ ] Dashboard page with stats
- [ ] Contracts list page
- [ ] Contract detail page with tabs
- [ ] Contract create/edit form
- [ ] Data dictionary page with search
- [ ] ERD visualization with React Flow
- [ ] Compliance dashboard with charts
- [ ] Notification history page
- [ ] Settings page
- [ ] Docker configuration + nginx proxy

### Phase 7: Polish
- [ ] Web UI for dictionary browsing
- [ ] Contract editor UI
- [ ] Compliance dashboard
- [ ] Documentation
- [ ] CI/CD pipeline

---

## Notes for Claude Code

1. **Start with the shared library** - `datapact_common` defines the canonical contract schema used everywhere
2. **Build services incrementally** - Get Contract Service working first, then add compliance monitoring
3. **Test as you go** - Write tests alongside implementation
4. **Use async throughout** - FastAPI + SQLAlchemy async for all database operations
5. **Keep contracts as YAML** - Human-readable, git-friendly
6. **Version everything** - Contracts, APIs, and the platform itself

When implementing, feel free to ask for clarification on any component or to dive deeper into specific implementation details.
