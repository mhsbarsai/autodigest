from __future__ import annotations

"""
Module for summarizing scored articles and creating a newsletter digest.
"""

import logging
from datetime import datetime

from src.models.schemas import ScoredArticle, NewsletterDigest
from src.ai.gemini_client import GeminiClient
from src.ai.prompts import EDITORIAL_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

def summarize_articles(scored_articles: list[ScoredArticle], client: GeminiClient) -> NewsletterDigest | None:
    """Summarize scored articles into a complete newsletter digest."""
    if not scored_articles:
        logger.warning("No scored articles provided for summarization.")
        return None
        
    logger.info(f"Summarizing {len(scored_articles)} articles...")
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    prompt_parts = [
        f"Create a newsletter digest for today: {today_date}.\n",
        "Here are the top articles to include:\n"
    ]
    
    for i, article in enumerate(scored_articles):
        text_content = article.raw_text if article.raw_text else ""
        prompt_parts.append(
            f"Article {i+1}:\n"
            f"Title: {article.title}\n"
            f"Source: {article.source_name}\n"
            f"URL: {article.url}\n"
            f"Content: {text_content}\n"
            "---"
        )
        
    prompt = "\n".join(prompt_parts)
    
    try:
        digest: NewsletterDigest = client.generate_structured(
            prompt=prompt,
            system_instruction=EDITORIAL_SYSTEM_PROMPT,
            response_schema=NewsletterDigest
        )
        return digest
    except Exception as e:
        logger.error(f"Failed to summarize articles: {e}")
        return None
