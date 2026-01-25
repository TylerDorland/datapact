"""Slack webhook reporter for compliance alerts."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class SlackReporter:
    """Sends compliance alerts to Slack via webhook."""

    # Alert type to color mapping
    COLORS = {
        "schema_drift": "#FF6B6B",  # Red
        "quality_breach": "#FFE66D",  # Yellow
        "availability_failure": "#FF6B6B",  # Red
    }

    # Alert type to emoji mapping
    EMOJIS = {
        "schema_drift": ":warning:",
        "quality_breach": ":chart_with_downwards_trend:",
        "availability_failure": ":rotating_light:",
    }

    def __init__(self, webhook_url: str):
        """
        Initialize Slack reporter.

        Args:
            webhook_url: Slack incoming webhook URL
        """
        self.webhook_url = webhook_url

    def send(
        self,
        alert_type: str,
        contract: dict[str, Any],
        details: dict[str, Any],
    ) -> None:
        """
        Send alert to Slack.

        Args:
            alert_type: Type of alert
            contract: Contract data
            details: Alert details
        """
        contract_name = contract.get("name", "unknown")
        publisher_team = contract.get("publisher_team", "unknown")

        color = self.COLORS.get(alert_type, "#808080")
        emoji = self.EMOJIS.get(alert_type, ":bell:")

        # Build message
        title = self._get_title(alert_type, contract_name)
        fields = self._build_fields(alert_type, contract, details)

        payload = {
            "attachments": [
                {
                    "color": color,
                    "fallback": title,
                    "title": f"{emoji} {title}",
                    "fields": fields,
                    "footer": f"DataPact Compliance Monitor | Team: {publisher_team}",
                    "ts": None,  # Will be set by Slack
                }
            ]
        }

        try:
            with httpx.Client() as client:
                response = client.post(self.webhook_url, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"Sent Slack alert for {contract_name}")
        except httpx.HTTPError as e:
            logger.error(f"Failed to send Slack alert: {e}")
            raise

    def _get_title(self, alert_type: str, contract_name: str) -> str:
        """Get alert title based on type."""
        titles = {
            "schema_drift": f"Schema Drift Detected: {contract_name}",
            "quality_breach": f"Quality SLA Breach: {contract_name}",
            "availability_failure": f"Service Unavailable: {contract_name}",
        }
        return titles.get(alert_type, f"Compliance Alert: {contract_name}")

    def _build_fields(
        self,
        alert_type: str,
        contract: dict[str, Any],
        details: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Build Slack message fields based on alert type."""
        fields = [
            {
                "title": "Contract",
                "value": contract.get("name"),
                "short": True,
            },
            {
                "title": "Version",
                "value": contract.get("version"),
                "short": True,
            },
        ]

        if alert_type == "schema_drift":
            errors = details.get("errors", [])
            if errors:
                fields.append({
                    "title": "Schema Errors",
                    "value": "\n".join(f"• {e}" for e in errors[:5]),
                    "short": False,
                })
            warnings = details.get("warnings", [])
            if warnings:
                fields.append({
                    "title": "Warnings",
                    "value": "\n".join(f"• {w}" for w in warnings[:3]),
                    "short": False,
                })

        elif alert_type == "quality_breach":
            checks = details.get("checks", [])
            failed_checks = [c for c in checks if c.get("status") == "fail"]
            if failed_checks:
                check_lines = []
                for check in failed_checks[:5]:
                    check_lines.append(
                        f"• {check['metric_type']}: {check.get('message', 'Failed')}"
                    )
                fields.append({
                    "title": "Failed Checks",
                    "value": "\n".join(check_lines),
                    "short": False,
                })

        elif alert_type == "availability_failure":
            fields.append({
                "title": "Endpoint",
                "value": details.get("endpoint", "N/A"),
                "short": True,
            })
            error = details.get("health_response", {}).get("error")
            if error:
                fields.append({
                    "title": "Error",
                    "value": error,
                    "short": False,
                })

        return fields
