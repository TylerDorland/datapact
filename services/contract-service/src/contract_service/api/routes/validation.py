"""Validation and compliance API routes."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from contract_service.api.dependencies import get_db
from contract_service.services.contract_service import ContractCRUD

router = APIRouter()


class ComplianceCheckRequest(BaseModel):
    """Request body for recording a compliance check."""

    check_type: str
    status: str  # pass, fail, warning, error
    details: dict[str, Any] = {}
    error_message: str | None = None


class ComplianceCheckResponse(BaseModel):
    """Response for a compliance check record."""

    id: UUID
    contract_id: UUID
    check_type: str
    status: str
    details: dict[str, Any]
    error_message: str | None

    model_config = {"from_attributes": True}


@router.post(
    "/{contract_id}/compliance",
    response_model=ComplianceCheckResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_compliance_check(
    contract_id: UUID,
    check: ComplianceCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    """Record a compliance check result for a contract."""
    crud = ContractCRUD(db)

    # Verify contract exists
    contract = await crud.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )

    result = await crud.record_compliance_check(
        contract_id=contract_id,
        check_type=check.check_type,
        status=check.status,
        details=check.details,
        error_message=check.error_message,
    )
    return result


@router.post("/{contract_id}/validate")
async def validate_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate a contract against its data service.
    This is a placeholder for Phase 2 implementation.
    """
    crud = ContractCRUD(db)

    contract = await crud.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )

    # Placeholder response - actual validation will be implemented in Phase 2
    return {
        "contract_id": str(contract_id),
        "contract_name": contract.name,
        "message": "Validation endpoint placeholder - implement in Phase 2",
        "status": "pending",
    }
