"""Contract CRUD operations and business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from contract_service.models import (
    AccessConfig,
    ComplianceCheck,
    Contract,
    ContractField,
    ContractVersion,
    QualityMetric,
    Subscriber,
)
from contract_service.schemas import (
    ContractCreate,
    ContractUpdate,
)


class ContractCRUD:
    """CRUD operations for contracts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, contract_data: ContractCreate) -> Contract:
        """Create a new contract with all nested entities."""
        # Create the contract
        contract = Contract(
            name=contract_data.name,
            version=contract_data.version,
            description=contract_data.description,
            status=contract_data.status,
            publisher_team=contract_data.publisher.team,
            publisher_owner=contract_data.publisher.owner,
            repository_url=contract_data.publisher.repository_url,
            contact_email=contract_data.publisher.contact_email,
            tags=contract_data.tags,
            metadata_=contract_data.metadata,
        )
        self.db.add(contract)
        await self.db.flush()  # Get the contract ID

        # Create fields
        for field_data in contract_data.schema_fields:
            field = ContractField(
                contract_id=contract.id,
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
            self.db.add(field)

        # Create quality metrics
        for metric_data in contract_data.quality:
            metric = QualityMetric(
                contract_id=contract.id,
                metric_type=metric_data.metric_type,
                threshold=metric_data.threshold,
                measurement_method=metric_data.measurement_method,
                alert_on_breach=metric_data.alert_on_breach,
            )
            self.db.add(metric)

        # Create access config if provided
        if contract_data.access:
            access = AccessConfig(
                contract_id=contract.id,
                endpoint_url=contract_data.access.endpoint_url,
                methods=contract_data.access.methods,
                auth_type=contract_data.access.auth_type,
                required_scopes=contract_data.access.required_scopes,
                rate_limit=contract_data.access.rate_limit,
            )
            self.db.add(access)

        # Create subscribers
        for sub_data in contract_data.subscribers:
            subscriber = Subscriber(
                contract_id=contract.id,
                team=sub_data.team,
                use_case=sub_data.use_case,
                fields_used=sub_data.fields_used,
                contact_email=sub_data.contact_email,
            )
            self.db.add(subscriber)

        await self.db.flush()

        # Return with all relationships loaded
        return await self.get(contract.id)

    async def get(self, contract_id: UUID) -> Contract | None:
        """Get a contract by ID with all relationships."""
        result = await self.db.execute(
            select(Contract)
            .options(
                selectinload(Contract.fields),
                selectinload(Contract.quality_metrics),
                selectinload(Contract.access_config),
                selectinload(Contract.subscribers),
            )
            .where(Contract.id == contract_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Contract | None:
        """Get a contract by name with all relationships."""
        result = await self.db.execute(
            select(Contract)
            .options(
                selectinload(Contract.fields),
                selectinload(Contract.quality_metrics),
                selectinload(Contract.access_config),
                selectinload(Contract.subscribers),
            )
            .where(Contract.name == name)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        publisher_team: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[Contract], int]:
        """List contracts with filtering and pagination."""
        query = select(Contract).options(
            selectinload(Contract.fields),
            selectinload(Contract.quality_metrics),
            selectinload(Contract.access_config),
            selectinload(Contract.subscribers),
        )

        # Apply filters
        if status:
            query = query.where(Contract.status == status)
        if publisher_team:
            query = query.where(Contract.publisher_team == publisher_team)
        if tag:
            query = query.where(Contract.tags.contains([tag]))

        # Get total count
        count_query = select(func.count(Contract.id))
        if status:
            count_query = count_query.where(Contract.status == status)
        if publisher_team:
            count_query = count_query.where(Contract.publisher_team == publisher_team)
        if tag:
            count_query = count_query.where(Contract.tags.contains([tag]))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Contract.created_at.desc())

        result = await self.db.execute(query)
        contracts = list(result.scalars().all())

        return contracts, total

    async def update(
        self, contract_id: UUID, update_data: ContractUpdate
    ) -> Contract | None:
        """Update a contract and create a version snapshot."""
        contract = await self.get(contract_id)
        if not contract:
            return None

        # Create version snapshot before updating
        await self._create_version_snapshot(
            contract,
            update_data.change_summary,
            update_data.changed_by,
        )

        # Update basic fields
        if update_data.version is not None:
            contract.version = update_data.version
        if update_data.description is not None:
            contract.description = update_data.description
        if update_data.status is not None:
            contract.status = update_data.status
        if update_data.tags is not None:
            contract.tags = update_data.tags
        if update_data.metadata is not None:
            contract.metadata_ = update_data.metadata

        # Update publisher info
        if update_data.publisher:
            contract.publisher_team = update_data.publisher.team
            contract.publisher_owner = update_data.publisher.owner
            contract.repository_url = update_data.publisher.repository_url
            contract.contact_email = update_data.publisher.contact_email

        # Update fields if provided (replace all)
        if update_data.schema_fields is not None:
            # Delete existing fields
            for field in contract.fields:
                await self.db.delete(field)

            # Create new fields
            for field_data in update_data.schema_fields:
                field = ContractField(
                    contract_id=contract.id,
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
                self.db.add(field)

        # Update quality metrics if provided (replace all)
        if update_data.quality is not None:
            for metric in contract.quality_metrics:
                await self.db.delete(metric)

            for metric_data in update_data.quality:
                metric = QualityMetric(
                    contract_id=contract.id,
                    metric_type=metric_data.metric_type,
                    threshold=metric_data.threshold,
                    measurement_method=metric_data.measurement_method,
                    alert_on_breach=metric_data.alert_on_breach,
                )
                self.db.add(metric)

        # Update access config if provided
        if update_data.access is not None:
            if contract.access_config:
                await self.db.delete(contract.access_config)

            access = AccessConfig(
                contract_id=contract.id,
                endpoint_url=update_data.access.endpoint_url,
                methods=update_data.access.methods,
                auth_type=update_data.access.auth_type,
                required_scopes=update_data.access.required_scopes,
                rate_limit=update_data.access.rate_limit,
            )
            self.db.add(access)

        contract.updated_at = datetime.utcnow()
        await self.db.flush()

        return await self.get(contract_id)

    async def deprecate(self, contract_id: UUID) -> bool:
        """Soft delete a contract by setting status to deprecated."""
        contract = await self.get(contract_id)
        if not contract:
            return False

        contract.status = "deprecated"
        contract.updated_at = datetime.utcnow()
        await self.db.flush()

        return True

    async def get_versions(self, contract_id: UUID) -> list[ContractVersion]:
        """Get version history for a contract."""
        result = await self.db.execute(
            select(ContractVersion)
            .where(ContractVersion.contract_id == contract_id)
            .order_by(ContractVersion.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_subscriber(
        self, contract_id: UUID, team: str, use_case: str | None, fields_used: list[str], contact_email: str | None
    ) -> Subscriber:
        """Add a subscriber to a contract."""
        subscriber = Subscriber(
            contract_id=contract_id,
            team=team,
            use_case=use_case,
            fields_used=fields_used,
            contact_email=contact_email,
        )
        self.db.add(subscriber)
        await self.db.flush()
        return subscriber

    async def remove_subscriber(self, contract_id: UUID, subscriber_id: UUID) -> bool:
        """Remove a subscriber from a contract."""
        result = await self.db.execute(
            select(Subscriber).where(
                Subscriber.id == subscriber_id,
                Subscriber.contract_id == contract_id,
            )
        )
        subscriber = result.scalar_one_or_none()
        if not subscriber:
            return False

        await self.db.delete(subscriber)
        await self.db.flush()
        return True

    async def get_subscribers(self, contract_id: UUID) -> list[Subscriber]:
        """Get all subscribers for a contract."""
        result = await self.db.execute(
            select(Subscriber).where(Subscriber.contract_id == contract_id)
        )
        return list(result.scalars().all())

    async def record_compliance_check(
        self,
        contract_id: UUID,
        check_type: str,
        status: str,
        details: dict[str, Any],
        error_message: str | None = None,
    ) -> ComplianceCheck:
        """Record a compliance check result."""
        check = ComplianceCheck(
            contract_id=contract_id,
            check_type=check_type,
            status=status,
            details=details,
            error_message=error_message,
        )
        self.db.add(check)
        await self.db.flush()
        return check

    async def _create_version_snapshot(
        self,
        contract: Contract,
        change_summary: str | None,
        changed_by: str | None,
    ) -> ContractVersion:
        """Create a version snapshot of the current contract state."""
        snapshot = {
            "name": contract.name,
            "version": contract.version,
            "description": contract.description,
            "status": contract.status,
            "publisher_team": contract.publisher_team,
            "publisher_owner": contract.publisher_owner,
            "repository_url": contract.repository_url,
            "contact_email": contract.contact_email,
            "tags": contract.tags,
            "metadata": contract.metadata_,
            "fields": [
                {
                    "name": f.name,
                    "data_type": f.data_type,
                    "description": f.description,
                    "nullable": f.nullable,
                    "is_pii": f.is_pii,
                    "is_primary_key": f.is_primary_key,
                    "is_foreign_key": f.is_foreign_key,
                    "foreign_key_reference": f.foreign_key_reference,
                    "constraints": f.constraints,
                }
                for f in contract.fields
            ],
            "quality_metrics": [
                {
                    "metric_type": m.metric_type,
                    "threshold": m.threshold,
                    "measurement_method": m.measurement_method,
                    "alert_on_breach": m.alert_on_breach,
                }
                for m in contract.quality_metrics
            ],
            "access_config": (
                {
                    "endpoint_url": contract.access_config.endpoint_url,
                    "methods": contract.access_config.methods,
                    "auth_type": contract.access_config.auth_type,
                    "required_scopes": contract.access_config.required_scopes,
                    "rate_limit": contract.access_config.rate_limit,
                }
                if contract.access_config
                else None
            ),
            "subscribers": [
                {
                    "team": s.team,
                    "use_case": s.use_case,
                    "fields_used": s.fields_used,
                    "contact_email": s.contact_email,
                }
                for s in contract.subscribers
            ],
        }

        version = ContractVersion(
            contract_id=contract.id,
            version=contract.version,
            contract_snapshot=snapshot,
            change_summary=change_summary,
            changed_by=changed_by,
        )
        self.db.add(version)
        await self.db.flush()

        return version
