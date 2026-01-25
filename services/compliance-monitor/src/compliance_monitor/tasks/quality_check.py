"""Quality metrics compliance check tasks."""

import logging
from typing import Any

import httpx

from compliance_monitor.celery_app import celery_app
from compliance_monitor.checks.freshness_checker import FreshnessChecker
from compliance_monitor.checks.completeness_checker import CompletenessChecker
from compliance_monitor.config import settings
from compliance_monitor.reporters import send_alert

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_quality(self, contract_id: str) -> dict[str, Any]:
    """
    Check a single contract's quality metrics compliance.

    Fetches metrics from the data service's /metrics endpoint and validates
    against the quality SLAs defined in the contract.
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

            # Fetch metrics from data service
            try:
                metrics_resp = client.get(f"{endpoint}/metrics", timeout=30)
                metrics_resp.raise_for_status()
                metrics_data = metrics_resp.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch metrics from {endpoint}: {e}")
                _record_compliance_check(
                    contract_id=contract_id,
                    check_type="quality",
                    status="error",
                    details={"error": f"Failed to fetch metrics: {str(e)}"},
                )
                raise self.retry(exc=e)

        # Get quality metrics from contract
        quality_metrics = contract_data.get("quality_metrics", [])

        results = {
            "checks": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        }

        for metric in quality_metrics:
            metric_type = metric.get("metric_type")
            threshold = metric.get("threshold")

            check_result = _check_metric(
                metric_type=metric_type,
                threshold=threshold,
                metrics_data=metrics_data,
            )

            results["checks"].append({
                "metric_type": metric_type,
                "threshold": threshold,
                **check_result,
            })

            if check_result["status"] == "pass":
                results["passed"] += 1
            elif check_result["status"] == "fail":
                results["failed"] += 1
            else:
                results["warnings"] += 1

        # Determine overall status
        overall_status = "pass" if results["failed"] == 0 else "fail"

        # Record result
        _record_compliance_check(
            contract_id=contract_id,
            check_type="quality",
            status=overall_status,
            details=results,
        )

        # Send alert on failure
        if results["failed"] > 0:
            send_alert(
                alert_type="quality_breach",
                contract=contract_data,
                details=results,
            )
            logger.warning(
                f"Quality check failed for {contract_data['name']}: "
                f"{results['failed']} metrics breached"
            )
        else:
            logger.info(f"Quality check passed for {contract_data['name']}")

        return results

    except httpx.HTTPError as e:
        logger.error(f"HTTP error checking quality for {contract_id}: {e}")
        raise self.retry(exc=e)
    except Exception as e:
        logger.exception(f"Error checking quality for {contract_id}")
        raise


@celery_app.task
def check_all_quality() -> dict[str, Any]:
    """
    Scheduled task to check quality for all active contracts.
    """
    logger.info("Starting scheduled quality check for all contracts")

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
        # Only check contracts that have quality metrics defined
        if contract.get("quality_metrics") and contract.get("access_config"):
            check_quality.delay(contract["id"])
            queued += 1

    logger.info(f"Queued {queued} quality checks out of {len(contracts)} contracts")
    return {"status": "ok", "queued": queued, "total": len(contracts)}


def _check_metric(
    metric_type: str,
    threshold: str,
    metrics_data: dict[str, Any],
) -> dict[str, Any]:
    """Check a single metric against its threshold."""

    if metric_type == "freshness":
        checker = FreshnessChecker(threshold)
        freshness_data = metrics_data.get("freshness", {})
        return checker.check(freshness_data)

    elif metric_type == "completeness":
        checker = CompletenessChecker(threshold)
        completeness_data = metrics_data.get("completeness", {})
        return checker.check(completeness_data)

    else:
        return {
            "status": "warning",
            "message": f"Unknown metric type: {metric_type}",
            "actual_value": None,
        }


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
