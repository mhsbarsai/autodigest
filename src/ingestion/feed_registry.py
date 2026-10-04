"""
Feed registry containing the list of sources for AutoDigest.
"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class FeedSource:
    name: str
    url: str
    category: str

FEED_REGISTRY: list[FeedSource] = [
    FeedSource("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "Tech"),
    FeedSource("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "Tech"),
    FeedSource("MIT Tech Review", "https://www.technologyreview.com/feed/", "Science"),
    FeedSource("Ars Technica", "https://feeds.arstechnica.com/arstechnica/technology-lab", "Tech"),
    FeedSource("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "Tech"),
    FeedSource("Hacker News Best", "https://hnrss.org/best?count=30", "Tech"),
    FeedSource("Product Hunt", "https://www.producthunt.com/feed", "Product"),
    FeedSource("OpenAI Blog", "https://openai.com/blog/rss/", "AI"),
    FeedSource("Google AI Blog", "https://blog.google/technology/ai/rss/", "AI"),
    FeedSource("Anthropic Blog", "https://www.anthropic.com/rss.xml", "AI"),
    FeedSource("Hugging Face Blog", "https://huggingface.co/blog/feed.xml", "AI"),
    FeedSource("The Rundown AI", "https://www.therundown.ai/feed", "Newsletter"),
    FeedSource("TLDR AI", "https://tldr.tech/ai/rss", "Newsletter"),
    FeedSource("ArXiv CS.AI", "https://rss.arxiv.org/rss/cs.AI", "Research"),
    FeedSource("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss", "Tech"),
]
