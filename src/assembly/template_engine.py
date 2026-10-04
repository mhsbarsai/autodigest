from __future__ import annotations
import datetime
import logging
from pathlib import Path
import jinja2

from src.models.schemas import NewsletterDigest

logger = logging.getLogger(__name__)

def render_newsletter(digest: NewsletterDigest, newsletter_name: str = 'AutoDigest', edition_number: int = 1) -> str:
    """Render the newsletter digest into HTML using a Jinja2 template."""
    project_root = Path(__file__).resolve().parent.parent.parent
    template_dir = project_root / 'templates'
    
    try:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)), autoescape=True)
        template = env.get_template('newsletter.html.j2')
        
        current_date = datetime.date.today().strftime("%B %d, %Y")
        
        html = template.render(
            digest=digest,
            newsletter_name=newsletter_name,
            edition_number=edition_number,
            current_date=current_date
        )
        return html
    except Exception as e:
        logger.error(f"Failed to render newsletter template: {e}")
        raise
