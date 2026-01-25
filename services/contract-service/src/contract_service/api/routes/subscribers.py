"""Subscriber management API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from contract_service.api.dependencies import get_db
from contract_service.schemas.subscriber import SubscriberCreate, SubscriberResponse
from contract_service.services.contract_service import ContractCRUD

router = APIRouter()


@router.get("/{contract_id}/subscribers", response_model=list[SubscriberResponse])
async def list_subscribers(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all subscribers for a contract."""
    crud = ContractCRUD(db)

    # Verify contract exists
    contract = await crud.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )

    subscribers = await crud.get_subscribers(contract_id)
    return subscribers


@router.post(
    "/{contract_id}/subscribers",
    response_model=SubscriberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_subscriber(
    contract_id: UUID,
    subscriber_data: SubscriberCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a subscriber to a contract."""
    crud = ContractCRUD(db)

    # Verify contract exists
    contract = await crud.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found",
        )

    # Check for existing subscription from same team
    existing = [s for s in contract.subscribers if s.team == subscriber_data.team]
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team '{subscriber_data.team}' is already subscribed to this contract",
        )

    subscriber = await crud.add_subscriber(
        contract_id=contract_id,
        team=subscriber_data.team,
        use_case=subscriber_data.use_case,
        fields_used=subscriber_data.fields_used,
        contact_email=subscriber_data.contact_email,
    )
    return subscriber


@router.delete(
    "/{contract_id}/subscribers/{subscriber_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_subscriber(
    contract_id: UUID,
    subscriber_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Remove a subscriber from a contract."""
    crud = ContractCRUD(db)

    success = await crud.remove_subscriber(contract_id, subscriber_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscriber {subscriber_id} not found",
        )
