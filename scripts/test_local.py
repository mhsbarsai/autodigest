from __future__ import annotations
import argparse
import logging
import webbrowser
from pathlib import Path
import sys

# Ensure src is in python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.main import run_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Test AutoDigest pipeline locally.")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True, help="Run without publishing remotely")
    parser.add_argument("--immediate", action=argparse.BooleanOptionalAction, default=True, help="Send email immediately without scheduling")
    parser.add_argument("--draft-only", action="store_true", help="Only create a draft (if publishing)")
    
    args = parser.parse_args()
    
    logger.info(f"Running pipeline (dry-run: {args.dry_run}, immediate: {args.immediate})")
    run = run_pipeline(dry_run=args.dry_run, immediate=args.immediate, use_local_cache=True)
    
    logger.info("Pipeline Summary:")
    logger.info(f"Status: {run.status}")
    logger.info(f"Articles Fetched: {run.articles_fetched}")
    logger.info(f"Articles Deduplicated: {run.articles_after_dedup}")
    logger.info(f"Articles Scored: {run.articles_scored}")
    logger.info(f"Articles in Digest: {run.articles_in_digest}")

    if run.status == "error":
        logger.error(f"Error Message: {run.error}")
        
    if args.dry_run and run.status == 'completed':
        preview_path = project_root / 'output' / 'latest_preview.html'
        if preview_path.exists():
            logger.info(f"Opening preview in browser: {preview_path}")
            webbrowser.open(preview_path.as_uri())

if __name__ == "__main__":
    main()
