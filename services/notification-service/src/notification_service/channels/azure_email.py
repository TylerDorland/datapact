"""Azure Communication Services email channel."""

import logging

from azure.communication.email import EmailClient

from notification_service.channels.base import BaseChannel
from notification_service.config import settings
from notification_service.models.notification import Notification

logger = logging.getLogger(__name__)


class AzureEmailChannel(BaseChannel):
    """Email channel using Azure Communication Services."""

    def __init__(self) -> None:
        self.client = EmailClient.from_connection_string(settings.acs_connection_string or "")
        self.from_email = settings.acs_sender_address

    async def send(self, notification: Notification) -> tuple[bool, str | None]:
        """Send email via Azure Communication Services."""
        try:
            message = {
                "senderAddress": self.from_email,
                "recipients": {"to": [{"address": notification.recipient_email}]},
                "content": {
                    "subject": notification.subject,
                    "plainText": notification.body_text or "",
                    "html": notification.body_html or "",
                },
            }
            poller = self.client.begin_send(message)
            result = poller.result()

            if result["status"] == "Succeeded":
                logger.info(f"Sent email to {notification.recipient_email}")
                return True, None
            return False, f"ACS status: {result['status']}"
        except Exception as e:
            error_msg = f"ACS error: {str(e)}"
            logger.error(f"Failed to send email: {error_msg}")
            return False, error_msg

    async def send_batch(
        self, notifications: list[Notification]
    ) -> list[tuple[Notification, bool, str | None]]:
        """Send batch of emails."""
        results = []
        for notification in notifications:
            success, error = await self.send(notification)
            results.append((notification, success, error))
        return results

    async def close(self) -> None:
        """Close connections."""
        pass
