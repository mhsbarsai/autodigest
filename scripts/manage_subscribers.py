"""CLI tool for managing newsletter subscribers."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.distribution.subscriber_manager import SubscriberManager


def main() -> None:
    parser = argparse.ArgumentParser(description="NeuralBrief Subscriber Management CLI")
    parser.add_argument("--list", action="store_true", help="List all active subscribers")
    parser.add_argument("--add", type=str, help="Add a new subscriber email")
    parser.add_argument("--remove", type=str, help="Remove / unsubscribe an email")
    parser.add_argument("--import-file", type=str, help="Path to text or CSV file containing emails to import")

    args = parser.parse_args()
    manager = SubscriberManager()

    if args.add:
        success = manager.add_subscriber(args.add)
        if success:
            print(f"[OK] Successfully added subscriber: {args.add}")
        else:
            print(f"[INFO] Failed to add or already exists: {args.add}")

    elif args.remove:
        success = manager.remove_subscriber(args.remove)
        if success:
            print(f"[OK] Unsubscribed: {args.remove}")
        else:
            print(f"[WARN] Email not found: {args.remove}")

    elif args.import_file:
        file_path = Path(args.import_file)
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}")
            sys.exit(1)

        count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                email = line.strip().strip(",")
                if email and manager.add_subscriber(email):
                    count += 1
        print(f"[OK] Successfully imported {count} new subscriber(s) from {file_path.name}")

    else:
        # Default action: list subscribers
        subscribers = manager.get_active_subscribers()
        print("=" * 50)
        print(f"NeuralBrief Active Subscribers ({len(subscribers)}):")
        print("=" * 50)
        for i, email in enumerate(subscribers, 1):
            print(f" {i}. {email}")
        print("=" * 50)


if __name__ == "__main__":
    main()
