# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataPact is a contract-driven data governance platform built as a microservices architecture. It enforces data contracts between publishers and subscribers, providing schema validation, compliance monitoring, and alerting.

## Quick Start

```bash
docker-compose up -d postgres redis    # Start infrastructure
docker-compose up --build              # Build and run all services
```

Access points:
- Contract Service: http://localhost:8001
- Dictionary Service: http://localhost:8002
- Notification Service: http://localhost:8003
- Template Data Service: http://localhost:8010
- Frontend: http://localhost:3000
- MailHog (email testing): http://localhost:8025

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   Frontend  │────▶│  Contract Service │────▶│  PostgreSQL        │
│  (React)    │     │  (Central API)    │     │  (contracts db)    │
└─────────────┘     └──────────────────┘     └────────────────────┘
                           │                           │
        ┌──────────────────┼──────────────────┐       │
        ▼                  ▼                  ▼       │
┌───────────────┐  ┌───────────────┐  ┌──────────────┐
│  Dictionary   │  │  Notification │  │  Compliance  │
│  Service      │  │  Service      │  │  Monitor     │
└───────────────┘  └───────────────┘  │  (Celery)    │
                          │            └──────────────┘
                          ▼                    │
                   ┌──────────┐         ┌──────────┐
                   │  Redis   │◀────────│  Redis   │
                   │  (queue) │         │  (broker)│
                   └──────────┘         └──────────┘
```

**Service dependencies:**
- All services depend on `datapact_common` (shared Pydantic models in `shared/datapact_common/`)
- Dictionary, Notification, and Compliance services call Contract Service API
- Celery workers (compliance-worker, notification-worker) use Redis as broker

## Service Communication

**Dictionary Service has no database.** It aggregates data by calling the Contract Service API (`/api/v1/contracts?limit=500`) on every request via `DictionaryAggregator`. The aggregator builds in-memory dictionaries, ERDs, and search indexes from contract data. Changes here require restarting `dictionary-service`.

**Compliance Monitor uses Celery Beat** with this schedule:
- `check-all-schemas`: every 5 minutes
- `check-all-quality`: every 15 minutes
- `check-all-availability`: every minute

**Frontend uses three separate axios clients** (`frontend/src/api/client.ts`):
- `apiClient` → Contract Service (port 8001)
- `dictionaryClient` → Dictionary Service (port 8002)
- `notificationClient` → Notification Service (port 8003)

Env vars: `VITE_API_BASE_URL`, `VITE_DICTIONARY_API_URL`, `VITE_NOTIFICATION_API_URL` (defaults to localhost ports above).

## Contract Service API (Key Endpoints)

The contract create/update payload uses nested objects that differ from the flat database columns:

```json
{
  "name": "orders",
  "version": "1.0.0",
  "status": "draft",
  "publisher": { "team": "...", "owner": "..." },
  "schema": [{ "name": "id", "data_type": "integer", ... }],
  "quality": [{ "metric_type": "completeness", "threshold": "99%", ... }],
  "tags": ["commerce"]
}
```

The Pydantic schema uses aliases: `schema_fields` → alias `"schema"`, `quality_metrics` → alias `"quality"`, publisher fields are nested via `PublisherInfo` model. **Responses return flat fields**: `publisher_team`, `publisher_owner`, `fields`, `quality_metrics`.

**Dictionary Service ERD endpoints** are at `/api/v1/erd/json` and `/api/v1/erd/mermaid` (NOT `/api/v1/erd?format=json`).

## SQLAlchemy Metadata Conflict

The `Contract` model uses `metadata_` as the Python attribute with `"metadata"` as the column name to avoid colliding with SQLAlchemy's class-level `metadata` attribute. In Pydantic response schemas, use `serialization_alias="metadata"` (not `alias="metadata"`) to prevent Pydantic from reading SQLAlchemy's `MetaData()` object instead of the column value.

## Development Commands

**All commands must run inside Docker containers.** Never run services directly on the host.

### Docker

| Command | Purpose |
|---------|---------|
| `docker-compose exec <service> bash` | Shell into container |
| `docker-compose logs -f <service>` | Tail logs |
| `docker-compose restart <service>` | Restart single service |
| `docker-compose down -v` | Stop and remove volumes |

### Poetry (inside container)

| Command | Purpose |
|---------|---------|
| `poetry add <pkg>` | Add runtime dependency |
| `poetry add --group dev <pkg>` | Add dev dependency |
| `poetry run pytest` | Run tests |
| `poetry run pytest --cov` | Run with coverage |
| `poetry run ruff check .` | Lint |
| `poetry run mypy .` | Type check |

### Alembic (inside container)

| Command | Purpose |
|---------|---------|
| `alembic revision --autogenerate -m "desc"` | Create migration from model changes |
| `alembic upgrade head` | Apply all migrations |
| `alembic downgrade -1` | Rollback one migration |
| `alembic history` | Show migration history |

## Code Style

Configured in root `pyproject.toml`:
- **ruff**: line-length=100, target-version=py311, select=["E","F","I","N","W","UP","B","C4","SIM"]
- **mypy**: strict=true

Frontend uses ESLint with TypeScript rules.

## Key Files

| Purpose | Location |
|---------|----------|
| Contract schema (Pydantic models) | `shared/datapact_common/src/datapact_common/contract_schema.py` |
| Contract Service SQLAlchemy models | `services/contract-service/src/contract_service/models/` |
| Contract Service Pydantic schemas | `services/contract-service/src/contract_service/schemas/` |
| Dictionary aggregator | `services/dictionary-service/src/dictionary_service/services/aggregator.py` |
| ERD generator | `services/dictionary-service/src/dictionary_service/services/erd_generator.py` |
| Celery beat schedule | `services/compliance-monitor/src/compliance_monitor/celery_app.py` |
| Notification templates | `services/notification-service/src/notification_service/templates/` |
| Frontend API clients | `frontend/src/api/client.ts` |
| Frontend React Query hooks | `frontend/src/hooks/` |
| Frontend form validation | `frontend/src/lib/validations/` |
| Frontend constants (DATA_TYPES, etc.) | `frontend/src/lib/constants.ts` |

## Database URLs

| Service | Database |
|---------|----------|
| contract-service | `postgresql+asyncpg://datapact:datapact_dev@postgres:5432/contracts` |
| template-data-service | `postgresql+asyncpg://datapact:datapact_dev@postgres:5432/template_data` |
| notification-service | `postgresql+asyncpg://datapact:datapact_dev@postgres:5432/notifications` |

