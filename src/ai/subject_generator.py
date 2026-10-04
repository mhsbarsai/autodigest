from __future__ import annotations

"""
Module for generating subject lines and preview text for the newsletter.
"""

import logging
from pydantic import BaseModel, Field

from src.models.schemas import NewsletterDigest
from src.ai.gemini_client import GeminiClient
from src.ai.prompts import SUBJECT_LINE_PROMPT

logger = logging.getLogger(__name__)

class SubjectResponse(BaseModel):
    subject_line: str = Field(description="The generated email subject line")
    preview_text: str = Field(description="The generated email preview text")

def generate_subject_line(digest: NewsletterDigest, client: GeminiClient) -> tuple[str, str]:
    """Generate an optimized subject line and preview text based on the digest content."""
    logger.info("Generating subject line...")
    
    prompt_parts = ["Based on the following newsletter content, generate a subject line and preview text.\n\n"]
    if digest.articles:
        for article in digest.articles:
            prompt_parts.append(f"Title: {article.headline}\nSummary: {article.summary}\n\n")
    
    prompt = "".join(prompt_parts)
    
    try:
        response: SubjectResponse = client.generate_structured(
            prompt=prompt,
            system_instruction=SUBJECT_LINE_PROMPT,
            response_schema=SubjectResponse
        )
        return response.subject_line, response.preview_text
    except Exception as e:
        logger.error(f"Failed to generate subject line: {e}")
        return digest.subject_line, "Your daily dose of AI news."
