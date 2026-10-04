"""AutoDigest unit tests for data models, deduplication, templating, and affiliate injection."""

from __future__ import annotations

from datetime import datetime, timezone
import pytest

from src.models.schemas import (
    RawArticle,
    ScoredArticle,
    ArticleSummary,
    NewsletterDigest,
    PublishedPost,
    PipelineRun,
)
from src.ingestion.deduplicator import deduplicate, get_updated_seen_hashes
from src.assembly.template_engine import render_newsletter
from src.assembly.affiliate_injector import inject_affiliate_links
from src.assembly.sponsor_slot import inject_sponsor


def test_raw_article_hash_stability():
    art1 = RawArticle(
        title="OpenAI Releases New Model",
        url="https://example.com/openai-new",
        source_name="TechCrunch",
    )
    art2 = RawArticle(
        title="openai releases new model",
        url="https://example.com/openai-new/",
        source_name="TechCrunch",
    )
    # The content_hash strips trailing slash and lowercases
    assert art1.content_hash == art2.content_hash


def test_deduplicator_filters_seen():
    art1 = RawArticle(title="A", url="https://a.com", source_name="S1")
    art2 = RawArticle(title="B", url="https://b.com", source_name="S2")
    art3 = RawArticle(title="C", url="https://c.com", source_name="S3")

    seen = {art1.content_hash, art3.content_hash}
    fresh = deduplicate([art1, art2, art3], seen_hashes=seen)

    assert len(fresh) == 1
    assert fresh[0].title == "B"


def test_get_updated_seen_hashes_limit():
    existing = {f"hash_{i}" for i in range(100)}
    new_articles = [
        RawArticle(title=f"New {i}", url=f"https://example.com/{i}", source_name="S")
        for i in range(10)
    ]
    updated = get_updated_seen_hashes(existing, new_articles, max_history=50)
    assert len(updated) <= 50


def test_render_newsletter_template():
    digest = NewsletterDigest(
        subject_line="🤖 3 Breakthrough AI Tools for Today",
        preview_text="Here is your quick morning brief.",
        greeting="Good morning! Today brings exciting advances in autonomous agents.",
        articles=[
            ArticleSummary(
                headline="Claude 3.7 Sonnet Unleashes Hybrid Reasoning",
                emoji="⚡",
                source_name="Anthropic",
                source_url="https://anthropic.com/news",
                summary="Anthropic launched their hybrid model capable of instant responses or deep chain-of-thought.",
                key_takeaways=[
                    "Supports scalable thinking budgets",
                    "Surpasses prior benchmarks on coding",
                ],
            )
        ],
        tool_of_the_day=ArticleSummary(
            headline="Cursor Editor Gets Supercharged",
            emoji="🛠️",
            source_name="Cursor",
            source_url="https://cursor.com",
            summary="An AI-native code editor that revolutionizes software engineering.",
            key_takeaways=["Composer multi-file editing", "Deep repo context"],
        ),
        closing="Have a productive day! Hit reply if you enjoyed this.",
    )

    html = render_newsletter(digest, newsletter_name="AutoDigest", edition_number=42)

    assert "AutoDigest" in html
    assert "#42" in html
    assert "Claude 3.7 Sonnet" in html
    assert "Cursor Editor" in html
    assert "Good morning!" in html


def test_affiliate_injection():
    sample_html = "<p>Try out Cursor and Notion AI to boost your team productivity.</p>"
    result = inject_affiliate_links(sample_html)
    assert 'href="https://cursor.com' in result or 'affiliate' in result
    assert "Notion AI" in result


def test_sponsor_slot():
    sample_html = "<div>Content</div><!-- SPONSOR_PLACEHOLDER -->{{SPONSOR_SLOT}}<div>Footer</div>"

    # With sponsor
    sponsored = inject_sponsor(
        sample_html,
        sponsor_name="Acme Cloud",
        sponsor_text="The fastest hosting for AI workloads.",
        sponsor_url="https://acmecloud.com",
    )
    assert "Acme Cloud" in sponsored
    assert "https://acmecloud.com" in sponsored

    # Without sponsor
    empty_sponsor = inject_sponsor(sample_html)
    assert "{{SPONSOR_SLOT}}" not in empty_sponsor


