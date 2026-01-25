"""Field management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contract_service.api.dependencies import get_db
from contract_service.models import Contract, ContractField
from contract_service.schemas.field import FieldCreate, FieldResponse, FieldUpdate

router = APIRouter()


@router.get("/{contract_id}/fields", response_model=list[FieldResponse])
async def list_fields(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all fields for a contract."""
    result = await db.execute(
        select(ContractField).where(ContractField.contract_id == contract_id)
    )
    fields = result.scalars().all()
    return fields


@router.get("/{contract_id}/fields/{field_id}", response_model=FieldResponse)
async def get_field(
    contract_id: UUID,
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific field."""
    result = await db.execute(
        select(ContractField).where(
            ContractField.id == field_id,
            ContractField.contract_id == contract_id,
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found",
        )
    return field


@router.post(
    "/{contract_id}/fields",
    response_model=FieldResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_field(
    contract_id: UUID,
    field_data: FieldCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a field to a contract."""
    # Verify contract exists
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )

    # Check for duplicate field name
    existing = await db.execute(
        select(ContractField).where(
            ContractField.contract_id == contract_id,
            ContractField.name == field_data.name,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Field '{field_data.name}' already exists in this contract",
        )

    field = ContractField(
        contract_id=contract_id,
        name=field_data.name,
        data_type=field_data.data_type,
        description=field_data.description,
        nullable=field_data.nullable,
        is_pii=field_data.is_pii,
        is_primary_key=field_data.is_primary_key,
        is_foreign_key=field_data.is_foreign_key,
        foreign_key_reference=field_data.foreign_key_reference,
        example_value=field_data.example_value,
        constraints=[c.model_dump() for c in field_data.constraints],
    )
    db.add(field)
    await db.flush()

    return field


@router.patch("/{contract_id}/fields/{field_id}", response_model=FieldResponse)
async def update_field(
    contract_id: UUID,
    field_id: UUID,
    field_update: FieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a field."""
    result = await db.execute(
        select(ContractField).where(
            ContractField.id == field_id,
            ContractField.contract_id == contract_id,
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found",
        )

    if field_update.description is not None:
        field.description = field_update.description
    if field_update.nullable is not None:
        field.nullable = field_update.nullable
    if field_update.is_pii is not None:
        field.is_pii = field_update.is_pii
    if field_update.example_value is not None:
        field.example_value = field_update.example_value
    if field_update.constraints is not None:
        field.constraints = [c.model_dump() for c in field_update.constraints]

    await db.flush()
    return field


@router.delete(
    "/{contract_id}/fields/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_field(
    contract_id: UUID,
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a field from a contract."""
    result = await db.execute(
        select(ContractField).where(
            ContractField.id == field_id,
            ContractField.contract_id == contract_id,
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found",
        )

    await db.delete(field)
    await db.flush()
