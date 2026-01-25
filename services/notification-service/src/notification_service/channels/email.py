"""Email notification channel."""

import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from notification_service.config import settings
from notification_service.channels.base import BaseChannel
from notification_service.models.notification import Notification

logger = logging.getLogger(__name__)


class EmailChannel(BaseChannel):
    """Email notification channel using SMTP."""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.use_tls = settings.smtp_use_tls
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name

    async def send(self, notification: Notification) -> tuple[bool, str | None]:
        """Send a single email notification."""
        try:
            msg = self._create_message(notification)

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=self.use_tls,
            )

            logger.info(f"Sent email to {notification.recipient_email}")
            return True, None

        except aiosmtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(f"Failed to send email to {notification.recipient_email}: {error_msg}")
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Failed to send email to {notification.recipient_email}: {error_msg}")
            return False, error_msg

    async def send_batch(
        self, notifications: list[Notification]
    ) -> list[tuple[Notification, bool, str | None]]:
        """Send a batch of email notifications."""
        results = []

        for notification in notifications:
            success, error = await self.send(notification)
            results.append((notification, success, error))

        return results

    def _create_message(self, notification: Notification) -> MIMEMultipart:
        """Create email message from notification."""
        msg = MIMEMultipart("alternative")

        msg["Subject"] = notification.subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = notification.recipient_email

        # Add text part
        if notification.body_text:
            text_part = MIMEText(notification.body_text, "plain")
            msg.attach(text_part)

        # Add HTML part
        if notification.body_html:
            html_part = MIMEText(notification.body_html, "html")
            msg.attach(html_part)

        return msg

    async def close(self) -> None:
        """Close any open connections."""
        # aiosmtplib creates connections per-send, so nothing to close
        pass
