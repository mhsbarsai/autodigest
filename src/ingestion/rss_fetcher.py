"""
Module to fetch RSS feeds.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
import feedparser
from dateutil import parser as dateutil_parser
from tenacity import retry, stop_after_attempt, wait_exponential

from src.models.schemas import RawArticle
from src.ingestion.feed_registry import FeedSource, FEED_REGISTRY

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
def fetch_feed(source: FeedSource, timeout: int = 15) -> list[RawArticle]:
    """
    Fetch a single RSS feed.
    """
    articles = []
    logger.info(f"Fetching feed: {source.name} at {source.url}")
    
    feed = feedparser.parse(source.url)
    
    if getattr(feed, 'bozo', 0) == 1 and not feed.entries:
        logger.warning(f"Failed to parse feed or empty feed for {source.name}")
        return articles
        
    for entry in feed.entries:
        title = entry.get("title", "")
        url = entry.get("link", "")
        
        published_at = datetime.now(timezone.utc)
        if hasattr(entry, "published"):
            try:
                published_at = dateutil_parser.parse(entry.published)
            except Exception:
                pass
        
        if title and url:
            try:
                article = RawArticle(
                    title=title,
                    url=url,
                    published_at=published_at,
                    source_name=source.name,
                )
                articles.append(article)
            except Exception as e:
                logger.warning(f"Error creating RawArticle for {url}: {e}")
                
    return articles

def fetch_all_feeds(registry: list[FeedSource] | None = None) -> list[RawArticle]:
    """
    Iterates all feeds and fetches articles.
    """
    if registry is None:
        registry = FEED_REGISTRY
        
    all_articles = []
    
    for source in registry:
        try:
            articles = fetch_feed(source)
            all_articles.extend(articles)
        except Exception as e:
            logger.warning(f"Exception while fetching {source.name}: {e}")
            
    all_articles.sort(key=lambda a: a.published_at, reverse=True)
    return all_articles
