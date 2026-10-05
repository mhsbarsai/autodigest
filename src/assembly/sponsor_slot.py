"""NeuralBrief / AutoDigest — Sponsor Slot Injector.

Injects paid sponsor placements or sponsorship inquiry callouts into the newsletter.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def load_active_sponsor() -> Optional[dict]:
    """Load active sponsor configuration from data/sponsor.json if present."""
    project_root = Path(__file__).resolve().parent.parent.parent
    sponsor_file = project_root / "data" / "sponsor.json"

    if sponsor_file.exists():
        try:
            with open(sponsor_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("active", False):
                    return data
        except Exception as e:
            logger.warning(f"Could not load sponsor file {sponsor_file}: {e}")

    return None


def inject_sponsor(
    html: str,
    sponsor_name: str | None = None,
    sponsor_text: str | None = None,
    sponsor_url: str | None = None,
    sponsor_cta: str | None = "Learn More",
) -> str:
    """Replace the {{SPONSOR_SLOT}} placeholder with active sponsor or inquiry CTA."""
    placeholder = "{{SPONSOR_SLOT}}"

    # 1. Check passed arguments first
    if sponsor_name and sponsor_text and sponsor_url:
        active = {
            "name": sponsor_name,
            "text": sponsor_text,
            "url": sponsor_url,
            "cta": sponsor_cta or "Learn More",
        }
    else:
        # 2. Check data/sponsor.json
        active = load_active_sponsor()

    if active:
        name = active.get("name", "Sponsor")
        text = active.get("text", "")
        url = active.get("url", "#")
        cta = active.get("cta", "Learn More &rarr;")

        sponsor_html = f"""
        <div style="background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; text-align: left; margin: 28px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 11px; font-weight: 800; color: #6366f1; text-transform: uppercase; letter-spacing: 0.8px;">⚡ FEATURED PARTNER</span>
                <span style="font-size: 11px; color: #94a3b8; font-weight: 600;">SPONSORED</span>
            </div>
            <h4 style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 6px 0;">{name}</h4>
            <p style="font-size: 14px; color: #334155; line-height: 1.55; margin: 0 0 14px 0;">{text}</p>
            <a href="{url}" target="_blank" rel="noopener noreferrer" style="background-color: #6366f1; color: #ffffff; padding: 8px 16px; font-size: 13px; font-weight: 600; text-decoration: none; border-radius: 6px; display: inline-block;">{cta}</a>
        </div>
        """
        return html.replace(placeholder, sponsor_html)

    # 3. Default high-converting sponsorship CTA
    inquiry_html = """
    <div style="background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 18px 20px; text-align: center; margin: 28px 0;">
        <span style="font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px; display: block; margin-bottom: 4px;">Partner With Creavora</span>
        <p style="font-size: 13px; color: #475569; margin: 0 0 10px 0; line-height: 1.5;">Reach 1,000+ engineers, researchers, and technical founders every morning.</p>
        <a href="mailto:mahsabar98@gmail.com?subject=Sponsorship%20Inquiry%20-%20Creavora" style="color: #6366f1; font-weight: 700; font-size: 13px; text-decoration: none;">Reserve a sponsor slot in tomorrow's edition &rarr;</a>
    </div>
    """
    return html.replace(placeholder, inquiry_html)
