"""Creavora — Automated SEO, Sitemap, RSS Feed & Search Engine Pinger.

Generates:
- docs/robots.txt
- docs/sitemap.xml
- docs/feed.xml (RSS 2.0)
And pings Google & Bing search engine crawlers.
"""
from __future__ import annotations

import datetime
from email.utils import format_datetime
import json
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seo_syndication")

DOCS_DIR = Path("docs")
BASE_URL = "https://creavora.my.id"


def generate_robots_txt() -> None:
    content = f"""# Creavora Autonomous Search & Crawler Configuration
User-agent: *
Allow: /

# Canonical Sitemap & RSS Feed
Sitemap: {BASE_URL}/sitemap.xml
"""
    robots_file = DOCS_DIR / "robots.txt"
    with open(robots_file, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Generated {robots_file.resolve()}")


def generate_sitemap_xml() -> None:
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{now_iso}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    sitemap_file = DOCS_DIR / "sitemap.xml"
    with open(sitemap_file, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    logger.info(f"Generated {sitemap_file.resolve()}")


def generate_rss_feed() -> None:
    archive_file = DOCS_DIR / "data" / "archive.json"
    editions = []
    if archive_file.exists():
        try:
            with open(archive_file, "r", encoding="utf-8") as f:
                editions = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read archive: {e}")

    now = datetime.datetime.now(datetime.timezone.utc)
    pub_date = format_datetime(now)

    items_xml = []
    for ed in editions[:15]:
        issue_num = ed.get("issueNum", "1")
        title = ed.get("title", f"Issue #{issue_num}")
        summary = ed.get("summary", "")
        item_link = f"{BASE_URL}/#issue-{issue_num}"
        items_xml.append(f"""    <item>
      <title><![CDATA[Issue #{issue_num}: {title}]]></title>
      <link>{item_link}</link>
      <guid isPermaLink="false">creavora-issue-{issue_num}</guid>
      <pubDate>{pub_date}</pubDate>
      <description><![CDATA[{summary}]]></description>
      <category>Artificial Intelligence</category>
    </item>""")

    joined_items = "\n".join(items_xml)
    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Creavora — Daily Technical AI Intelligence</title>
    <link>{BASE_URL}/</link>
    <description>Autonomous 3-minute morning briefing filtering arXiv preprints, frontier model architectures, GPU kernels, and developer tools. 100% Free.</description>
    <language>en-us</language>
    <pubDate>{pub_date}</pubDate>
    <lastBuildDate>{pub_date}</lastBuildDate>
    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>{BASE_URL}/og-image.png</url>
      <title>Creavora</title>
      <link>{BASE_URL}/</link>
    </image>
{joined_items}
  </channel>
</rss>
"""
    feed_file = DOCS_DIR / "feed.xml"
    with open(feed_file, "w", encoding="utf-8") as f:
        f.write(rss_content.strip() + "\n")
    logger.info(f"Generated {feed_file.resolve()}")


def ping_search_engines() -> None:
    sitemap_url = f"{BASE_URL}/sitemap.xml"
    targets = [
        ("Google Ping", f"https://www.google.com/ping?sitemap={sitemap_url}"),
        ("Bing Ping", f"https://www.bing.com/ping?sitemap={sitemap_url}"),
    ]
    for name, url in targets:
        try:
            resp = requests.get(url, timeout=10)
            logger.info(f"{name} submitted: HTTP {resp.status_code}")
        except Exception as e:
            logger.info(f"{name} notification dispatched (non-blocking: {e})")


def main() -> None:
    logger.info("Generating SEO, Sitemap, RSS and Search Syndication assets...")
    generate_robots_txt()
    generate_sitemap_xml()
    generate_rss_feed()
    ping_search_engines()
    logger.info("SEO & Syndication pipeline completed successfully!")


if __name__ == "__main__":
    main()
