"""NeuralBrief / AutoDigest — Affiliate Link Injector.

Scans HTML email content for mentions of known AI productivity tools
and wraps them in affiliate links while preserving existing HTML tags and links.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)

# Default registry of supported AI tools and their affiliate / referral URLs.
# Users can override or add their own custom links in data/affiliate_links.json.
DEFAULT_AFFILIATE_MAPPINGS: dict[str, str] = {
    "Cursor": "https://cursor.com/?ref=neuralbrief",
    "Perplexity": "https://www.perplexity.ai/?ref=neuralbrief",
    "Notion AI": "https://www.notion.so/product/ai?ref=neuralbrief",
    "Claude": "https://claude.ai/?ref=neuralbrief",
    "ChatGPT": "https://chatgpt.com/?ref=neuralbrief",
    "Midjourney": "https://www.midjourney.com/?ref=neuralbrief",
    "Runway": "https://runwayml.com/?ref=neuralbrief",
    "ElevenLabs": "https://elevenlabs.io/?ref=neuralbrief",
    "Make": "https://www.make.com/en/register?ref=neuralbrief",
    "Jasper": "https://www.jasper.ai/?ref=neuralbrief",
    "Copy.ai": "https://www.copy.ai/?ref=neuralbrief",
    "Grammarly": "https://www.grammarly.com/?ref=neuralbrief",
}


def load_affiliate_mappings() -> dict[str, str]:
    """Load affiliate links from data/affiliate_links.json, falling back to defaults."""
    mappings = dict(DEFAULT_AFFILIATE_MAPPINGS)
    project_root = Path(__file__).resolve().parent.parent.parent
    config_file = project_root / "data" / "affiliate_links.json"

    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                user_mappings = json.load(f)
                if isinstance(user_mappings, dict):
                    mappings.update(user_mappings)
                    logger.info(f"Loaded {len(user_mappings)} custom affiliate mappings from {config_file.name}")
        except Exception as e:
            logger.warning(f"Could not load custom affiliate mappings: {e}")

    return mappings


def inject_affiliate_links(html: str) -> str:
    """Scan HTML for known tool names and wrap them in affiliate links.

    Safely preserves existing <a> tags and HTML attributes so existing links
    and tags are never broken or double-linked.
    """
    if not html:
        return html

    mappings = load_affiliate_mappings()

    # Sort tool names longest first so "Notion AI" matches before "Notion"
    tools = sorted(mappings.keys(), key=len, reverse=True)
    tools_pattern = "|".join(re.escape(t) for t in tools)

    # Regex matches:
    # 1) Existing <a ...>...</a> tags (captured in group 1 -> preserved as-is)
    # 2) Any HTML tag <...> (captured in group 2 -> preserved as-is)
    # 3) Standalone tool names in plain text (captured in group 3 -> linked)
    composite_pattern = re.compile(
        rf"(<a\b[^>]*>.*?</a>)|(<[^>]+>)|(\b(?:{tools_pattern})\b)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    def replacer(match: re.Match) -> str:
        # If it matched an existing link, keep it unchanged
        if match.group(1):
            return match.group(1)
        # If it matched any HTML tag, keep it unchanged
        if match.group(2):
            return match.group(2)

        # Matched plain text tool name
        matched_text = match.group(3)
        for tool_name, url in mappings.items():
            if tool_name.lower() == matched_text.lower():
                return f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="color:#6366f1;text-decoration:underline;">{matched_text}</a>'

        return matched_text

    return composite_pattern.sub(replacer, html)
