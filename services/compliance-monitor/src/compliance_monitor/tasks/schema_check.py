"""Schema compliance check tasks."""

import logging
from typing import Any

import httpx

from compliance_monitor.celery_app import celery_app
from compliance_monitor.checks.schema_validator import SchemaValidator
from compliance_monitor.config import settings
from compliance_monitor.reporters import send_alert

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_schema(self, contract_id: str) -> dict[str, Any]:
    """
    Check a single contract's schema compliance.

    Fetches the contract definition, then fetches the actual schema from
    the data service's /schema endpoint, and validates them against each other.
    """
    try:
        with httpx.Client(timeout=settings.http_timeout) as client:
            # Fetch contract from Contract Service
            contract_resp = client.get(
                f"{settings.contract_service_url}/api/v1/contracts/{contract_id}"
            )
            contract_resp.raise_for_status()
            contract_data = contract_resp.json()

            # Get access endpoint from contract
            access_config = contract_data.get("access_config")
            if not access_config:
                logger.info(f"Contract {contract_id} has no access config, skipping")
                return {"status": "skipped", "reason": "No access config"}

            endpoint = access_config.get("endpoint_url")
            if not endpoint:
                logger.info(f"Contract {contract_id} has no endpoint URL, skipping")
                return {"status": "skipped", "reason": "No endpoint configured"}

            # Fetch actual schema from data service
            try:
                schema_resp = client.get(f"{endpoint}/schema", timeout=30)
                schema_resp.raise_for_status()
                actual_schema = schema_resp.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch schema from {endpoint}: {e}")
                _record_compliance_check(
                    contract_id=contract_id,
                    check_type="schema",
                    status="error",
                    details={"error": f"Failed to fetch schema: {str(e)}"},
                    error_message=str(e),
                )
                raise self.retry(exc=e)

        # Validate schema
        validator = SchemaValidator(contract_data)
        is_valid = validator.validate(actual_schema)
        result = validator.get_result()

        # Record result in Contract Service
        status = "pass" if is_valid else "fail"
        _record_compliance_check(
            contract_id=contract_id,
            check_type="schema",
            status=status,
            details=result,
        )

        # Send alert on failure
        if not is_valid:
            send_alert(
                alert_type="schema_drift",
                contract=contract_data,
                details=result,
            )
            logger.warning(
                f"Schema validation failed for {contract_data['name']}: {result['errors']}"
            )
        else:
            logger.info(f"Schema validation passed for {contract_data['name']}")

        return result

    except httpx.HTTPError as e:
        logger.error(f"HTTP error checking schema for {contract_id}: {e}")
        raise self.retry(exc=e)
    except Exception as e:
        logger.exception(f"Error checking schema for {contract_id}")
        _record_compliance_check(
            contract_id=contract_id,
            check_type="schema",
            status="error",
            details={"error": str(e)},
            error_message=str(e),
        )
        raise


@celery_app.task
def check_all_schemas() -> dict[str, Any]:
    """
    Scheduled task to check all active contracts.

    Fetches all active contracts from the Contract Service and queues
    individual schema checks for each one.
    """
    logger.info("Starting scheduled schema check for all contracts")

    try:
        with httpx.Client(timeout=settings.http_timeout) as client:
            resp = client.get(
                f"{settings.contract_service_url}/api/v1/contracts",
                params={"status": "active", "limit": 100},
            )
            resp.raise_for_status()
            contracts = resp.json().get("contracts", [])
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch contracts: {e}")
        return {"status": "error", "error": str(e)}

    queued = 0
    for contract in contracts:
        # Only check contracts that have an access endpoint configured
        if contract.get("access_config"):
            check_schema.delay(contract["id"])
            queued += 1

    logger.info(f"Queued {queued} schema checks out of {len(contracts)} contracts")
    return {"status": "ok", "queued": queued, "total": len(contracts)}


def _record_compliance_check(
    contract_id: str,
    check_type: str,
    status: str,
    details: dict[str, Any],
    error_message: str | None = None,
) -> None:
    """Record compliance check result in Contract Service."""
    try:
        with httpx.Client(timeout=settings.http_timeout) as client:
            client.post(
                f"{settings.contract_service_url}/api/v1/contracts/{contract_id}/compliance",
                json={
                    "check_type": check_type,
                    "status": status,
                    "details": details,
                    "error_message": error_message,
                },
            )
    except httpx.HTTPError as e:
        logger.error(f"Failed to record compliance check: {e}")
