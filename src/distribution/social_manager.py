"""Creavora Autonomous Social Media Manager & Orchestration Engine.

Acts as an autonomous social media executive:
1. Generates multi-channel copy & viral hooks (X, Bluesky, LinkedIn, Reddit, Telegram, Discord).
2. Generates dynamic 1200x630 dark editorial social card preview image via Pillow.
3. Dispatches directly to Telegram Channel (@CreavoraAI) with photo and pinned status.
4. Dispatches multi-part thread to Bluesky (AT Protocol).
5. Dispatches rich embed to Discord webhook.
6. Dispatches to Make.com / n8n / Zapier webhook bridge for free X & LinkedIn posting.
7. Dispatches native X/Twitter threads (if API keys are funded).
8. Tracks persistent content history in data/social_history.json.
9. Writes output artifacts (today_social_teasers.md & $GITHUB_STEP_SUMMARY).
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from typing import Any, Optional
import requests

from src.models.schemas import NewsletterDigest
from src.distribution.social_poster import (
    generate_social_teasers,
    dispatch_discord,
    dispatch_telegram,
    dispatch_twitter,
    DEFAULT_LANDING_URL,
)
from src.distribution.card_generator import generate_social_card

logger = logging.getLogger(__name__)

HISTORY_FILE = Path("data") / "social_history.json"


def record_social_history(
    digest: NewsletterDigest,
    dispatched_channels: list[str],
    card_path: Optional[str] = None,
) -> None:
    """Record today's social publication history into persistent JSON storage."""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        history: list[dict[str, Any]] = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load existing social history, resetting: {e}")
                history = []

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subject_line": digest.subject_line,
            "articles": [a.headline for a in digest.articles],
            "tool_of_the_day": digest.tool_of_the_day.headline if digest.tool_of_the_day else None,
            "dispatched_channels": dispatched_channels,
            "card_image": card_path,
        }

        # Keep rolling last 90 entries
        history.append(entry)
        if len(history) > 90:
            history = history[-90:]

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"Recorded social publication to {HISTORY_FILE.resolve()}")
    except Exception as e:
        logger.warning(f"Failed to record social history: {e}")


