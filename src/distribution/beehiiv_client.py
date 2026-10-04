from __future__ import annotations
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import BeehiivConfig
from src.models.schemas import PublishedPost

logger = logging.getLogger(__name__)

class BeehiivClient:
    """Client for interacting with the Beehiiv API."""

    def __init__(self, config: BeehiivConfig):
        self.config = config
        self.client = httpx.Client(
            base_url="https://api.beehiiv.com/v2",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def create_post(self, title: str, subtitle: str, html_content: str, scheduled_at: str | None = None, status: str = 'confirmed') -> PublishedPost:
        """Create a new post in Beehiiv."""
        logger.info(f"Creating Beehiiv post: {title}")
        url = f"/publications/{self.config.publication_id}/posts"
        payload = {
            "title": title,
            "subtitle": subtitle,
            "body_content": html_content,
            "status": status,
            "audience_type": "free"
        }
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at

        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json().get("data", {})
            return PublishedPost(
                post_id=data.get("id", ""),
                title=title,
                web_url=data.get("web_url", ""),
                status=data.get("status", status)
            )
        except httpx.HTTPError as e:
            logger.error(f"Failed to create Beehiiv post: {e}")
            raise

    def get_post(self, post_id: str) -> dict:
        """Verify a post exists and retrieve its details."""
        url = f"/publications/{self.config.publication_id}/posts/{post_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json().get("data", {})

    def get_subscriber_count(self) -> int:
        """Get the total subscriber count for the publication."""
        url = f"/publications/{self.config.publication_id}/subscriptions"
        response = self.client.get(url)
        response.raise_for_status()
        # simplified based on typical pagination data structure, might need adjustment
        return response.json().get("total_results", 0)
