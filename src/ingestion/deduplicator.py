"""
Module to deduplicate articles.
"""
from __future__ import annotations

import logging
from typing import Set

from src.models.schemas import RawArticle

logger = logging.getLogger(__name__)

def deduplicate(articles: list[RawArticle], seen_hashes: set[str]) -> list[RawArticle]:
    """
    Filters out articles whose content_hash is already in seen_hashes.
    """
    new_articles = []
    for article in articles:
        h = getattr(article, "content_hash", "")
        if not h:
            h = str(hash(article.url))
            
        if h not in seen_hashes:
            new_articles.append(article)
        else:
            logger.debug(f"Article duplicate dropped: {article.url}")
            
    return new_articles

def get_updated_seen_hashes(existing: set[str], new_articles: list[RawArticle], max_history: int = 5000) -> set[str]:
    """
    Merge existing hashes with new article hashes, keeping the most recent max_history entries.
    """
    new_hashes = []
    for article in new_articles:
        h = getattr(article, "content_hash", "")
        if not h:
            h = str(hash(article.url))
        new_hashes.append(h)
        
    combined = list(existing) + new_hashes
    
    if len(combined) > max_history:
        combined = combined[-max_history:]
        
    return set(combined)