def dispatch_telegram_with_card(
    bot_token: str,
    chat_id: str,
    message: str,
    card_path: Optional[Path | str] = None,
) -> bool:
    """Send photo banner followed by formatted text, and pin the latest edition."""
    if not bot_token or not chat_id:
        return False

    success = False
    message_id_to_pin: Optional[int] = None

    # 1. Send Photo Banner if exists
    if card_path and Path(card_path).exists():
        try:
            photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            with open(card_path, "rb") as photo_file:
                resp = requests.post(
                    photo_url,
                    data={"chat_id": chat_id, "caption": "⚡ *Creavora Daily Intelligence Banner*", "parse_mode": "Markdown"},
                    files={"photo": photo_file},
                    timeout=15,
                )
            if resp.status_code == 200:
                logger.info("Successfully pushed social card image to Telegram.")
            else:
                logger.warning(f"Failed to send photo to Telegram ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.warning(f"Error sending photo to Telegram: {e}")

    # 2. Send Main Briefing Message
    try:
        msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(
            msg_url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": False},
            timeout=12,
        )
        if resp.status_code == 200:
            data = resp.json().get("result", {})
            message_id_to_pin = data.get("message_id")
            success = True
            logger.info("Successfully published briefing text to Telegram.")
        else:
            logger.warning(f"Failed to send briefing to Telegram ({resp.status_code}): {resp.text}")
    except Exception as e:
        logger.warning(f"Error sending briefing text to Telegram: {e}")

    # 3. Pin Message in Channel / Group
    if message_id_to_pin:
        try:
            pin_url = f"https://api.telegram.org/bot{bot_token}/pinChatMessage"
            pin_resp = requests.post(
                pin_url,
                json={"chat_id": chat_id, "message_id": message_id_to_pin, "disable_notification": True},
                timeout=8,
            )
            if pin_resp.status_code == 200:
                logger.info(f"Pinned message #{message_id_to_pin} in Telegram channel {chat_id}.")
        except Exception as e:
            logger.debug(f"Could not pin message (may lack pin permissions): {e}")

    return success


def dispatch_webhook_bridge(
    webhook_url: str,
    payload: dict[str, Any],
) -> bool:
    """Send complete social briefing payload to Make.com / n8n / Zapier webhook bridge."""
    if not webhook_url:
        return False
    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code in (200, 201, 202, 204):
            logger.info("Successfully triggered multi-platform Webhook Bridge (Make/n8n)!")
            return True
        else:
            logger.warning(f"Webhook Bridge returned status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        logger.warning(f"Error triggering Webhook Bridge: {e}")
        return False


def run_autonomous_social_manager(
    digest: NewsletterDigest,
    landing_url: str = DEFAULT_LANDING_URL,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Execute end-to-end social media pipeline: generate assets, copy, dispatch, and track."""
    logger.info("=" * 60)
    logger.info("RUNNING CREAVORA AUTONOMOUS SOCIAL MANAGER")
    logger.info("=" * 60)

    # 1. Generate multi-platform teasers & copy
    teasers = generate_social_teasers(digest, landing_url=landing_url)

    # 2. Generate dynamic 1200x630 dark editorial social card banner
    card_path: Optional[Path] = None
    try:
        card_path = generate_social_card(digest)
    except Exception as e:
        logger.warning(f"Failed to generate social card banner: {e}")

    # 3. Save local teasers to output/today_social_teasers.md
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    social_file = output_dir / "today_social_teasers.md"

    x_formatted = "\n\n---\n\n".join([f"**Tweet {i+1}:**\n{t}" for i, t in enumerate(teasers["x_thread"])])

    markdown_content = f"""# Creavora — Today's Social Teasers & Teaser Copy

## 🎨 Daily Social Banner
- Path: `output/today_social_card.png`
- Live URL: `https://creavora.my.id/today_social_card.png`

---

## 🐦 X / Twitter & Bluesky Thread (Ready to Copy & Post)
{x_formatted}

---

## 💼 LinkedIn Post (High-Retention & Spacing Format)
{teasers['linkedin_post']}

---

## 🤖 Reddit / Developer Community Post (r/MachineLearning, r/LocalLLaMA, HN)
{teasers['reddit_post']}

---

## 📱 Telegram Channel Post
```markdown
{teasers['telegram_message']}
```
"""

    with open(social_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    logger.info(f"Saved ready-to-use social teasers to {social_file.resolve()}")

    # 4. Append to GitHub Actions Step Summary if running in CI
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path and Path(summary_path).exists():
        try:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write(f"\n\n## 📢 Today's Creavora Social Distribution Suite\n\n{markdown_content}\n")
            logger.info("Appended social distribution suite to GITHUB_STEP_SUMMARY.")
        except Exception as e:
            logger.warning(f"Could not write to GITHUB_STEP_SUMMARY: {e}")

    dispatched_channels: list[str] = []

    # 5. Autonomous Multi-Channel Dispatch (if not dry_run)
    if not dry_run:
        # A. Discord Webhook
        discord_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
        if discord_url:
            if dispatch_discord(discord_url, teasers["discord_payload"]):
                dispatched_channels.append("discord")

        # B. Telegram Channel with Social Card & Pinning
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        tg_chat = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if tg_token and tg_chat:
            if dispatch_telegram_with_card(tg_token, tg_chat, teasers["telegram_message"], card_path):
                dispatched_channels.append("telegram")

        # C. Bluesky Thread via AT Protocol
        bsky_handle = os.getenv("BLUESKY_HANDLE", "").strip()
        bsky_pw = os.getenv("BLUESKY_APP_PASSWORD", "").strip()
        if bsky_handle and bsky_pw:
            try:
                from src.distribution.bluesky_poster import dispatch_bluesky_thread
                posts = dispatch_bluesky_thread(bsky_handle, bsky_pw, teasers["x_thread"])
                if posts:
                    dispatched_channels.append("bluesky")
            except Exception as e:
                logger.warning(f"Failed to post to Bluesky: {e}")

        # D. X / Twitter Direct API (if configured)
        tw_key = os.getenv("TWITTER_API_KEY", "").strip()
        tw_secret = os.getenv("TWITTER_API_SECRET", "").strip()
        tw_token = os.getenv("TWITTER_ACCESS_TOKEN", "").strip()
        tw_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "").strip()
        if tw_key and tw_secret and tw_token and tw_token_secret:
            try:
                tweet_ids = dispatch_twitter(tw_key, tw_secret, tw_token, tw_token_secret, teasers["x_thread"])
                if tweet_ids:
                    dispatched_channels.append("twitter")
            except Exception as e:
                logger.warning(f"Failed to post to X/Twitter: {e}")

        # E. Universal Webhook Bridge (Make.com / n8n / Zapier)
        bridge_url = os.getenv("SOCIAL_WEBHOOK_URL") or os.getenv("MAKE_WEBHOOK_URL") or os.getenv("N8N_WEBHOOK_URL", "").strip()
        if bridge_url:
            bridge_payload = {
                "brand": "Creavora",
                "subject_line": digest.subject_line,
                "landing_url": landing_url,
                "telegram_channel": "https://t.me/CreavoraAI",
                "card_image_url": f"{landing_url.rstrip('/')}/today_social_card.png",
                "x_thread": teasers["x_thread"],
                "linkedin_post": teasers["linkedin_post"],
                "reddit_post": teasers["reddit_post"],
                "telegram_message": teasers["telegram_message"],
                "tool_of_the_day": {
                    "headline": digest.tool_of_the_day.headline if digest.tool_of_the_day else None,
                    "source_url": digest.tool_of_the_day.source_url if digest.tool_of_the_day else None,
                },
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
            }
            if dispatch_webhook_bridge(bridge_url, bridge_payload):
                dispatched_channels.append("webhook_bridge")

        # 6. Record Persistent History
        record_social_history(
            digest,
            dispatched_channels=dispatched_channels,
            card_path=str(card_path) if card_path else None,
        )

    logger.info(f"Social Manager Run Completed. Dispatched to: {dispatched_channels if dispatched_channels else ['dry-run / saved locally']}")
    return {
        "teasers": teasers,
        "card_path": str(card_path) if card_path else None,
        "dispatched_channels": dispatched_channels,
    }
