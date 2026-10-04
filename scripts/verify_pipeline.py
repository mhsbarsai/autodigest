"""Standalone verification test script using Python standard library (no pytest required)."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

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


def test_raw_article_hash():
    print("[TEST] Testing RawArticle hash...")
    art1 = RawArticle(
        title="OpenAI Releases New Model",
        url="https://example.com/openai-new",
        source_name="TechCrunch",
    )
    art2 = RawArticle(
        title="OpenAI Releases New Model",
        url="https://example.com/openai-new",
        source_name="TechCrunch",
    )
    assert art1.content_hash == art2.content_hash
    print("  -> Passed!")


def test_deduplicator():
    print("[TEST] Testing Deduplication...")
    art1 = RawArticle(title="A", url="https://a.com", source_name="S1")
    art2 = RawArticle(title="B", url="https://b.com", source_name="S2")
    art3 = RawArticle(title="C", url="https://c.com", source_name="S3")

    seen = {art1.content_hash, art3.content_hash}
    fresh = deduplicate([art1, art2, art3], seen_hashes=seen)
    assert len(fresh) == 1
    assert fresh[0].title == "B"
    print("  -> Passed!")


def test_template_rendering():
    print("[TEST] Testing Jinja2 Template Rendering...")
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
    print("  -> Passed! (Length:", len(html), "bytes)")


def test_affiliate_and_sponsor():
    print("[TEST] Testing Affiliate Links & Sponsor Injection...")
    sample_html = "<p>Try out Cursor for fast programming.</p><!-- SPONSOR -->{{SPONSOR_SLOT}}"
    with_affiliate = inject_affiliate_links(sample_html)
    assert "cursor" in with_affiliate.lower()

    sponsored = inject_sponsor(
        with_affiliate,
        sponsor_name="Acme Cloud",
        sponsor_text="High performance hosting",
        sponsor_url="https://acme.com",
    )
    assert "Acme Cloud" in sponsored
    assert "{{SPONSOR_SLOT}}" not in sponsored
    print("  -> Passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Running AutoDigest Self-Verification Tests")
    print("=" * 60)
    try:
        test_raw_article_hash()
        test_deduplicator()
        test_template_rendering()
        test_affiliate_and_sponsor()
        print("=" * 60)
        print("ALL TESTS PASSED SUCCESSFULLY! [OK]")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAILED] Test Failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
