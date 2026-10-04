"""AutoDigest / NeuralBrief — Subscriber Management.

Handles persistent tracking, validation, and retrieval of active newsletter subscribers.
"""
from __future__ import annotations

import datetime
import json
import logging
import re
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class SubscriberRecord(TypedDict):
    email: str
    subscribed_at: str
    status: str


class SubscriberManager:
    """Manages newsletter subscriber persistence and operations."""

    def __init__(self, file_path: Path | None = None) -> None:
        if file_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            self.file_path = project_root / "data" / "subscribers.json"
        else:
            self.file_path = file_path

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save_records([])

    def _load_records(self) -> list[SubscriberRecord]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load subscribers from {self.file_path}: {e}")
            return []

    def _save_records(self, records: list[SubscriberRecord]) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save subscribers to {self.file_path}: {e}")

    def add_subscriber(self, email: str) -> bool:
        """Add a new subscriber if valid and not already registered.

        Returns True if newly added, False if already present or invalid.
        """
        clean_email = email.strip().lower()
        if not EMAIL_REGEX.match(clean_email):
            logger.warning(f"Invalid email address provided: {email}")
            return False

        records = self._load_records()
        for record in records:
            if record["email"].lower() == clean_email:
                if record["status"] != "active":
                    record["status"] = "active"
                    self._save_records(records)
                    logger.info(f"Re-activated subscriber: {clean_email}")
                    return True
                logger.info(f"Subscriber already active: {clean_email}")
                return False

        new_record: SubscriberRecord = {
            "email": clean_email,
            "subscribed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "active",
        }
        records.append(new_record)
        self._save_records(records)
        logger.info(f"Added new subscriber: {clean_email}")
        return True

    def remove_subscriber(self, email: str) -> bool:
        """Mark a subscriber as unsubscribed."""
        clean_email = email.strip().lower()
        records = self._load_records()
        found = False
        for record in records:
            if record["email"].lower() == clean_email:
                record["status"] = "unsubscribed"
                found = True
                break

        if found:
            self._save_records(records)
            logger.info(f"Unsubscribed: {clean_email}")
        return found

    def get_active_subscribers(self) -> list[str]:
        """Return list of all active subscriber email addresses."""
        records = self._load_records()
        return [
            r["email"]
            for r in records
            if r.get("status", "active") == "active"
        ]
