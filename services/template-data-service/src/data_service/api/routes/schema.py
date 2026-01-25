"""Schema endpoint for compliance monitoring."""

from fastapi import APIRouter, Depends
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.config import settings
from data_service.database import get_db

router = APIRouter()


@router.get("/schema")
async def get_schema(db: AsyncSession = Depends(get_db)):
    """
    Return the current database schema.
    This endpoint is polled by the Compliance Monitor.
    """
    # Get the raw connection for inspection
    connection = await db.connection()
    raw_conn = await connection.get_raw_connection()

    # Use synchronous inspection
    def inspect_schema(sync_conn):
        inspector = inspect(sync_conn)
        tables = {}

        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": str(col.get("default")) if col.get("default") else None,
                    "primary_key": False,  # Will be updated below
                })

            # Get primary key columns
            pk = inspector.get_pk_constraint(table_name)
            pk_columns = pk.get("constrained_columns", []) if pk else []
            for col in columns:
                if col["name"] in pk_columns:
                    col["primary_key"] = True

            # Get foreign keys
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                fks.append({
                    "columns": fk["constrained_columns"],
                    "references": f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                    if fk.get("referred_columns")
                    else None,
                })

            tables[table_name] = {
                "columns": columns,
                "foreign_keys": fks,
            }

        return tables

    # Run inspection synchronously through the async connection
    tables = await connection.run_sync(
        lambda sync_conn: inspect_schema(sync_conn)
    )

    return {
        "service": settings.service_name,
        "contract_name": settings.contract_name,
        "tables": tables,
    }
