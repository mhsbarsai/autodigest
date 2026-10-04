from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

def inject_sponsor(html: str, sponsor_name: str | None = None, sponsor_text: str | None = None, sponsor_url: str | None = None) -> str:
    """Replace the {{SPONSOR_SLOT}} placeholder with sponsor content."""
    placeholder = "{{SPONSOR_SLOT}}"
    
    if sponsor_name and sponsor_text and sponsor_url:
        sponsor_html = f'''
        <div style="background-color: #f3f4f6; padding: 20px; text-align: center; margin: 20px 0;">
            <p style="font-size: 12px; color: #6b7280; text-transform: uppercase; margin-bottom: 5px;">Sponsored by {sponsor_name}</p>
            <p style="font-size: 16px; margin-bottom: 15px;">{sponsor_text}</p>
            <a href="{sponsor_url}" style="background-color: #2563eb; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Learn More</a>
        </div>
        '''
        return html.replace(placeholder, sponsor_html)
    else:
        return html.replace(placeholder, "")
