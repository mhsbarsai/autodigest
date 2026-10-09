"""Tests for Creavora Autonomous Social Manager & Dynamic Card Generator."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

from src.models.schemas import NewsletterDigest, ArticleSummary
from src.distribution.card_generator import generate_social_card, CARD_WIDTH, CARD_HEIGHT
from src.distribution.social_manager import (
    record_social_history,
    dispatch_webhook_bridge,
    run_autonomous_social_manager,
)


def sample_digest() -> NewsletterDigest:
    return NewsletterDigest(
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


def test_generate_social_card(tmp_path: Path):
    digest = sample_digest()
    card_path = tmp_path / "test_social_card.png"
    docs_path = tmp_path / "docs_card.png"

    result_path = generate_social_card(digest, output_path=card_path, public_docs_path=docs_path)

    assert result_path.exists()
    assert docs_path.exists()

    with Image.open(result_path) as img:
        assert img.size == (CARD_WIDTH, CARD_HEIGHT)
        assert img.format == "PNG"


def test_record_social_history(tmp_path: Path, monkeypatch):
    history_file = tmp_path / "social_history.json"
    monkeypatch.setattr("src.distribution.social_manager.HISTORY_FILE", history_file)

    digest = sample_digest()
    record_social_history(digest, dispatched_channels=["telegram", "bluesky"], card_path="test.png")

    assert history_file.exists()
    with open(history_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]["subject_line"] == "DeepSeek V3 Released: 671B Weights Open"
    assert "telegram" in data[0]["dispatched_channels"]
    assert "bluesky" in data[0]["dispatched_channels"]


def test_dispatch_webhook_bridge_success():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        res = dispatch_webhook_bridge("https://hook.make.com/test", {"test": "data"})
        assert res is True
        mock_post.assert_called_once()


def test_dispatch_webhook_bridge_failure():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_post.return_value = mock_resp

        res = dispatch_webhook_bridge("https://hook.make.com/test", {"test": "data"})
        assert res is False


def test_run_autonomous_social_manager_dry_run(tmp_path: Path):
    digest = sample_digest()
    result = run_autonomous_social_manager(digest, dry_run=True)

    assert "teasers" in result
    assert "card_path" in result
    assert result["card_path"] is not None
    assert Path(result["card_path"]).exists()

    # Check generated markdown
    social_file = Path("output") / "today_social_teasers.md"
    assert social_file.exists()
    content = social_file.read_text(encoding="utf-8")
    assert "Creavora — Today's Social Teasers" in content
    assert "DeepSeek V3" in content
