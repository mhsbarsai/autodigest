"""AutoDigest — Configuration management.

Loads settings from environment variables (or .env file for local dev).
In production (Cloud Functions), secrets come from Secret Manager.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env for local development — no-op if file doesn't exist
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class GeminiConfig:
    """Google Gemini AI settings."""

    api_key: str = field(repr=False, default_factory=lambda: os.environ["GEMINI_API_KEY"])
    model: str = field(default_factory=lambda: os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"))
    temperature: float = 0.3
    max_output_tokens: int = 8192


@dataclass(frozen=True)
class ResendConfig:
    """Resend email & newsletter platform settings."""

    api_key: str = field(repr=False, default_factory=lambda: os.environ.get("RESEND_API_KEY", ""))
    from_email: str = field(
        default_factory=lambda: os.environ.get("RESEND_FROM_EMAIL", "Creavora <newsletter@creavora.my.id>")
    )
    to_email: str = field(default_factory=lambda: os.environ.get("RESEND_TO_EMAIL", ""))
    audience_id: str = field(default_factory=lambda: os.environ.get("RESEND_AUDIENCE_ID", ""))
    base_url: str = "https://api.resend.com"


@dataclass(frozen=True)
class BeehiivConfig:
    """Beehiiv newsletter platform settings."""

    api_key: str = field(repr=False, default_factory=lambda: os.environ.get("BEEHIIV_API_KEY", ""))
    publication_id: str = field(default_factory=lambda: os.environ.get("BEEHIIV_PUBLICATION_ID", ""))
    base_url: str = "https://api.beehiiv.com/v2"


@dataclass(frozen=True)
class StorageConfig:
    """Google Cloud Storage cache settings."""

    bucket_name: str = field(
        default_factory=lambda: os.environ.get("GCS_BUCKET_NAME", "autodigest-cache")
    )
    cache_file: str = "seen_articles.json"


@dataclass(frozen=True)
class NewsletterConfig:
    """Newsletter identity & schedule settings."""

    name: str = field(default_factory=lambda: os.environ.get("NEWSLETTER_NAME", "Creavora"))
    tagline: str = (
        "High-signal AI intelligence in under 3 minutes — frontier breakthroughs, agents, and actionable tools."
    )
    max_articles: int = 5
    min_articles: int = 3
    send_hour_utc: int = field(
        default_factory=lambda: int(os.environ.get("SEND_HOUR_UTC", "12"))
    )
    send_minute_utc: int = field(
        default_factory=lambda: int(os.environ.get("SEND_MINUTE_UTC", "0"))
    )


@dataclass(frozen=True)
class AppConfig:
    """Root application configuration — aggregates all sub-configs."""

    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    resend: ResendConfig = field(default_factory=ResendConfig)
    beehiiv: BeehiivConfig = field(default_factory=BeehiivConfig)
    distribution_provider: str = field(
        default_factory=lambda: os.environ.get("DISTRIBUTION_PROVIDER", "resend").lower()
    )
    storage: StorageConfig = field(default_factory=StorageConfig)
    newsletter: NewsletterConfig = field(default_factory=NewsletterConfig)
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))
    dry_run: bool = False


def load_config(*, dry_run: bool = False) -> AppConfig:
    """Build and return application config from environment.

    Args:
        dry_run: If True, skip remote distribution publishing (useful for local testing).

    Returns:
        Fully initialized AppConfig instance.

    Raises:
        KeyError: If a required environment variable is missing for the active provider.
    """
    config = AppConfig(dry_run=dry_run)
    if not dry_run:
        if config.distribution_provider == "resend":
            if not config.resend.api_key:
                raise KeyError(
                    "RESEND_API_KEY is required when DISTRIBUTION_PROVIDER=resend and dry_run=False"
                )
        elif config.distribution_provider == "beehiiv":
            if not config.beehiiv.api_key:
                raise KeyError("BEEHIIV_API_KEY is required when DISTRIBUTION_PROVIDER=beehiiv and dry_run=False")
            if not config.beehiiv.publication_id:
                raise KeyError("BEEHIIV_PUBLICATION_ID is required when DISTRIBUTION_PROVIDER=beehiiv and dry_run=False")
    return config