## Critical Patterns

1. **Async everywhere** - All database ops use `async/await` with AsyncSession
2. **Poetry only** - Never use pip or requirements.txt
3. **Alembic only** - Never write manual SQL for schema changes
4. **Docker required** - Services communicate via Docker network names (e.g., `http://contract-service:8000`). Internal port is always 8000; external ports differ (8001, 8002, 8003).
5. **Soft deletes** - Contracts are deprecated, not deleted
6. **Version snapshots** - Every contract update creates a ContractVersion record
7. **Shared package** - Changes to `datapact_common` require rebuilding ALL services
8. **Pagination limit** - Contract list endpoint caps at `limit=500`

## Frontend Patterns

- **Forms**: react-hook-form + zod + @hookform/resolvers. Dynamic arrays via `useFieldArray`.
- **Data fetching**: TanStack Query with hooks in `src/hooks/`. Mutations auto-invalidate query cache.
- **UI components**: shadcn/ui (in `src/components/ui/`). Dialog, Tabs, Card, Table, Select, Switch, etc.
- **Routing**: react-router-dom v6. Place specific routes before parameterized routes (`/contracts/new` before `/contracts/:id`).
- **Toast notifications**: `useToast()` hook from `src/hooks/useToast.ts`.
- **ERD visualization**: React Flow with custom `DatasetNode` component.

## Adding a New Service Endpoint

1. Add SQLAlchemy model in `models/`
2. Add Pydantic schema in `schemas/`
3. Create Alembic migration: `alembic revision --autogenerate -m "add xyz"`
4. Apply migration: `alembic upgrade head`
5. Add route in `api/routes/`
6. Register router in `main.py`

## Running Tests

```bash
docker-compose exec contract-service pytest -v
docker-compose exec contract-service pytest tests/test_contracts.py::test_create_contract -v
```

## Frontend Development

```bash
cd frontend
npm install
npm run dev          # Start dev server with hot-reload
npm run build        # Production build
npm run lint         # ESLint check
```

Tech stack: React 18, TypeScript, Vite, TanStack Query, Tailwind CSS, shadcn/ui, React Flow, Recharts

## Azure Deployment

Infrastructure is defined in `infrastructure/terraform/`. GitHub Actions workflows handle CI/CD.

### Terraform Resources

| File | Resources |
|------|-----------|
| `datapact.tf` | 8 web apps (4 services, 3 workers, 1 frontend) |
| `redis.tf` | Azure Cache for Redis |
| `communication.tf` | Azure Communication Services (email) |
| `database.tf` | PostgreSQL + 3 DataPact databases |

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy-azure.yml` | Push to main | Build images, deploy to App Service, run migrations |
| `terraform.yml` | Changes to `infrastructure/terraform/` | Plan/Apply infrastructure |

### Required GitHub Secrets

`AZURE_CREDENTIALS`, `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_SUBSCRIPTION_ID`, `ARM_TENANT_ID`, `DB_ADMIN_PASSWORD`

### Required GitHub Variables

`AZURE_RESOURCE_GROUP`, `ACR_NAME`, `PROJECT_NAME`, `DATAPACT_EMAIL_DOMAIN`

### Email Provider Configuration

The notification service supports two email providers configured via `EMAIL_PROVIDER` env var:
- `smtp` (default) - Uses SMTP settings for local dev with MailHog
- `azure` - Uses Azure Communication Services (production)

Azure email requires `ACS_CONNECTION_STRING` and `ACS_SENDER_ADDRESS` env vars.

### Azure URL Pattern

All services use predictable hostnames: `https://{PROJECT_NAME}-datapact-{service}.azurewebsites.net`
