"""AutoDigest — Pydantic data models.

All structured data flowing through the pipeline is defined here so every
module shares the same schema.  Gemini structured-output calls also use
these models to guarantee valid JSON responses.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, computed_field


# ---------------------------------------------------------------------------
# Ingestion layer models
# ---------------------------------------------------------------------------

class RawArticle(BaseModel):
    """A single article fetched from an RSS feed before AI processing."""

    title: str
    url: str
    source_name: str
    published_at: Optional[datetime] = None
    raw_text: str = ""
    word_count: int = 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def content_hash(self) -> str:
        """Stable hash for deduplication based on URL + title."""
        norm_url = self.url.strip().rstrip("/").lower()
        norm_title = self.title.strip().lower()
        key = f"{norm_url}|{norm_title}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# AI layer models — used as Gemini structured-output schemas
# ---------------------------------------------------------------------------

class ScoredArticle(BaseModel):
    """Article with AI-assigned relevance scores."""

    title: str
    url: str
    source_name: str
    raw_text: str = ""
    relevance_score: int = Field(
        description="How relevant is this to AI professionals? 1-10",
        ge=1,
        le=10,
    )
    newsworthiness_score: int = Field(
        description="How newsworthy / significant is this? 1-10",
        ge=1,
        le=10,
    )
    reasoning: str = Field(description="Brief explanation for the score")


class ArticleSummary(BaseModel):
    """AI-generated summary for one article — part of the newsletter digest."""

    headline: str = Field(description="Catchy 8-12 word headline for the newsletter")
    emoji: str = Field(description="Single relevant emoji")
    source_name: str = Field(description="Original publication name")
    source_url: str = Field(description="Link to original article")
    summary: str = Field(description="2-3 sentence summary of the core insight")
    key_takeaways: list[str] = Field(
        description="2-3 bullet points of crucial facts or quotes",
        min_length=2,
        max_length=4,
    )


class NewsletterDigest(BaseModel):
    """Complete newsletter edition — the final AI output that feeds the template."""

    subject_line: str = Field(
        description="High open-rate email subject line, max 60 characters"
    )
    preview_text: str = Field(
        description="Email preview / preheader text, max 120 characters"
    )
    greeting: str = Field(
        description="Brief engaging opening paragraph, 1-2 sentences"
    )
    articles: list[ArticleSummary] = Field(
        description="3-5 curated article summaries, ordered by importance",
        min_length=1,
        max_length=7,
    )
    tool_of_the_day: Optional[ArticleSummary] = Field(
        description="Optional featured AI tool recommendation",
        default=None,
    )
    closing: str = Field(
        description="Sign-off with CTA to share or reply, 1-2 sentences"
    )


# ---------------------------------------------------------------------------
# Distribution layer models
# ---------------------------------------------------------------------------

class PublishedPost(BaseModel):
    """Result from Beehiiv after publishing."""

    post_id: str
    title: str
    status: str
    scheduled_at: Optional[str] = None
    web_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Pipeline metadata
# ---------------------------------------------------------------------------

class PipelineRun(BaseModel):
    """Metadata for a single pipeline execution — used for logging and caching."""

    run_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    articles_fetched: int = 0
    articles_after_dedup: int = 0
    articles_scored: int = 0
    articles_in_digest: int = 0
    beehiiv_post_id: Optional[str] = None
    status: str = "running"
    error: Optional[str] = None
