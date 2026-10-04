"""AutoDigest — Daily Automated Newsletter Runner.

Executes the pipeline and dispatches the newsletter live via the configured provider (Resend/Beehiiv).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

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
    logger.info("Starting AutoDigest daily dispatch...")
    run = run_pipeline(dry_run=False, immediate=True, use_local_cache=True)

    logger.info("=" * 50)
    logger.info("AutoDigest Execution Summary:")
    logger.info(f"Status: {run.status}")
    logger.info(f"Articles Fetched: {run.articles_fetched}")
    logger.info(f"Articles After Deduplication: {run.articles_after_dedup}")
    logger.info(f"Articles Scored: {run.articles_scored}")
    logger.info(f"Articles in Digest: {run.articles_in_digest}")
    logger.info(f"Post / Delivery ID: {run.beehiiv_post_id}")
    logger.info("=" * 50)

    if run.status != "completed":
        logger.error(f"Pipeline failed: {run.error}")
        sys.exit(1)

    logger.info("AutoDigest completed successfully!")


if __name__ == "__main__":
    main()
