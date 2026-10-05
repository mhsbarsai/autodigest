from __future__ import annotations

import logging
from typing import Optional
import resend
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import ResendConfig
from src.models.schemas import PublishedPost

logger = logging.getLogger(__name__)


class ResendClient:
    """Client for distributing newsletter editions via Resend API."""

    def __init__(self, config: ResendConfig) -> None:
        self.config = config
        resend.api_key = config.api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def publish_newsletter(
        self,
        subject: str,
        html_content: str,
        scheduled_at: Optional[str] = None,
    ) -> PublishedPost:
        """Send newsletter via Resend Broadcasts (if audience_id is set) or direct Emails."""
        logger.info(f"Publishing newsletter with Resend: {subject}")

        # If audience_id is provided, send a Broadcast to all subscribers
        if self.config.audience_id:
            logger.info(f"Dispatching broadcast to Resend Audience ID: {self.config.audience_id}")
            params: dict = {
                "from": self.config.from_email,
                "audience_id": self.config.audience_id,
                "subject": subject,
                "html": html_content,
                "send": True,
            }
            if scheduled_at:
                params["scheduled_at"] = scheduled_at

            response = resend.Broadcasts.create(params)
            broadcast_id = (
                response.get("id", "")
                if isinstance(response, dict)
                else getattr(response, "id", "")
            )
            return PublishedPost(
                post_id=broadcast_id,
                title=subject,
                status="scheduled" if scheduled_at else "sent",
                web_url=f"https://resend.com/broadcasts/{broadcast_id}",
            )

        # Collect recipients from subscriber manager and config
        from src.distribution.subscriber_manager import SubscriberManager
        import uuid

        sub_manager = SubscriberManager()
        active_subscribers = sub_manager.get_active_subscribers()
        config_recipients = [e.strip() for e in self.config.to_email.split(",") if e.strip()]

        # Combine unique recipients
        all_recipients = list(dict.fromkeys(active_subscribers + config_recipients))
        if not all_recipients:
            logger.warning("No subscribers found in data/subscribers.json or RESEND_TO_EMAIL. Defaulting to owner mahsabar98@gmail.com.")
            all_recipients = ["mahsabar98@gmail.com"]

        logger.info(f"Dispatching newsletter to {len(all_recipients)} subscriber(s)...")

        if len(all_recipients) == 1:
            params = {
                "from": self.config.from_email,
                "to": all_recipients,
                "subject": subject,
                "html": html_content,
            }
            if scheduled_at:
                params["scheduled_at"] = scheduled_at

            response = resend.Emails.send(params)
            email_id = (
                response.get("id", "")
                if isinstance(response, dict)
                else getattr(response, "id", "")
            )
            return PublishedPost(
                post_id=email_id,
                title=subject,
                status="scheduled" if scheduled_at else "sent",
                web_url=f"https://resend.com/emails/{email_id}",
            )
        else:
            # Batch send for multi-subscriber delivery (preserves recipient privacy)
            batch_params = [
                {
                    "from": self.config.from_email,
                    "to": [r],
                    "subject": subject,
                    "html": html_content,
                }
                for r in all_recipients[:100]
            ]
            resend.Batch.send(batch_params)
            batch_id = str(uuid.uuid4())[:8]
            logger.info(f"Batch dispatch completed for {len(batch_params)} subscriber(s).")
            return PublishedPost(
                post_id=f"batch_{batch_id}",
                title=subject,
                status="sent",
                web_url="https://resend.com/emails",
            )
