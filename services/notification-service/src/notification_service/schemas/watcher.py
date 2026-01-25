"""Watcher schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WatcherCreate(BaseModel):
    """Schema for creating a watcher."""

    # What to watch (at least one required)
    contract_id: UUID | None = None
    contract_name: str | None = None
    publisher_team: str | None = None
    tag: str | None = None

    # Who is watching
    watcher_email: str
    watcher_team: str | None = None

    # What events to watch
    watch_schema_drift: bool = True
    watch_quality_breach: bool = True
    watch_contract_updated: bool = True
    watch_deprecation: bool = True
    watch_pr_blocked: bool = False

    # Options
    notify_on_warning: bool = False
    reason: str | None = None
    metadata: dict = Field(default_factory=dict)


class WatcherUpdate(BaseModel):
    """Schema for updating a watcher."""

    watch_schema_drift: bool | None = None
    watch_quality_breach: bool | None = None
    watch_contract_updated: bool | None = None
    watch_deprecation: bool | None = None
    watch_pr_blocked: bool | None = None
    is_active: bool | None = None
    notify_on_warning: bool | None = None
    reason: str | None = None


class WatcherResponse(BaseModel):
    """Schema for watcher response."""

    id: UUID
    contract_id: UUID | None = None
    contract_name: str | None = None
    publisher_team: str | None = None
    tag: str | None = None
    watcher_email: str
    watcher_team: str | None = None
    watch_schema_drift: bool
    watch_quality_breach: bool
    watch_contract_updated: bool
    watch_deprecation: bool
    watch_pr_blocked: bool
    is_active: bool
    notify_on_warning: bool
    reason: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WatcherListResponse(BaseModel):
    """Schema for watcher list response."""

    items: list[WatcherResponse]
    total: int
    offset: int
    limit: int
