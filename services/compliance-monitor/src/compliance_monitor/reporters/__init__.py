"""Alert reporters for compliance failures."""

import logging
from typing import Any

from compliance_monitor.config import settings
from compliance_monitor.reporters.slack import SlackReporter
from compliance_monitor.reporters.email import EmailReporter

logger = logging.getLogger(__name__)


def send_alert(
    alert_type: str,
    contract: dict[str, Any],
    details: dict[str, Any],
) -> None:
    """
    Send an alert through all configured channels.

    Args:
        alert_type: Type of alert (schema_drift, quality_breach, availability_failure)
        contract: Contract data
        details: Alert details (errors, metrics, etc.)
    """
    contract_name = contract.get("name", "unknown")
    logger.info(f"Sending {alert_type} alert for contract {contract_name}")

    # Send to Slack if configured
    if settings.slack_webhook_url:
        try:
            slack = SlackReporter(settings.slack_webhook_url)
            slack.send(alert_type, contract, details)
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    # Send email to contract owner
    contact_email = contract.get("contact_email")
    if contact_email:
        try:
            email = EmailReporter(
                smtp_host=settings.smtp_host,
                smtp_port=settings.smtp_port,
                from_addr=settings.alert_email_from,
            )
            email.send(alert_type, contract, details, to_addr=contact_email)
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")


__all__ = ["send_alert", "SlackReporter", "EmailReporter"]
