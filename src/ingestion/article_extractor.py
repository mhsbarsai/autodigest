"""
Module to extract clean article text from a URL.
"""
from __future__ import annotations

import logging
import trafilatura
from tenacity import retry, stop_after_attempt

from src.models.schemas import RawArticle

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(2))
def extract_article_text(url: str, timeout: int = 10) -> str:
    """
    Extracts article text from URL using trafilatura.
    """
    logger.debug(f"Extracting text from: {url}")
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return ""
        text = trafilatura.extract(downloaded)
        return text if text else ""
    except Exception as e:
        logger.warning(f"Error extracting text from {url}: {e}")
        return ""

def enrich_articles(articles: list[RawArticle], max_articles: int = 20) -> list[RawArticle]:
    """
    Enrich articles by extracting full text for top N articles.
    """
    enriched = []
    
    top_articles = articles[:max_articles]
    logger.info(f"Enriching top {len(top_articles)} articles.")
    
    for idx, article in enumerate(top_articles):
        text = extract_article_text(article.url)
        if text:
            word_count = len(text.split())
            if word_count >= 50:
                article.raw_text = text
                article.word_count = word_count
                enriched.append(article)
            else:
                logger.info(f"Article {article.url} dropped: word count {word_count} < 50.")
        else:
            logger.info(f"Article {article.url} dropped: no text extracted.")
            
        if (idx + 1) % 5 == 0:
            logger.info(f"Processed {idx + 1}/{len(top_articles)} articles.")
            
    return enriched
