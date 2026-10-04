"""AutoDigest — Main pipeline orchestrator and Cloud Function entrypoint."""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
import sys
import uuid

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ai.content_scorer import score_articles
from src.ai.gemini_client import GeminiClient
from src.ai.subject_generator import generate_subject_line
from src.ai.summarizer import summarize_articles
from src.assembly.affiliate_injector import inject_affiliate_links
from src.assembly.sponsor_slot import inject_sponsor
from src.assembly.template_engine import render_newsletter
from src.config import load_config
from src.distribution.beehiiv_client import BeehiivClient
from src.distribution.resend_client import ResendClient
from src.distribution.social_poster import distribute_social
from src.ingestion.article_extractor import enrich_articles
from src.ingestion.deduplicator import deduplicate, get_updated_seen_hashes
from src.ingestion.rss_fetcher import fetch_all_feeds
from src.models.schemas import PipelineRun
from src.storage.gcs_cache import create_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline(dry_run: bool = False, immediate: bool = False, use_local_cache: bool = False) -> PipelineRun:
    """Orchestrate the entire newsletter pipeline from ingestion to publishing."""
    run_id = str(uuid.uuid4())
    run = PipelineRun(
        run_id=run_id,
        started_at=datetime.datetime.now(datetime.timezone.utc),
        status="running",
    )

    try:
        logger.info(f"Starting pipeline run: {run_id} (dry_run: {dry_run})")
        config = load_config(dry_run=dry_run)

        gemini_client = GeminiClient(config.gemini)
        cache = create_cache(config.storage, use_local=(dry_run or use_local_cache))

        # 1. Ingestion: Fetch RSS Feeds
        feeds = fetch_all_feeds()
        run.articles_fetched = len(feeds)
        logger.info(f"Fetched {len(feeds)} articles across all feeds.")

        # 2. Deduplication
        seen_hashes = cache.load_seen_hashes()
        fresh_feeds = deduplicate(feeds, seen_hashes)
        run.articles_after_dedup = len(fresh_feeds)
        logger.info(f"Found {len(fresh_feeds)} fresh articles after deduplication.")

        if not fresh_feeds:
            logger.info("No new articles to process. Pipeline complete.")
            run.status = "completed"
            run.completed_at = datetime.datetime.now(datetime.timezone.utc)
            return run

        # 3. Extraction & Enrichment
        enriched = enrich_articles(fresh_feeds, max_articles=25)
        logger.info(f"Enriched {len(enriched)} fresh articles with full content.")
        new_articles = enriched

        if not new_articles:
            logger.info("No new articles to process. Pipeline complete.")
            run.status = "completed"
            run.completed_at = datetime.datetime.now(datetime.timezone.utc)
            return run

        # 4. AI Content Scoring
        scored = score_articles(
            articles=new_articles,
            client=gemini_client,
            top_k=config.newsletter.max_articles,
        )
        run.articles_scored = len(scored)
        logger.info(f"Scored articles. Selected top {len(scored)} candidates.")

        if len(scored) < config.newsletter.min_articles:
            msg = (
                f"Fewer than minimum required articles ({len(scored)} < "
                f"{config.newsletter.min_articles}). Aborting run."
            )
            logger.warning(msg)
            run.status = "aborted"
            run.error = msg
            run.completed_at = datetime.datetime.now(datetime.timezone.utc)
            return run

        # 5. AI Summarization & Synthesis
        digest = summarize_articles(scored_articles=scored, client=gemini_client)
        if not digest:
            raise RuntimeError("Gemini summarization failed to produce a valid digest.")

        run.articles_in_digest = len(digest.articles)

        # 6. Generate optimized Subject Line & Preview
        subject_line, preview_text = generate_subject_line(digest=digest, client=gemini_client)
        digest.subject_line = subject_line
        digest.preview_text = preview_text
        logger.info(f"Generated Subject Line: {subject_line}")

        # 7. Assemble Email HTML
        html_content = render_newsletter(digest, newsletter_name=config.newsletter.name)
        html_content = inject_sponsor(html_content)  # Empty slot for now
        html_content = inject_affiliate_links(html_content)

        # Always save local preview HTML
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        preview_file = output_dir / "latest_preview.html"
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Saved preview HTML to {preview_file.resolve()}")

        # Generate social copy & teasers (and distribute to Discord/Telegram if active)
        try:
            distribute_social(digest, dry_run=dry_run)
        except Exception as e:
            logger.warning(f"Social distribution encounter an error but non-fatal: {e}")

        # 8. Distribution / Output
        if not dry_run:
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            send_hour = config.newsletter.send_hour_utc
            scheduled_date = now_utc.date()
            if now_utc.hour >= send_hour:
                scheduled_date += datetime.timedelta(days=1)

            scheduled_time = (
                None
                if immediate
                else datetime.datetime.combine(
                    scheduled_date,
                    datetime.time(hour=send_hour),
                    tzinfo=datetime.timezone.utc,
                ).isoformat()
            )

            if config.distribution_provider == "resend":
                resend_client = ResendClient(config.resend)
                post = resend_client.publish_newsletter(
                    subject=subject_line,
                    html_content=html_content,
                    scheduled_at=scheduled_time,
                )
                run.beehiiv_post_id = post.post_id
                logger.info(f"Newsletter dispatched via Resend (ID: {post.post_id})")
            else:
                beehiiv_client = BeehiivClient(config.beehiiv)
                post = beehiiv_client.create_post(
                    title=subject_line,
                    subtitle=preview_text[:100],
                    html_content=html_content,
                    scheduled_at=scheduled_time,
                )
                run.beehiiv_post_id = post.post_id
                logger.info(f"Post scheduled on Beehiiv (Post ID: {post.post_id})")

        # 9. Update Cache with seen articles
        updated_hashes = get_updated_seen_hashes(seen_hashes, new_articles)
        cache.save_seen_hashes(updated_hashes)

        run.status = "completed"

    except Exception as e:
        logger.exception("Pipeline execution failed.")
        run.status = "error"
        run.error = str(e)

    run.completed_at = datetime.datetime.now(datetime.timezone.utc)
    logger.info(f"Pipeline finished with status: {run.status}")
    return run


def newsletter_handler(request) -> tuple[str, int, dict]:
    """Cloud Function HTTP handler for Cloud Scheduler or manual trigger."""
    run = run_pipeline(dry_run=False)
    status_code = 200 if run.status == "completed" else 500
    headers = {"Content-Type": "application/json"}
    return json.dumps(run.model_dump(mode="json")), status_code, headers


if __name__ == "__main__":
    run_pipeline(dry_run=True)
