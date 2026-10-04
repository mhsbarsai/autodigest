from __future__ import annotations

"""
Client wrapper for interacting with the Google Gemini API.
"""

import json
import logging
from typing import TypeVar

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types

from src.config import GeminiConfig

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(self, config: GeminiConfig) -> None:
        """Initialize the Gemini client with the given configuration."""
        self.config = config
        self.client = genai.Client(api_key=config.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def generate_structured(
        self, prompt: str, system_instruction: str, response_schema: type[T], temperature: float | None = None
    ) -> T:
        """Generate structured JSON output validated by a Pydantic model."""
        try:
            logger.info("Generating structured content with Gemini...")
            schema_dict = response_schema.model_json_schema()
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type='application/json',
                response_schema=schema_dict,
                temperature=temperature if temperature is not None else self.config.temperature,
            )
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=prompt,
                config=config
            )
            if not response.text:
                raise ValueError("Received empty response from Gemini API.")
            
            data = json.loads(response.text)
            return response_schema.model_validate(data)
        except Exception as e:
            logger.error(f"Error in generate_structured: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def generate_text(
        self, prompt: str, system_instruction: str, temperature: float | None = None
    ) -> str:
        """Generate plain text output."""
        try:
            logger.info("Generating text content with Gemini...")
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature if temperature is not None else self.config.temperature,
            )
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=prompt,
                config=config
            )
            if not response.text:
                raise ValueError("Received empty response from Gemini API.")
            
            return response.text
        except Exception as e:
            logger.error(f"Error in generate_text: {e}")
            raise
