"""Data CRUD endpoints for the example dataset."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.database import get_db
from data_service.models import ExampleData
from data_service.schemas import ExampleDataCreate, ExampleDataResponse

router = APIRouter()


@router.get("/data", response_model=list[ExampleDataResponse])
async def list_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all data entries with optional filtering."""
    query = select(ExampleData)

    if category:
        query = query.where(ExampleData.category == category)
    if is_active is not None:
        query = query.where(ExampleData.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(ExampleData.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/data/{data_id}", response_model=ExampleDataResponse)
async def get_data(
    data_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific data entry by ID."""
    result = await db.execute(select(ExampleData).where(ExampleData.id == data_id))
    data = result.scalar_one_or_none()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data entry {data_id} not found",
        )
    return data


@router.post("/data", response_model=ExampleDataResponse, status_code=status.HTTP_201_CREATED)
async def create_data(
    data: ExampleDataCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new data entry."""
    entry = ExampleData(
        name=data.name,
        description=data.description,
        value=data.value,
        category=data.category,
        is_active=data.is_active,
    )
    db.add(entry)
    await db.flush()
    return entry


@router.delete("/data/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data(
    data_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a data entry."""
    result = await db.execute(select(ExampleData).where(ExampleData.id == data_id))
    data = result.scalar_one_or_none()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data entry {data_id} not found",
        )

    await db.delete(data)
    await db.flush()


@router.get("/data/stats/summary")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get summary statistics for the dataset."""
    result = await db.execute(
        select(
            func.count(ExampleData.id).label("total_count"),
            func.sum(ExampleData.value).label("total_value"),
            func.avg(ExampleData.value).label("avg_value"),
        )
    )
    row = result.fetchone()

    return {
        "total_count": row.total_count or 0,
        "total_value": float(row.total_value) if row.total_value else 0,
        "average_value": float(row.avg_value) if row.avg_value else 0,
    }