def test_resend_client_direct_email():
    from unittest.mock import patch
    from src.config import ResendConfig
    from src.distribution.resend_client import ResendClient

    config = ResendConfig(
        api_key="re_test_123",
        from_email="AutoDigest <onboarding@resend.dev>",
        to_email="test@example.com",
    )
    client = ResendClient(config)

    with patch("src.distribution.subscriber_manager.SubscriberManager.get_active_subscribers", return_value=[]), \
         patch("resend.Emails.send", return_value={"id": "email_123"}) as mock_send:
        post = client.publish_newsletter(
            subject="Test Subject",
            html_content="<p>Test</p>",
        )
        assert post.post_id == "email_123"
        assert post.status == "sent"
        mock_send.assert_called_once()


def test_resend_client_batch_email():
    from unittest.mock import patch
    from src.config import ResendConfig
    from src.distribution.resend_client import ResendClient

    config = ResendConfig(
        api_key="re_test_123",
        from_email="AutoDigest <onboarding@resend.dev>",
        to_email="",
    )
    client = ResendClient(config)

    with patch("src.distribution.subscriber_manager.SubscriberManager.get_active_subscribers", return_value=["sub1@example.com", "sub2@example.com"]), \
         patch("resend.Batch.send", return_value=[{"id": "b1"}, {"id": "b2"}]) as mock_batch:
        post = client.publish_newsletter(
            subject="Batch Subject",
            html_content="<p>Batch Content</p>",
        )
        assert post.post_id.startswith("batch_")
        assert post.status == "sent"
        mock_batch.assert_called_once()


def test_resend_client_broadcast():
    from unittest.mock import patch
    from src.config import ResendConfig
    from src.distribution.resend_client import ResendClient

    config = ResendConfig(
        api_key="re_test_123",
        from_email="AutoDigest <onboarding@resend.dev>",
        audience_id="aud_123",
    )
    client = ResendClient(config)

    with patch("resend.Broadcasts.create", return_value={"id": "bcast_123"}) as mock_bcast:
        post = client.publish_newsletter(
            subject="Test Broadcast",
            html_content="<p>Broadcast content</p>",
        )
        assert post.post_id == "bcast_123"
        mock_bcast.assert_called_once()


def test_social_teaser_generation():
    from src.distribution.social_poster import generate_social_teasers, distribute_social

    digest = NewsletterDigest(
        subject_line="DeepSeek V3 Released: 671B Weights Open",
        preview_text="Full architecture breakdown inside.",
        greeting="Good morning AI engineers!",
        articles=[
            ArticleSummary(
                headline="DeepSeek V3 Matches Claude 3.5 Sonnet",
                emoji="🚀",
                source_name="Hacker News",
                source_url="https://news.ycombinator.com/item?id=1",
                summary="DeepSeek released their flagship open model.",
                key_takeaways=["FP8 native support", "MLA architecture cuts VRAM by 50%"],
            )
        ],
        tool_of_the_day=ArticleSummary(
            headline="vLLM Inference Engine",
            emoji="⚡",
            source_name="GitHub",
            source_url="https://github.com/vllm-project/vllm",
            summary="High-throughput serving engine for LLMs.",
            key_takeaways=["PagedAttention implementation", "Continuous batching with zero memory waste"],
        ),
        closing="See you tomorrow!",
    )

    teasers = generate_social_teasers(digest)
    assert len(teasers["x_thread"]) == 3
    assert "DeepSeek V3" in teasers["x_thread"][0]
    assert "https://creavora.my.id/" in teasers["x_thread"][2]
    assert "LinkedIn" not in teasers["linkedin_post"]  # should be clean body
    assert "vLLM Inference Engine" in teasers["linkedin_post"]
    assert "discord_payload" in teasers
    assert len(teasers["discord_payload"]["embeds"][0]["fields"]) == 2

    # Test distribute_social in dry_run mode
    result = distribute_social(digest, dry_run=True)
    assert "x_thread" in result
