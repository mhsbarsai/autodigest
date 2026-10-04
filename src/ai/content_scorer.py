from __future__ import annotations

"""
Module for scoring raw articles based on relevance and newsworthiness.
"""

import logging
from pydantic import BaseModel, Field

from src.models.schemas import RawArticle, ScoredArticle
from src.ai.gemini_client import GeminiClient
from src.ai.prompts import SCORER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ArticleScore(BaseModel):
    title: str = Field(description="The title of the article")
    url: str = Field(description="The URL of the article")
    relevance_score: int = Field(description="Relevance score from 1-10", ge=1, le=10)
    newsworthiness_score: int = Field(description="Newsworthiness score from 1-10", ge=1, le=10)
    combined_score: int = Field(description="Combined score from 1-10", ge=1, le=10)
    reasoning: str = Field(description="Brief reasoning for the scores")

class ScoringResult(BaseModel):
    scores: list[ArticleScore] = Field(description="List of scored articles")

def score_articles(articles: list[RawArticle], client: GeminiClient, top_k: int = 5) -> list[ScoredArticle]:
    """Score a list of raw articles and return the top K scored articles."""
    if not articles:
        logger.warning("No articles provided for scoring.")
        return []
    
    logger.info(f"Scoring {len(articles)} articles...")
    
    prompt_parts = ["Please score the following articles:\n"]
    for i, article in enumerate(articles):
        # Taking first 200 words approximately (splitting by space)
        text_preview = " ".join((article.raw_text or "").split()[:200])
        prompt_parts.append(
            f"Article {i+1}:\n"
            f"Title: {article.title}\n"
            f"URL: {article.url}\n"
            f"Preview: {text_preview}\n"
            "---"
        )
    prompt = "\n".join(prompt_parts)
    
    try:
        result: ScoringResult = client.generate_structured(
            prompt=prompt,
            system_instruction=SCORER_SYSTEM_PROMPT,
            response_schema=ScoringResult
        )
        
        # Map back to ScoredArticle
        def _norm_url(u: str) -> str:
            return u.strip().rstrip("/").lower()

        article_map = {_norm_url(a.url): a for a in articles}
        title_map = {a.title.strip().lower(): a for a in articles}

        scored_articles: list[ScoredArticle] = []
        for score in result.scores:
            norm_u = _norm_url(score.url)
            norm_t = score.title.strip().lower()
            raw = article_map.get(norm_u) or title_map.get(norm_t)
            if raw:
                scored_articles.append(
                    ScoredArticle(
                        title=raw.title,
                        url=raw.url,
                        source_name=raw.source_name,
                        raw_text=raw.raw_text,
                        relevance_score=score.relevance_score,
                        newsworthiness_score=score.newsworthiness_score,
                        reasoning=score.reasoning,
                    )
                )

        # Sort and take top k
        scored_articles.sort(
            key=lambda x: (x.relevance_score + x.newsworthiness_score),
            reverse=True,
        )
        return scored_articles[:top_k]
        
    except Exception as e:
        logger.error(f"Failed to score articles: {e}")
        return []
