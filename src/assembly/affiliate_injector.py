"""AutoDigest — Affiliate Link Injector.

Scans HTML email content for mentions of known AI productivity tools
and wraps them in affiliate links while preserving existing HTML tags and links.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Registry of supported AI tools and their affiliate / referral URLs.
# In Phase 3, these can be customized with your actual affiliate IDs.
AFFILIATE_MAPPINGS: dict[str, str] = {
    "ChatGPT": "https://chatgpt.com/?ref=autodigest",
    "Claude": "https://claude.ai/?ref=autodigest",
    "Midjourney": "https://www.midjourney.com/?ref=autodigest",
    "Cursor": "https://cursor.com/?ref=autodigest",
    "Notion AI": "https://www.notion.so/product/ai?ref=autodigest",
    "Jasper": "https://www.jasper.ai/?ref=autodigest",
    "Copy.ai": "https://www.copy.ai/?ref=autodigest",
    "Grammarly": "https://www.grammarly.com/?ref=autodigest",
    "Runway": "https://runwayml.com/?ref=autodigest",
    "Perplexity": "https://www.perplexity.ai/?ref=autodigest",
}


def inject_affiliate_links(html: str) -> str:
    """Scan HTML for known tool names and wrap them in affiliate links.

    Safely preserves existing <a> tags and HTML attributes so existing links
    and tags are never broken or double-linked.
    """
    if not html:
        return html

    # Sort tool names longest first so "Notion AI" matches before "Notion"
    tools = sorted(AFFILIATE_MAPPINGS.keys(), key=len, reverse=True)
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
        for tool_name, url in AFFILIATE_MAPPINGS.items():
            if tool_name.lower() == matched_text.lower():
                return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{matched_text}</a>'

        return matched_text

    return composite_pattern.sub(replacer, html)
