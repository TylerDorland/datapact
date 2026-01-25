"""Contract CRUD API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from contract_service.api.dependencies import get_db
from contract_service.schemas.contract import (
    ContractCreate,
    ContractListResponse,
    ContractResponse,
    ContractUpdate,
    ContractVersionResponse,
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
    limit: int = Query(50, ge=1, le=500),
    status: str | None = Query(None, description="Filter by status (active, deprecated, draft)"),
    publisher_team: str | None = Query(None, description="Filter by publisher team"),
    tag: str | None = Query(None, description="Filter by tag"),
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
    """Update a contract. Creates a new version snapshot."""
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


@router.get("/{contract_id}/versions", response_model=list[ContractVersionResponse])
async def get_contract_versions(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get version history for a contract."""
    crud = ContractCRUD(db)

    # Verify contract exists
    contract = await crud.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )

    versions = await crud.get_versions(contract_id)
    return versions
