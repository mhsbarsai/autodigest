"""NeuralBrief / AutoDigest — Daily Automated Newsletter Runner.

Executes the pipeline and dispatches the newsletter live via the configured provider (Resend/Beehiiv).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
import sys

# Ensure src is in python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.main import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("=" * 60)
    logger.info("STARTING CREAVORA DAILY AUTOMATION RUN")
    logger.info("=" * 60)

    # Pre-flight environment check
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    resend_key = os.getenv("RESEND_API_KEY", "").strip()
    to_email = os.getenv("RESEND_TO_EMAIL", "").strip()

    logger.info("PRE-FLIGHT SECRETS CHECK:")
    logger.info(f"  • GEMINI_API_KEY  : {'[OK] (Configured, ' + str(len(gemini_key)) + ' chars)' if gemini_key else '[CRITICAL: MISSING OR EMPTY]'}")
    logger.info(f"  • RESEND_API_KEY  : {'[OK] (Configured, ' + str(len(resend_key)) + ' chars)' if resend_key else '[CRITICAL: MISSING OR EMPTY]'}")
    logger.info(f"  • RESEND_TO_EMAIL : {'[OK] (' + to_email + ')' if to_email else '[NOT SET - will fallback to mahsabar99@gmail.com]'}")
    logger.info("=" * 60)

    if not gemini_key:
        logger.error(
            "CRITICAL CONFIGURATION ERROR: GEMINI_API_KEY is not set or empty in GitHub Secrets!\n"
            "Solution: Go to your repo -> Settings -> Secrets and variables -> Actions -> Repository secrets.\n"
            "Click 'New repository secret', Name: 'GEMINI_API_KEY', Value: your Gemini API key."
        )
        sys.exit(1)

    if not resend_key:
        logger.error(
            "CRITICAL CONFIGURATION ERROR: RESEND_API_KEY is not set or empty in GitHub Secrets!\n"
            "Solution: Go to your repo -> Settings -> Secrets and variables -> Actions -> Repository secrets.\n"
            "Click 'New repository secret', Name: 'RESEND_API_KEY', Value: your Resend API key (re_...)."
        )
        sys.exit(1)

    run = run_pipeline(dry_run=False, immediate=True, use_local_cache=True)

    logger.info("=" * 60)
    logger.info("AutoDigest Execution Summary:")
    logger.info(f"Status: {run.status}")
    logger.info(f"Articles Fetched: {run.articles_fetched}")
    logger.info(f"Articles After Deduplication: {run.articles_after_dedup}")
    logger.info(f"Articles Scored: {run.articles_scored}")
    logger.info(f"Articles in Digest: {run.articles_in_digest}")
    logger.info(f"Post / Delivery ID: {run.beehiiv_post_id}")
    logger.info("=" * 60)

    if run.status != "completed":
        logger.error(f"Pipeline failed: {run.error}")
        sys.exit(1)

    logger.info("Creavora daily briefing completed successfully!")


if __name__ == "__main__":
    main()
