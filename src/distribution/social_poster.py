"""NeuralBrief / AutoDigest — Automated Social Distribution & Teaser Engine.

Generates high-converting social snippets and dispatches them across:
- X / Twitter Threads
- LinkedIn / Reddit / Technical Community Briefings
- Discord Webhooks (Developer & AI communities)
- Telegram Channels
- GitHub Actions Job Summary ($GITHUB_STEP_SUMMARY)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any
import requests

from src.models.schemas import NewsletterDigest

logger = logging.getLogger(__name__)

DEFAULT_LANDING_URL = "https://creavora.my.id/"


def generate_social_teasers(
    digest: NewsletterDigest,
    landing_url: str = DEFAULT_LANDING_URL,
) -> dict[str, Any]:
    """Format social copy tailored for each developer/tech platform."""
    articles = digest.articles[:3]

    # --- 1. X / Twitter 3-Part Thread ---
    t1_hook = f"🚨 {digest.subject_line}\n\nToday's top movements in frontier AI models, agent architectures & developer tools:\n\n🧵 👇"

    t2_bullets = []
    for a in articles:
        bullets = " • ".join(a.key_takeaways[:2]) if a.key_takeaways else a.summary[:100]
        t2_bullets.append(f"{a.emoji} {a.headline}\n{bullets}")

    t2_body = "\n\n".join(t2_bullets)

    tool_text = ""
    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        tool_text = f"\n\n🛠️ Tool of the Day: {totd.headline}\n{totd.summary[:120]}..."

    t3_cta = (
        f"Get the full 3-minute morning briefing in your inbox before 6:00 AM.\n\n"
        f"100% Free. High signal, zero fluff:\n"
        f"👉 {landing_url}"
    )

    x_thread = [t1_hook, t2_body + tool_text, t3_cta]

    # --- 2. LinkedIn / Reddit / Tech Forum Post ---
    linkedin_parts = [
        f"🧠 {digest.subject_line}",
        "",
        digest.greeting,
        "",
        "Here are today's critical developments across frontier AI:",
        "",
    ]
    for idx, a in enumerate(articles, 1):
        linkedin_parts.append(f"{idx}. {a.emoji} {a.headline} ({a.source_name})")
        linkedin_parts.append(f"   {a.summary}")
        if a.key_takeaways:
            for t in a.key_takeaways[:2]:
                linkedin_parts.append(f"   • {t}")
        linkedin_parts.append("")

    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        linkedin_parts.append(f"🛠️ Tool of the Day: {totd.headline}")
        linkedin_parts.append(f"{totd.summary}")
        linkedin_parts.append(f"Link: {totd.source_url}")
        linkedin_parts.append("")

    linkedin_parts.append(f"📩 Subscribe for tomorrow's 3-minute brief: {landing_url}")
    linkedin_post = "\n".join(linkedin_parts)

    # --- 3. Telegram Message (Markdown format) ---
    tg_lines = [
        f"⚡ *Creavora Daily Briefing*",
        f"*{digest.subject_line}*",
        "",
    ]
    for a in articles:
        tg_lines.append(f"{a.emoji} *{a.headline}*")
        tg_lines.append(f"{a.summary}")
        tg_lines.append(f"[Read full source]({a.source_url})\n")

    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        tg_lines.append(f"🛠️ *Tool of the Day:* [{totd.headline}]({totd.source_url})\n")

    tg_lines.append(f"👉 [Read & Subscribe Free]({landing_url})")
    telegram_message = "\n".join(tg_lines)

    # --- 4. Discord Webhook Payload ---
    discord_fields = []
    for a in articles:
        discord_fields.append({
            "name": f"{a.emoji} {a.headline} ({a.source_name})",
            "value": f"{a.summary}\n[Original Source]({a.source_url})",
            "inline": False,
        })

    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        discord_fields.append({
            "name": f"🛠️ Tool of the Day: {totd.headline}",
            "value": f"{totd.summary}\n[Explore Tool]({totd.source_url})",
            "inline": False,
        })

    discord_payload = {
        "username": "Creavora Bot",
        "avatar_url": "https://raw.githubusercontent.com/mhsbarsai/autodigest/main/docs/avatar.png",
        "embeds": [
            {
                "title": f"⚡ {digest.subject_line}",
                "description": f"{digest.greeting}\n\n[**Read Web Version & Subscribe**]({landing_url})",
                "color": 6514417,  # Indigo #6366f1
                "fields": discord_fields,
                "footer": {"text": "Creavora — Daily 3-minute technical AI briefing"},
            }
        ],
    }

    return {
        "x_thread": x_thread,
        "linkedin_post": linkedin_post,
        "telegram_message": telegram_message,
        "discord_payload": discord_payload,
    }


def dispatch_discord(webhook_url: str, payload: dict) -> bool:
    """Send automated announcement to a Discord server webhook."""
    if not webhook_url:
        return False
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Successfully pushed briefing to Discord webhook.")
        return True
    except Exception as e:
        logger.warning(f"Failed to post to Discord webhook: {e}")
        return False


def dispatch_telegram(bot_token: str, chat_id: str, message: str) -> bool:
    """Send automated briefing to a Telegram channel or group."""
    if not bot_token or not chat_id:
        return False
    try:
        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(
            api_url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": False},
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Successfully pushed briefing to Telegram.")
        return True
    except Exception as e:
        logger.warning(f"Failed to post to Telegram: {e}")
        return False


def distribute_social(
    digest: NewsletterDigest,
    landing_url: str = DEFAULT_LANDING_URL,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Generate all social teasers, save to local output, and broadcast to enabled channels."""
    teasers = generate_social_teasers(digest, landing_url=landing_url)

    # 1. Save teasers locally to output/today_social_teasers.md
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    social_file = output_dir / "today_social_teasers.md"

    x_formatted = "\n\n---\n\n".join([f"**Tweet {i+1}:**\n{t}" for i, t in enumerate(teasers["x_thread"])])

    markdown_content = f"""# Creavora — Today's Social Teasers & Teaser Copy

## 🐦 X / Twitter Thread (Ready to Copy & Post)
{x_formatted}

---

## 💼 LinkedIn / Reddit / Community Post
{teasers['linkedin_post']}

---

## 📱 Telegram Channel Post
```markdown
{teasers['telegram_message']}
```
"""

    with open(social_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    logger.info(f"Saved ready-to-use social teasers to {social_file.resolve()}")

    # 2. Append to GitHub Actions Step Summary if running in CI
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path and Path(summary_path).exists():
        try:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write(f"\n\n## 📢 Today's Creavora Social Teasers\n\n{markdown_content}\n")
            logger.info("Appended social teasers to GITHUB_STEP_SUMMARY.")
        except Exception as e:
            logger.warning(f"Could not write to GITHUB_STEP_SUMMARY: {e}")

    # 3. Automatic push to Discord (if DISCORD_WEBHOOK_URL is set and not dry_run)
    if not dry_run:
        discord_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        if discord_url:
            dispatch_discord(discord_url, teasers["discord_payload"])

        # 4. Automatic push to Telegram (if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set)
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        tg_chat = os.getenv("TELEGRAM_CHAT_ID", "")
        if tg_token and tg_chat:
            dispatch_telegram(tg_token, tg_chat, teasers["telegram_message"])
    else:
        logger.info("Dry-run mode: skipped Discord/Telegram broadcast.")

    return teasers
