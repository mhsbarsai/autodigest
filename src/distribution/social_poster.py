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
    """Format high-converting, human-sounding copy tailored for each tech platform.

    Inspired by top-tier developer content engineering frameworks:
    - Scroll-stopping single-line hook
    - Whitespace & rhythm optimized for mobile readability
    - Hard engineering signal (latency, VRAM, architecture tradeoffs)
    - Actionable takeaways over marketing hype
    - High-conversion dual-CTA (Website + Telegram Channel)
    """
    articles = digest.articles[:3]
    top_article = articles[0] if articles else None

    # =========================================================================
    # 1. X / Twitter & Bluesky 4-Part Viral Thread
    # =========================================================================
    t1_hook = (
        f"🚨 {digest.subject_line}\n\n"
        f"90% of AI announcements this week were marketing fluff.\n"
        f"Here are the actual engineering breakthroughs you need before your first commit:\n\n"
        f"🧵 1/4 👇"
    )

    t2_bullets = []
    for idx, a in enumerate(articles[:2], 1):
        bullets = " • ".join(a.key_takeaways[:2]) if a.key_takeaways else a.summary[:110]
        t2_bullets.append(f"{a.emoji} {a.headline}\n{bullets}")

    t2_body = "\n\n".join(t2_bullets)
    if len(t2_body) > 280:
        t2_body = t2_body[:275] + "..."
    t2_body = f"2/4 Key Shifts:\n\n{t2_body}"

    tool_text = ""
    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        tool_text = (
            f"3/4 🛠️ Tool of the Day: {totd.headline}\n\n"
            f"{totd.summary[:140]}...\n\n"
            f"Repo: {totd.source_url}"
        )
    else:
        tool_text = "3/4 ⚡ Architecture Signal:\n\nReview full latency & memory trade-offs across today's featured models at creavora.my.id."

    t4_cta = (
        f"4/4 High signal. Zero PR hype.\n\n"
        f"Delivered daily before 06:00 WIB:\n"
        f"👉 Free Web Briefing: {landing_url}\n"
        f"👉 Instant Telegram: https://t.me/CreavoraAI\n\n"
        f"Bookmark to save for later 🔖"
    )

    x_thread = [t1_hook, t2_body, tool_text, t4_cta]

    # =========================================================================
    # 2. LinkedIn High-Engagement Storytelling Post
    # =========================================================================
    linkedin_parts = [
        f"Most AI news on the internet is just PR noise.",
        "",
        f"Here is the actual engineering signal from today's frontier models & arXiv drops:",
        "",
        f"⚡ {digest.subject_line}",
        "",
        "---",
        "",
    ]

    for idx, a in enumerate(articles, 1):
        linkedin_parts.append(f"📌 {idx}. {a.headline} ({a.source_name})")
        linkedin_parts.append(f"{a.summary}")
        if a.key_takeaways:
            for t in a.key_takeaways[:2]:
                linkedin_parts.append(f"   ▸ {t}")
        linkedin_parts.append("")

    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        linkedin_parts.append(f"🛠️ Open-Source Tool of the Day:")
        linkedin_parts.append(f"• {totd.headline}")
        linkedin_parts.append(f"• {totd.summary}")
        linkedin_parts.append(f"• Code: {totd.source_url}")
        linkedin_parts.append("")

    linkedin_parts.extend([
        "---",
        "",
        "💡 The takeaway for builders:",
        "Don't optimize for model benchmarks alone; optimize for inference throughput, memory bandwidth, and deterministic guardrails.",
        "",
        f"We synthesize these breakdowns every morning at 06:00 WIB into a 3-minute read.",
        f"👉 Read today's full issue & code snippet: {landing_url}",
        f"👉 Join our Telegram channel: https://t.me/CreavoraAI",
        "",
        "#ArtificialIntelligence #MachineLearning #SoftwareEngineering #OpenSource #DevOps #LLM",
    ])
    linkedin_post = "\n".join(linkedin_parts)

    # =========================================================================
    # 3. Reddit / Tech Community Discussion Post (r/LocalLLaMA, r/MachineLearning)
    # =========================================================================
    reddit_parts = [
        f"# [Daily Briefing] {digest.subject_line}",
        "",
        f"*Dispatched at 06:00 WIB | 3-minute technical synthesis for builders & researchers*",
        "",
        "## Key Architecture & Research Movements Today",
        "",
    ]
    for a in articles:
        reddit_parts.append(f"### {a.emoji} {a.headline}")
        reddit_parts.append(f"{a.summary}\n")
        if a.key_takeaways:
            reddit_parts.append("**Core Technical Takeaways:**")
            for t in a.key_takeaways:
                reddit_parts.append(f"- {t}")
            reddit_parts.append("")
        reddit_parts.append(f"**Source:** [{a.source_name}]({a.source_url})\n")

    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        reddit_parts.append(f"## 🛠️ Tool of the Day: [{totd.headline}]({totd.source_url})")
        reddit_parts.append(f"{totd.summary}\n")

    reddit_parts.append(f"---\n*Full web archive and interactive reproduction snippets available at [{landing_url}]({landing_url}) or join our discussion on [Telegram](https://t.me/CreavoraAI).*")
    reddit_post = "\n".join(reddit_parts)

    # =========================================================================
    # 4. Telegram Channel Message (Clean Typographic Rhythm)
    # =========================================================================
    tg_lines = [
        f"⚡ *Creavora Daily Briefing*",
        f"*{digest.subject_line}*",
        "",
    ]
    for a in articles:
        tg_lines.append(f"{a.emoji} *{a.headline}*")
        tg_lines.append(f"{a.summary}")
        tg_lines.append(f"👉 [Read full source]({a.source_url})\n")

    if digest.tool_of_the_day:
        totd = digest.tool_of_the_day
        tg_lines.append(f"🛠️ *Tool of the Day:* [{totd.headline}]({totd.source_url})")
        tg_lines.append(f"{totd.summary}\n")

    tg_lines.append(f"🌐 [Read Web Version & Archive]({landing_url})")
    telegram_message = "\n".join(tg_lines)

    # =========================================================================
    # 5. Discord Webhook Payload
    # =========================================================================
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
                "description": f"{digest.greeting}\n\n[**Read Web Version & Subscribe**]({landing_url}) • [**Telegram Channel**](https://t.me/CreavoraAI)",
                "color": 6514417,  # Indigo #6366f1
                "fields": discord_fields,
                "footer": {"text": "Creavora — Daily 3-minute technical AI intelligence"},
            }
        ],
    }

    return {
        "x_thread": x_thread,
        "linkedin_post": linkedin_post,
        "reddit_post": reddit_post,
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


def dispatch_twitter(
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
    tweets: list[str],
) -> list[str]:
    """Publish a multi-part thread to X / Twitter via Twitter API v2.

    Returns list of created tweet IDs.
    """
    if not api_key or not api_secret or not access_token or not access_token_secret or not tweets:
        return []

    try:
        from requests_oauthlib import OAuth1

        auth = OAuth1(
            client_key=api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        tweet_ids: list[str] = []
        last_id: str | None = None

        for tweet_text in tweets:
            payload: dict[str, Any] = {"text": tweet_text}
            if last_id:
                payload["reply"] = {"in_reply_to_tweet_id": last_id}

            resp = requests.post(
                "https://api.twitter.com/2/tweets",
                auth=auth,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            if resp.status_code in (200, 201):
                data = resp.json().get("data", {})
                last_id = data.get("id")
                if last_id:
                    tweet_ids.append(last_id)
            else:
                logger.warning(f"Failed to post tweet to X/Twitter: {resp.status_code} - {resp.text}")
                break

        if tweet_ids:
            logger.info(f"Successfully published {len(tweet_ids)}-part thread to X/Twitter! (Root Tweet ID: {tweet_ids[0]})")
        return tweet_ids
    except Exception as e:
        logger.warning(f"Error publishing to X/Twitter: {e}")
        return []


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

        # 5. Automatic push to X / Twitter Thread (if TWITTER_* credentials are set)
        tw_key = os.getenv("TWITTER_API_KEY", "").strip()
        tw_secret = os.getenv("TWITTER_API_SECRET", "").strip()
        tw_token = os.getenv("TWITTER_ACCESS_TOKEN", "").strip()
        tw_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "").strip()
        if tw_key and tw_secret and tw_token and tw_token_secret:
            dispatch_twitter(tw_key, tw_secret, tw_token, tw_token_secret, teasers["x_thread"])

        # 6. Automatic push to Bluesky Thread (100% Free & Open AI Community)
        bsky_handle = os.getenv("BLUESKY_HANDLE", "").strip()
        bsky_pw = os.getenv("BLUESKY_APP_PASSWORD", "").strip()
        if bsky_handle and bsky_pw:
            try:
                from src.distribution.bluesky_poster import dispatch_bluesky_thread
                dispatch_bluesky_thread(bsky_handle, bsky_pw, teasers["x_thread"])
            except Exception as e:
                logger.warning(f"Failed to post to Bluesky: {e}")
    else:
        logger.info("Dry-run mode: skipped Discord/Telegram/Twitter/Bluesky broadcast.")

    return teasers
