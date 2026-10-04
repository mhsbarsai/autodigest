from __future__ import annotations
import json
import logging
from pathlib import Path

from src.config import StorageConfig

logger = logging.getLogger(__name__)

class ArticleCache:
    """Handles seen-article hash persistence in GCS."""

    def __init__(self, config: StorageConfig):
        self.config = config
        # Google Cloud Storage import here assuming it's available in real environment
        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.config.bucket_name)
            self.blob = self.bucket.blob("seen_articles.json")
        except ImportError:
            logger.warning("google-cloud-storage not installed. ArticleCache will fail if used.")

    def load_seen_hashes(self) -> set[str]:
        """Download JSON file from GCS and return hashes."""
        try:
            if not self.blob.exists():
                return set()
            data = self.blob.download_as_string()
            return set(json.loads(data))
        except Exception as e:
            logger.error(f"Failed to load hashes from GCS: {e}")
            return set()

    def save_seen_hashes(self, hashes: set[str]) -> None:
        """Upload hashes to GCS."""
        try:
            data = json.dumps(list(hashes))
            self.blob.upload_from_string(data, content_type="application/json")
        except Exception as e:
            logger.error(f"Failed to save hashes to GCS: {e}")


class LocalArticleCache:
    """Local file-based article cache for development."""

    def __init__(self, config: StorageConfig):
        self.config = config
        self.file_path = Path("data/seen_articles.json")
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_seen_hashes(self) -> set[str]:
        """Load hashes from local JSON file."""
        if not self.file_path.exists():
            return set()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load local hashes: {e}")
            return set()

    def save_seen_hashes(self, hashes: set[str]) -> None:
        """Save hashes to local JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(list(hashes), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save local hashes: {e}")


def create_cache(config: StorageConfig, use_local: bool = False) -> ArticleCache | LocalArticleCache:
    """Factory to create appropriate cache instance with graceful local fallback."""
    if use_local:
        return LocalArticleCache(config)
    try:
        return ArticleCache(config)
    except Exception as e:
        logger.warning(f"Google Cloud Storage not configured or unavailable ({e}). Falling back to local file cache.")
        return LocalArticleCache(config)
