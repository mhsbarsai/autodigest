"""Creavora — Automated Bluesky (AT Protocol) Thread Dispatcher.

Publishes multi-part threads to Bluesky without fees or rate limit paywalls.
Bluesky is widely used across the AI engineering, arXiv, and open-source communities.
"""
from __future__ import annotations

import datetime
import logging
from typing import Any
import requests

logger = logging.getLogger(__name__)

BSKY_API_BASE = "https://bsky.social/xrpc"


def create_bluesky_session(handle: str, app_password: str) -> dict[str, str] | None:
    """Authenticate with Bluesky server via AT Protocol createSession."""
    if not handle or not app_password:
        return None

    clean_handle = handle.strip().lstrip("@")
    clean_password = app_password.strip()

    try:
        url = f"{BSKY_API_BASE}/com.atproto.server.createSession"
        resp = requests.post(
            url,
            json={"identifier": clean_handle, "password": clean_password},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "accessJwt": data.get("accessJwt", ""),
                "did": data.get("did", ""),
                "handle": data.get("handle", clean_handle),
            }
        else:
            logger.warning(f"Bluesky session creation failed ({resp.status_code}): {resp.text}")
            return None
    except Exception as e:
        logger.warning(f"Bluesky connection error: {e}")
        return None


def dispatch_bluesky_thread(
    handle: str,
    app_password: str,
    posts: list[str],
) -> list[dict[str, str]]:
    """Publish a multi-part thread to Bluesky.

    Returns a list of created post references: [{'uri': ..., 'cid': ...}].
    """
    if not handle or not app_password or not posts:
        return []

    session = create_bluesky_session(handle, app_password)
    if not session:
        return []

    token = session["accessJwt"]
    did = session["did"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{BSKY_API_BASE}/com.atproto.repo.createRecord"

    created_posts: list[dict[str, str]] = []
    root_ref: dict[str, str] | None = None
    parent_ref: dict[str, str] | None = None

    for idx, text in enumerate(posts):
        # Bluesky has a 300 grapheme / char limit per post
        post_text = text.strip()
        if len(post_text) > 300:
            post_text = post_text[:297] + "..."

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

        record: dict[str, Any] = {
            "$type": "app.bsky.feed.post",
            "text": post_text,
            "createdAt": now_iso,
        }

        # Threading: point to root and previous parent
        if root_ref and parent_ref:
            record["reply"] = {
                "root": root_ref,
                "parent": parent_ref,
            }

        payload = {
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": record,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code in (200, 201):
                res_data = resp.json()
                current_ref = {
                    "uri": res_data.get("uri", ""),
                    "cid": res_data.get("cid", ""),
                }
                created_posts.append(current_ref)

                if idx == 0:
                    root_ref = current_ref
                parent_ref = current_ref
            else:
                logger.warning(f"Failed to post to Bluesky (part {idx + 1}): {resp.status_code} - {resp.text}")
                break
        except Exception as e:
            logger.warning(f"Error publishing post to Bluesky: {e}")
            break

    if created_posts:
        logger.info(f"Successfully published {len(created_posts)}-part thread to Bluesky (@{session['handle']})!")

    return created_posts
