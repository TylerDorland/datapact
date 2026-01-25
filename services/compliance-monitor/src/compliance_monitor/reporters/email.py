"""Email reporter for compliance alerts."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any

logger = logging.getLogger(__name__)


class EmailReporter:
    """Sends compliance alerts via email."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        from_addr: str,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        use_tls: bool = False,
    ):
        """
        Initialize email reporter.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            from_addr: From email address
            smtp_user: SMTP username (optional)
            smtp_password: SMTP password (optional)
            use_tls: Whether to use TLS
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.use_tls = use_tls

    def send(
        self,
        alert_type: str,
        contract: dict[str, Any],
        details: dict[str, Any],
        to_addr: str,
    ) -> None:
        """
        Send alert email.

        Args:
            alert_type: Type of alert
            contract: Contract data
            details: Alert details
            to_addr: Recipient email address
        """
        contract_name = contract.get("name", "unknown")

        subject = self._get_subject(alert_type, contract_name)
        html_body = self._build_html_body(alert_type, contract, details)
        text_body = self._build_text_body(alert_type, contract, details)

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = to_addr

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_addr, [to_addr], msg.as_string())
                logger.info(f"Sent email alert to {to_addr} for {contract_name}")
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email alert: {e}")
            raise

    def _get_subject(self, alert_type: str, contract_name: str) -> str:
        """Get email subject based on alert type."""
        subjects = {
            "schema_drift": f"[DataPact Alert] Schema Drift Detected: {contract_name}",
            "quality_breach": f"[DataPact Alert] Quality SLA Breach: {contract_name}",
            "availability_failure": f"[DataPact Alert] Service Unavailable: {contract_name}",
        }
        return subjects.get(alert_type, f"[DataPact Alert] {contract_name}")

    def _build_html_body(
        self,
        alert_type: str,
        contract: dict[str, Any],
        details: dict[str, Any],
    ) -> str:
        """Build HTML email body."""
        contract_name = contract.get("name", "unknown")
        version = contract.get("version", "unknown")
        publisher_team = contract.get("publisher_team", "unknown")

        title = self._get_title(alert_type)

        details_html = self._build_details_html(alert_type, details)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8d7da; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; color: #721c24; font-size: 18px; }}
                .info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .info p {{ margin: 5px 0; }}
                .details {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; }}
                .details h3 {{ margin-top: 0; color: #856404; }}
                ul {{ margin: 10px 0; padding-left: 20px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>

                <div class="info">
                    <p><strong>Contract:</strong> {contract_name}</p>
                    <p><strong>Version:</strong> {version}</p>
                    <p><strong>Publisher Team:</strong> {publisher_team}</p>
                </div>

                <div class="details">
                    <h3>Details</h3>
                    {details_html}
                </div>

                <div class="footer">
                    <p>This is an automated alert from DataPact Compliance Monitor.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _build_text_body(
        self,
        alert_type: str,
        contract: dict[str, Any],
        details: dict[str, Any],
    ) -> str:
        """Build plain text email body."""
        contract_name = contract.get("name", "unknown")
        version = contract.get("version", "unknown")
        publisher_team = contract.get("publisher_team", "unknown")

        title = self._get_title(alert_type)
        details_text = self._build_details_text(alert_type, details)

        return f"""
{title}

Contract: {contract_name}
Version: {version}
Publisher Team: {publisher_team}

Details:
{details_text}

---
This is an automated alert from DataPact Compliance Monitor.
"""

    def _get_title(self, alert_type: str) -> str:
        """Get alert title based on type."""
        titles = {
            "schema_drift": "Schema Drift Detected",
            "quality_breach": "Quality SLA Breach",
            "availability_failure": "Service Unavailable",
        }
        return titles.get(alert_type, "Compliance Alert")

    def _build_details_html(self, alert_type: str, details: dict[str, Any]) -> str:
        """Build HTML details section based on alert type."""
        if alert_type == "schema_drift":
            errors = details.get("errors", [])
            warnings = details.get("warnings", [])
            html = ""
            if errors:
                html += "<h4>Errors:</h4><ul>"
                for error in errors:
                    html += f"<li>{error}</li>"
                html += "</ul>"
            if warnings:
                html += "<h4>Warnings:</h4><ul>"
                for warning in warnings:
                    html += f"<li>{warning}</li>"
                html += "</ul>"
            return html or "<p>No specific details available.</p>"

        elif alert_type == "quality_breach":
            checks = details.get("checks", [])
            failed = [c for c in checks if c.get("status") == "fail"]
            if failed:
                html = "<ul>"
                for check in failed:
                    html += f"<li><strong>{check['metric_type']}:</strong> {check.get('message', 'Failed')}</li>"
                html += "</ul>"
                return html
            return "<p>No specific details available.</p>"

        elif alert_type == "availability_failure":
            endpoint = details.get("endpoint", "N/A")
            error = details.get("health_response", {}).get("error", "Unknown error")
            return f"<p><strong>Endpoint:</strong> {endpoint}</p><p><strong>Error:</strong> {error}</p>"

        return "<p>No specific details available.</p>"

    def _build_details_text(self, alert_type: str, details: dict[str, Any]) -> str:
        """Build plain text details section."""
        if alert_type == "schema_drift":
            lines = []
            for error in details.get("errors", []):
                lines.append(f"  - {error}")
            for warning in details.get("warnings", []):
                lines.append(f"  - (Warning) {warning}")
            return "\n".join(lines) or "No specific details available."

        elif alert_type == "quality_breach":
            checks = details.get("checks", [])
            failed = [c for c in checks if c.get("status") == "fail"]
            lines = []
            for check in failed:
                lines.append(f"  - {check['metric_type']}: {check.get('message', 'Failed')}")
            return "\n".join(lines) or "No specific details available."

        elif alert_type == "availability_failure":
            endpoint = details.get("endpoint", "N/A")
            error = details.get("health_response", {}).get("error", "Unknown error")
            return f"  Endpoint: {endpoint}\n  Error: {error}"

        return "No specific details available."
