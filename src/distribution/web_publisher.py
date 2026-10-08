"""Creavora / AutoDigest — Automated Web Publisher & Archive Engine.

Exports structured daily briefings directly into docs/data/ for automated web publishing,
search indexing, and live website synchronization on https://creavora.my.id.
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Optional

from src.models.schemas import NewsletterDigest

logger = logging.getLogger(__name__)


def publish_web_briefing(
    digest: NewsletterDigest,
    issue_num: Optional[int] = None,
    docs_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Publish today's digest to docs/data/latest_briefing.json and docs/data/archive.json."""
    if docs_dir is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        docs_dir = project_root / "docs"

    data_dir = docs_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    date_str = now_wib.strftime("%b %d, %Y")

    # Determine issue number: calculate from base date or archive count
    archive_file = data_dir / "archive.json"
    existing_archive: list[dict[str, Any]] = []
    if archive_file.exists():
        try:
            with open(archive_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    existing_archive = loaded
        except Exception as e:
            logger.warning(f"Could not read existing archive: {e}")

    if issue_num is None:
        if existing_archive and "issueNum" in existing_archive[0]:
            try:
                issue_num = int(existing_archive[0]["issueNum"]) + 1
            except ValueError:
                issue_num = 143
        else:
            issue_num = 143

    top_article = digest.articles[0] if digest.articles else None
    headline = top_article.headline if top_article else digest.subject_line
    summary = top_article.summary if top_article else digest.greeting
    takeaways = top_article.key_takeaways if top_article else []

    why_it_matters = [
        {
            "bold": f"Core Signal #{idx}:",
            "text": point,
        }
        for idx, point in enumerate(takeaways, 1)
    ]

    links = []
    if top_article:
        links.append({"label": f"{top_article.source_name}: Source Article", "url": top_article.source_url})
    if digest.tool_of_the_day:
        links.append({"label": f"Tool of the Day: {digest.tool_of_the_day.headline}", "url": digest.tool_of_the_day.source_url})

    code_snippet = f"""# Creavora Morning Briefing — Issue #{issue_num}
# Date: {date_str} | Dispatched at 06:00 WIB
# Topic: {headline}

# Key Points:
{chr(10).join([f'# - {p}' for p in takeaways])}

# Source Reference:
# {top_article.source_url if top_article else 'https://creavora.my.id'}"""

    briefing_payload = {
        "issueNum": str(issue_num),
        "date": date_str,
        "timeWib": "06:00 WIB",
        "readTime": "3 min read",
        "category": "FRONTIER INTELLIGENCE",
        "title": headline,
        "summary": summary,
        "whyItMatters": why_it_matters,
        "codeSnippet": code_snippet,
        "links": links,
        "subject_line": digest.subject_line,
        "articles": [
            {
                "headline": a.headline,
                "emoji": a.emoji,
                "source_name": a.source_name,
                "source_url": a.source_url,
                "summary": a.summary,
                "key_takeaways": a.key_takeaways,
            }
            for a in digest.articles
        ],
        "tool_of_the_day": (
            {
                "headline": digest.tool_of_the_day.headline,
                "source_url": digest.tool_of_the_day.source_url,
                "summary": digest.tool_of_the_day.summary,
            }
            if digest.tool_of_the_day
            else None
        ),
    }

    # 1. Write latest_briefing.json
    latest_file = data_dir / "latest_briefing.json"
    try:
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(briefing_payload, f, indent=2, ensure_ascii=False)
        logger.info(f"Published latest briefing to {latest_file.resolve()}")
    except Exception as e:
        logger.error(f"Failed to write latest briefing: {e}")

    # 2. Prepend to archive.json (avoiding duplicate date)
    updated_archive = [briefing_payload] + [
        item for item in existing_archive if item.get("date") != date_str and item.get("issueNum") != str(issue_num)
    ]
    # Keep up to 60 editions in archive
    updated_archive = updated_archive[:60]

    try:
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(updated_archive, f, indent=2, ensure_ascii=False)
        logger.info(f"Updated web archive at {archive_file.resolve()} ({len(updated_archive)} editions)")
    except Exception as e:
        logger.error(f"Failed to update web archive: {e}")

    return briefing_payload
