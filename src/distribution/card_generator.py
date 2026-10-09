"""Creavora Dynamic Social Media Card & Banner Generator.

Generates high-resolution 1200x630 dark-editorial preview cards for daily briefings
using Pillow (PIL). Produces professional visuals ready for X/Twitter, LinkedIn,
Bluesky, and Telegram.
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import textwrap
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from src.models.schemas import NewsletterDigest

logger = logging.getLogger(__name__)

# Standard social card dimensions (OpenGraph / Twitter Card)
CARD_WIDTH = 1200
CARD_HEIGHT = 630

# Editorial Dark Theme Palette
COLOR_BG = (11, 15, 25)          # Deep obsidian navy #0b0f19
COLOR_CARD_BG = (17, 24, 39)     # Surface card #111827
COLOR_BORDER = (31, 41, 55)      # Slate border #1f2937
COLOR_PRIMARY = (99, 102, 241)   # Electric Indigo #6366f1
COLOR_ACCENT = (129, 140, 248)   # Light Indigo #818cf8
COLOR_TEXT_WHITE = (248, 250, 252) # Clean white #f8fafc
COLOR_TEXT_MUTED = (156, 163, 175) # Slate gray #9ca3af
COLOR_BADGE_BG = (30, 27, 75)    # Dark indigo badge #1e1b4b
COLOR_BADGE_BORDER = (99, 102, 241)


def _get_font(size: int, bold: bool = False) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """Find a readable system TTF font across Windows/Linux, with graceful default fallback."""
    candidate_fonts: list[str] = []
    if bold:
        candidate_fonts.extend([
            "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "Roboto-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
        ])
    else:
        candidate_fonts.extend([
            "segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "Roboto-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
        ])

    for font_name in candidate_fonts:
        try:
            return ImageFont.truetype(font_name, size)
        except (OSError, IOError):
            continue

    try:
        return ImageFont.load_default(size=size)  # Pillow 10+ supports size
    except TypeError:
        return ImageFont.load_default()


def generate_social_card(
    digest: NewsletterDigest,
    output_path: Optional[Path | str] = None,
    public_docs_path: Optional[Path | str] = None,
) -> Path:
    """Generate a 1200x630 dark editorial social preview banner for today's briefing."""
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), color=COLOR_BG)
    draw = ImageDraw.Draw(img)

    # 1. Background Grid / Subtle Technical Accent Lines
    grid_spacing = 40
    for x in range(0, CARD_WIDTH, grid_spacing):
        draw.line([(x, 0), (x, CARD_HEIGHT)], fill=(16, 22, 36), width=1)
    for y in range(0, CARD_HEIGHT, grid_spacing):
        draw.line([(0, y), (CARD_WIDTH, y)], fill=(16, 22, 36), width=1)

    # 2. Main Content Container (Rounded Slate Card)
    margin = 36
    card_rect = [margin, margin, CARD_WIDTH - margin, CARD_HEIGHT - margin]
    draw.rounded_rectangle(card_rect, radius=20, fill=COLOR_CARD_BG, outline=COLOR_BORDER, width=2)

    # Glowing Top Accent Bar
    draw.line([(margin + 20, margin), (CARD_WIDTH - margin - 20, margin)], fill=COLOR_PRIMARY, width=4)

    # Fonts
    font_brand = _get_font(22, bold=True)
    font_badge = _get_font(16, bold=True)
    font_title = _get_font(42, bold=True)
    font_subtitle = _get_font(20, bold=False)
    font_highlight = _get_font(18, bold=False)
    font_footer = _get_font(18, bold=True)

    # 3. Header Section (Brand + Date Badge)
    header_y = margin + 35
    # Brand tag
    draw.text((margin + 45, header_y), "CREAVORA", fill=COLOR_TEXT_WHITE, font=font_brand)
    draw.text((margin + 185, header_y + 3), "//  DAILY TECHNICAL AI INTELLIGENCE", fill=COLOR_PRIMARY, font=font_badge)

    # Date / Issue Badge on right
    today_str = datetime.now(timezone.utc).strftime("%d %b %Y • 06:00 WIB")
    date_badge_text = f"ISSUE #145 • {today_str}"
    draw.text((CARD_WIDTH - margin - 350, header_y + 3), date_badge_text, fill=COLOR_TEXT_MUTED, font=font_badge)

    # Separator Line
    draw.line([(margin + 45, header_y + 35), (CARD_WIDTH - margin - 45, header_y + 35)], fill=COLOR_BORDER, width=1)

    # 4. Main Headline (Wrapped)
    title_text = digest.subject_line or "Frontier AI Architecture & Open Weights Breakdown"
    # Clean emoji or prefixes if needed
    cleaned_title = title_text.replace("⚡", "").replace("🧠", "").replace("🚨", "").strip()
    wrapped_title = textwrap.fill(cleaned_title, width=38)

    title_y = header_y + 60
    draw.text((margin + 45, title_y), wrapped_title, fill=COLOR_TEXT_WHITE, font=font_title, spacing=10)

    # Calculate height taken by title
    num_title_lines = len(wrapped_title.split("\n"))
    title_height = num_title_lines * 52

    # 5. Core Signal Box (What's Inside / Tool of the Day)
    box_y = title_y + title_height + 25
    box_rect = [margin + 45, box_y, CARD_WIDTH - margin - 45, box_y + 110]
    draw.rounded_rectangle(box_rect, radius=12, fill=COLOR_BADGE_BG, outline=COLOR_BADGE_BORDER, width=1)

    # Highlight Content inside the box
    highlight_icon_y = box_y + 20
    draw.text((margin + 70, highlight_icon_y), "TOP ENGINEERING HIGHLIGHTS TODAY:", fill=COLOR_ACCENT, font=font_badge)

    if digest.articles:
        top_art = digest.articles[0]
        summary_snip = top_art.headline
        if top_art.key_takeaways:
            summary_snip += f" — {top_art.key_takeaways[0]}"
        wrapped_highlight = textwrap.shorten(summary_snip, width=95, placeholder="...")
        draw.text((margin + 70, highlight_icon_y + 28), f"▸ {wrapped_highlight}", fill=COLOR_TEXT_WHITE, font=font_highlight)

    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        draw.text(
            (margin + 70, highlight_icon_y + 54),
            f"🛠️ Tool of the Day: {totd.headline} ({totd.source_name})",
            fill=COLOR_TEXT_MUTED,
            font=font_highlight,
        )

    # 6. Bottom Status & Call-To-Action Bar
    footer_y = CARD_HEIGHT - margin - 50
    draw.line([(margin + 45, footer_y - 15), (CARD_WIDTH - margin - 45, footer_y - 15)], fill=COLOR_BORDER, width=1)

    draw.text((margin + 45, footer_y), "🌐 creavora.my.id", fill=COLOR_TEXT_WHITE, font=font_footer)
    draw.text((margin + 240, footer_y), "•", fill=COLOR_BORDER, font=font_footer)
    draw.text((margin + 270, footer_y), "📱 t.me/CreavoraAI", fill=COLOR_PRIMARY, font=font_footer)
    draw.text((margin + 480, footer_y), "•", fill=COLOR_BORDER, font=font_footer)
    draw.text((margin + 510, footer_y), "⚡ 3-Min Synthesis for Builders", fill=COLOR_TEXT_MUTED, font=font_highlight)

    # Save outputs
    out_file = Path(output_path) if output_path else Path("output") / "today_social_card.png"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_file, format="PNG", optimize=True)
    logger.info(f"Generated dynamic social card banner at {out_file.resolve()}")

    # Also save to docs/today_social_card.png so it is served live via creavora.my.id
    docs_file = Path(public_docs_path) if public_docs_path else Path("docs") / "today_social_card.png"
    try:
        docs_file.parent.mkdir(parents=True, exist_ok=True)
        img.save(docs_file, format="PNG", optimize=True)
        logger.info(f"Published live social card banner to {docs_file.resolve()}")
    except Exception as e:
        logger.warning(f"Could not write to docs/today_social_card.png: {e}")

    return out_file
