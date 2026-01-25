"""Watcher management API routes."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.database import get_session
from notification_service.models.watcher import Watcher
from notification_service.schemas.watcher import (
    WatcherCreate,
    WatcherUpdate,
    WatcherResponse,
    WatcherListResponse,
)

router = APIRouter(prefix="/watchers", tags=["watchers"])


@router.post("", response_model=WatcherResponse, status_code=status.HTTP_201_CREATED)
async def create_watcher(
    data: WatcherCreate,
    session: AsyncSession = Depends(get_session),
) -> Watcher:
    """
    Create a new watcher subscription.

    Watchers allow users to subscribe to notifications for specific contracts,
    teams, or tags they don't directly own or subscribe to.
    """
    # Validate that at least one target is specified
    if not data.contract_id and not data.publisher_team and not data.tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of contract_id, publisher_team, or tag must be specified",
        )

    # Check for duplicate watcher
    query = select(Watcher).where(Watcher.watcher_email == data.watcher_email)

    if data.contract_id:
        query = query.where(Watcher.contract_id == data.contract_id)
    if data.publisher_team:
        query = query.where(Watcher.publisher_team == data.publisher_team)
    if data.tag:
        query = query.where(Watcher.tag == data.tag)

    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Watcher already exists for this combination",
        )

    watcher = Watcher(**data.model_dump())
    session.add(watcher)
    await session.commit()
    await session.refresh(watcher)

    return watcher


@router.get("", response_model=WatcherListResponse)
async def list_watchers(
    email: str | None = Query(None, description="Filter by watcher email"),
    contract_id: UUID | None = Query(None, description="Filter by contract ID"),
    publisher_team: str | None = Query(None, description="Filter by publisher team"),
    tag: str | None = Query(None, description="Filter by tag"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """List watchers with optional filters."""
    query = select(Watcher)

    if email:
        query = query.where(Watcher.watcher_email == email)
    if contract_id:
        query = query.where(Watcher.contract_id == contract_id)
    if publisher_team:
        query = query.where(Watcher.publisher_team == publisher_team)
    if tag:
        query = query.where(Watcher.tag == tag)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # Get paginated results
    query = query.order_by(Watcher.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    watchers = result.scalars().all()

    return {
        "items": watchers,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{watcher_id}", response_model=WatcherResponse)
async def get_watcher(
    watcher_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Watcher:
    """Get a single watcher by ID."""
    result = await session.execute(
        select(Watcher).where(Watcher.id == watcher_id)
    )
    watcher = result.scalar_one_or_none()

    if not watcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watcher not found",
        )

    return watcher


@router.put("/{watcher_id}", response_model=WatcherResponse)
async def update_watcher(
    watcher_id: UUID,
    data: WatcherUpdate,
    session: AsyncSession = Depends(get_session),
) -> Watcher:
    """Update a watcher's notification settings."""
    result = await session.execute(
        select(Watcher).where(Watcher.id == watcher_id)
    )
    watcher = result.scalar_one_or_none()

    if not watcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watcher not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(watcher, field, value)

    await session.commit()
    await session.refresh(watcher)

    return watcher


@router.delete("/{watcher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watcher(
    watcher_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a watcher subscription."""
    result = await session.execute(
        select(Watcher).where(Watcher.id == watcher_id)
    )
    watcher = result.scalar_one_or_none()

    if not watcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watcher not found",
        )

    await session.delete(watcher)
    await session.commit()


@router.get("/by-email/{email}", response_model=WatcherListResponse)
async def get_watchers_by_email(
    email: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Get all watchers for a specific email address."""
    query = select(Watcher).where(Watcher.watcher_email == email)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    query = query.order_by(Watcher.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    watchers = result.scalars().all()

    return {
        "items": watchers,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/by-contract/{contract_id}", response_model=WatcherListResponse)
async def get_watchers_by_contract(
    contract_id: UUID,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Get all watchers for a specific contract."""
    query = select(Watcher).where(Watcher.contract_id == contract_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    query = query.order_by(Watcher.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    watchers = result.scalars().all()

    return {
        "items": watchers,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
