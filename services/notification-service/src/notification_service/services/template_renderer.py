"""Template renderer service."""

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from notification_service.config import settings
from notification_service.schemas.events import (
    BaseEvent,
    EventType,
    SchemaDriftEvent,
    QualityBreachEvent,
    PRBlockedEvent,
    ContractUpdatedEvent,
    DeprecationWarningEvent,
)


class TemplateRenderer:
    """Renders notification templates."""

    def __init__(self):
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Subject templates
        self.subjects = {
            EventType.SCHEMA_DRIFT: "[DataPact] Schema Drift Detected: {contract_name}",
            EventType.QUALITY_BREACH: "[DataPact] Quality SLA Breach: {contract_name}",
            EventType.PR_BLOCKED: "[DataPact] PR Blocked: {contract_name}",
            EventType.CONTRACT_UPDATED: "[DataPact] Contract Updated: {contract_name}",
            EventType.DEPRECATION_WARNING: "[DataPact] Deprecation Warning: {contract_name}",
            EventType.AVAILABILITY_FAILURE: "[DataPact] Service Unavailable: {contract_name}",
        }

    def render(self, event: BaseEvent) -> tuple[str, str, str]:
        """
        Render notification content from event.

        Returns:
            Tuple of (subject, html_body, text_body)
        """
        subject = self._render_subject(event)
        html_body = self._render_html(event)
        text_body = self._render_text(event)

        return subject, html_body, text_body

    def _render_subject(self, event: BaseEvent) -> str:
        """Render email subject."""
        template = self.subjects.get(
            event.event_type,
            "[DataPact] Alert: {contract_name}"
        )
        return template.format(
            contract_name=event.contract_name,
            contract_version=event.contract_version or "",
        )

    def _render_html(self, event: BaseEvent) -> str:
        """Render HTML email body."""
        template_name = self._get_template_name(event.event_type, "html")

        try:
            template = self.env.get_template(template_name)
            return template.render(
                event=event,
                frontend_url=settings.frontend_url,
            )
        except Exception:
            # Fallback to base template
            return self._render_fallback_html(event)

    def _render_text(self, event: BaseEvent) -> str:
        """Render plain text email body."""
        template_name = self._get_template_name(event.event_type, "txt")

        try:
            template = self.env.get_template(template_name)
            return template.render(
                event=event,
                frontend_url=settings.frontend_url,
            )
        except Exception:
            # Fallback to base template
            return self._render_fallback_text(event)

    def _get_template_name(self, event_type: EventType, extension: str) -> str:
        """Get template filename for event type."""
        return f"{event_type.value}.{extension}"

    def _render_fallback_html(self, event: BaseEvent) -> str:
        """Render fallback HTML template."""
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
        .footer {{ margin-top: 20px; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{event.event_type.value.replace('_', ' ').title()}</h1>
        </div>

        <div class="info">
            <p><strong>Contract:</strong> {event.contract_name}</p>
            <p><strong>Version:</strong> {event.contract_version or 'N/A'}</p>
            <p><strong>Publisher Team:</strong> {event.publisher_team or 'N/A'}</p>
            <p><strong>Time:</strong> {event.timestamp.isoformat()}</p>
        </div>

        <div class="footer">
            <p>This is an automated alert from DataPact.</p>
            <p><a href="{settings.frontend_url}">View in Dashboard</a></p>
        </div>
    </div>
</body>
</html>
"""

    def _render_fallback_text(self, event: BaseEvent) -> str:
        """Render fallback text template."""
        return f"""
{event.event_type.value.replace('_', ' ').title()}

Contract: {event.contract_name}
Version: {event.contract_version or 'N/A'}
Publisher Team: {event.publisher_team or 'N/A'}
Time: {event.timestamp.isoformat()}

---
This is an automated alert from DataPact.
View in Dashboard: {settings.frontend_url}
"""

    def render_digest(self, notifications_by_type: dict) -> str:
        """Render digest email with multiple notifications grouped by type."""
        try:
            template = self.env.get_template("digest.html")
            return template.render(
                notifications_by_type=notifications_by_type,
                frontend_url=settings.frontend_url,
            )
        except Exception:
            return self._render_fallback_digest(notifications_by_type)

    def _render_fallback_digest(self, notifications_by_type: dict) -> str:
        """Render fallback digest template."""
        total = sum(len(n) for n in notifications_by_type.values())
        sections = []

        for event_type, notifications in notifications_by_type.items():
            section = f"<h3>{event_type.replace('_', ' ').title()} ({len(notifications)})</h3>"
            section += "<ul>"
            for n in notifications:
                section += f"<li><strong>{n.subject}</strong> - {n.created_at.strftime('%Y-%m-%d %H:%M')}</li>"
            section += "</ul>"
            sections.append(section)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #3b82f6; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: white; font-size: 18px; }}
        h3 {{ margin-top: 20px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DataPact Digest: {total} Notifications</h1>
        </div>
        {''.join(sections)}
        <div class="footer">
            <p><a href="{settings.frontend_url}">View all in Dashboard</a></p>
        </div>
    </div>
</body>
</html>
"""
