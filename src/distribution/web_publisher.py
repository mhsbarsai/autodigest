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

    # 3. Update RSS Feed (docs/feed.xml) and Sitemap (docs/sitemap.xml)
    try:
        _update_rss_feed(docs_dir, updated_archive)
        _update_sitemap(docs_dir)
    except Exception as e:
        logger.warning(f"Non-fatal error updating RSS/Sitemap: {e}")

    return briefing_payload


def _update_rss_feed(docs_dir: Path, editions: list[dict[str, Any]]) -> None:
    """Generate RSS 2.0 feed from latest editions."""
    base_url = "https://creavora.my.id"
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    pub_date = now_utc.strftime("%a, %d %b %Y %H:%M:%S +0000")

    items_xml = []
    for ed in editions[:20]:
        issue_num = ed.get("issueNum", "1")
        title = ed.get("title", f"Issue #{issue_num}")
        summary = ed.get("summary", "")
        item_link = f"{base_url}/#issue-{issue_num}"
        items_xml.append(f"""    <item>
      <title><![CDATA[Issue #{issue_num}: {title}]]></title>
      <link>{item_link}</link>
      <guid isPermaLink="false">creavora-issue-{issue_num}</guid>
      <pubDate>{pub_date}</pubDate>
      <description><![CDATA[{summary}]]></description>
      <category>Artificial Intelligence</category>
    </item>""")

    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Creavora — Daily Technical AI Intelligence</title>
    <link>{base_url}/</link>
    <description>Autonomous 3-minute morning briefing filtering arXiv preprints, frontier model architectures, GPU kernels, and developer tools. 100% Free.</description>
    <language>en-us</language>
    <pubDate>{pub_date}</pubDate>
    <lastBuildDate>{pub_date}</lastBuildDate>
    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>{base_url}/og-image.png</url>
      <title>Creavora</title>
      <link>{base_url}/</link>
    </image>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    feed_file = docs_dir / "feed.xml"
    with open(feed_file, "w", encoding="utf-8") as f:
        f.write(feed_xml.strip() + "\n")
    logger.info(f"Updated live RSS 2.0 feed at {feed_file.resolve()}")


def _update_sitemap(docs_dir: Path) -> None:
    """Generate search engine sitemap.xml."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://creavora.my.id/</loc>
    <lastmod>{now_iso}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    sitemap_file = docs_dir / "sitemap.xml"
    with open(sitemap_file, "w", encoding="utf-8") as f:
        f.write(sitemap_xml.strip() + "\n")
    logger.info(f"Updated sitemap at {sitemap_file.resolve()}")
