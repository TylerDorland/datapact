"""Availability compliance check tasks."""

import logging
from typing import Any

import httpx

from compliance_monitor.celery_app import celery_app
from compliance_monitor.config import settings
from compliance_monitor.reporters import send_alert

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def check_availability(self, contract_id: str) -> dict[str, Any]:
    """
    Check a single contract's service availability.

    Pings the data service's /health endpoint to verify it's accessible.
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
                return {"status": "skipped", "reason": "No access config"}

            endpoint = access_config.get("endpoint_url")
            if not endpoint:
                return {"status": "skipped", "reason": "No endpoint configured"}

            # Check health endpoint
            try:
                health_resp = client.get(f"{endpoint}/health", timeout=10)
                health_resp.raise_for_status()
                health_data = health_resp.json()

                is_healthy = health_data.get("status") == "healthy"
                response_time_ms = health_resp.elapsed.total_seconds() * 1000

            except httpx.TimeoutException:
                is_healthy = False
                health_data = {"error": "Request timed out"}
                response_time_ms = None
            except httpx.HTTPError as e:
                is_healthy = False
                health_data = {"error": str(e)}
                response_time_ms = None

        result = {
            "is_available": is_healthy,
            "response_time_ms": response_time_ms,
            "health_response": health_data,
            "endpoint": endpoint,
        }

        status = "pass" if is_healthy else "fail"

        # Record result
        _record_compliance_check(
            contract_id=contract_id,
            check_type="availability",
            status=status,
            details=result,
        )

        # Send alert on failure
        if not is_healthy:
            send_alert(
                alert_type="availability_failure",
                contract=contract_data,
                details=result,
            )
            logger.warning(
                f"Availability check failed for {contract_data['name']}: "
                f"endpoint {endpoint} is not healthy"
            )
        else:
            logger.debug(
                f"Availability check passed for {contract_data['name']} "
                f"(response time: {response_time_ms:.0f}ms)"
            )

        return result

    except httpx.HTTPError as e:
        logger.error(f"HTTP error checking availability for {contract_id}: {e}")
        raise self.retry(exc=e)
    except Exception as e:
        logger.exception(f"Error checking availability for {contract_id}")
        raise


@celery_app.task
def check_all_availability() -> dict[str, Any]:
    """
    Scheduled task to check availability for all active contracts.

    Runs every minute to quickly detect service outages.
    """
    logger.debug("Starting scheduled availability check for all contracts")

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
            check_availability.delay(contract["id"])
            queued += 1

    logger.debug(f"Queued {queued} availability checks out of {len(contracts)} contracts")
    return {"status": "ok", "queued": queued, "total": len(contracts)}


def _record_compliance_check(
    contract_id: str,
    check_type: str,
    status: str,
    details: dict[str, Any],
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
                },
            )
    except httpx.HTTPError as e:
        logger.error(f"Failed to record compliance check: {e}")
