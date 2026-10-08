"""Creavora — Social Media Dispatch Diagnostic & Live Test Tool.

Run this script to test broadcasting to:
1. Telegram Channel
2. Discord Webhook
3. X / Twitter API

Usage:
  python scripts/test_social.py [--all] [--telegram] [--discord] [--twitter]
"""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
import sys

# Windows UTF-8 console output support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()

from src.distribution.social_poster import (
    dispatch_discord,
    dispatch_telegram,
    dispatch_twitter,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("test_social")


def verify_telegram() -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    print("\n" + "=" * 50)
    print("🤖 TELEGRAM CHANNEL TEST")
    print("=" * 50)

    if not token or not chat_id:
        print("❌ SKIPPED: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing.")
        print("   Cara konfigurasi:")
        print("   1. Buat bot via @BotFather di Telegram, salin Token-nya.")
        print("   2. Buat Channel publik/privat di Telegram, jadikan bot sebagai Admin.")
        print("   3. Isi TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID (contoh: @creavora_ai) di .env")
        return False

    test_message = (
        "🚀 *Creavora Social Automation Test*\n\n"
        "Sistem otomasi distribusi Creavora berhasil terhubung ke Channel ini!\n\n"
        "Setiap pagi pukul 06:00 WIB, ringkasan riset AI termutakhir akan disiarkan otomatis ke sini.\n\n"
        "👉 [Kunjungi Creavora Web](https://creavora.my.id/)"
    )

    print(f"Mengirim pesan uji coba ke chat: {chat_id} ...")
    success = dispatch_telegram(token, chat_id, test_message)
    if success:
        print("✅ SUKSES! Pesan uji coba berhasil masuk ke Telegram Channel.")
    else:
        print("❌ GAGAL: Periksa kembali Bot Token dan pastikan Bot sudah diundang sebagai Admin di Channel tersebut.")
    return success


def verify_discord() -> bool:
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

    print("\n" + "=" * 50)
    print("👾 DISCORD WEBHOOK TEST")
    print("=" * 50)

    if not webhook_url:
        print("❌ SKIPPED: DISCORD_WEBHOOK_URL is missing.")
        print("   Cara konfigurasi:")
        print("   1. Di Discord channel pilihanmu, klik ikon Settings (Edit Channel).")
        print("   2. Pilih Integrations -> Webhooks -> New Webhook -> Copy Webhook URL.")
        print("   3. Isi DISCORD_WEBHOOK_URL di .env")
        return False

    payload = {
        "username": "Creavora Bot",
        "avatar_url": "https://raw.githubusercontent.com/mhsbarsai/autodigest/main/docs/avatar.png",
        "embeds": [
            {
                "title": "⚡ Creavora Social Automation Test",
                "description": "Sistem otomasi distribusi Creavora berhasil terhubung ke server Discord ini!\n\nSetiap pukul 06:00 WIB, ringkasan harian akan disiarkan ke sini secara otomatis.\n\n[**Baca Web Creavora**](https://creavora.my.id/)",
                "color": 6514417,
                "footer": {"text": "Creavora — Daily 3-minute technical AI intelligence"},
            }
        ],
    }

    print("Mengirim kartu embed uji coba ke Discord Webhook...")
    success = dispatch_discord(webhook_url, payload)
    if success:
        print("✅ SUKSES! Embed uji coba berhasil muncul di Discord Server.")
    else:
        print("❌ GAGAL: Periksa kembali format DISCORD_WEBHOOK_URL.")
    return success


def verify_twitter() -> bool:
    key = os.getenv("TWITTER_API_KEY", "").strip()
    secret = os.getenv("TWITTER_API_SECRET", "").strip()
    token = os.getenv("TWITTER_ACCESS_TOKEN", "").strip()
    token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "").strip()

    print("\n" + "=" * 50)
    print("🐦 X / TWITTER API TEST")
    print("=" * 50)

    if not key or not secret or not token or not token_secret:
        print("❌ SKIPPED: Twitter API credentials incomplete.")
        print("   Dibutuhkan: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
        return False

    test_tweets = [
        "🚨 Testing Creavora Automated Dispatch Engine. Technical AI intelligence delivered daily at 6:00 AM WIB.\n\nVisit: https://creavora.my.id/"
    ]

    print("Mengirim tweet uji coba ke X / Twitter API v2...")
    tweet_ids = dispatch_twitter(key, secret, token, token_secret, test_tweets)
    if tweet_ids:
        print(f"✅ SUKSES! Tweet berhasil dipublikasikan. ID: {tweet_ids[0]}")
        return True
    else:
        print("❌ GAGAL: Periksa kembali permission API (Pastikan Read and Write aktif).")
        return False


def verify_bluesky() -> bool:
    handle = os.getenv("BLUESKY_HANDLE", "").strip()
    password = os.getenv("BLUESKY_APP_PASSWORD", "").strip()

    print("\n" + "=" * 50)
    print("🦋 BLUESKY AT PROTOCOL TEST")
    print("=" * 50)

    if not handle or not password:
        print("❌ SKIPPED: BLUESKY_HANDLE or BLUESKY_APP_PASSWORD is missing.")
        print("   Cara konfigurasi:")
        print("   1. Buat akun di https://bsky.app (misal: creavora.bsky.social).")
        print("   2. Masuk ke Settings -> Privacy & Security -> App Passwords -> Add App Password.")
        print("   3. Isi BLUESKY_HANDLE dan BLUESKY_APP_PASSWORD di .env")
        return False

    test_posts = [
        "🚨 Testing Creavora Automated Dispatch Engine on Bluesky! ⚡\n\nDaily 3-minute technical AI intelligence dispatched every morning at 06:00 WIB.\n\n👉 https://creavora.my.id",
        "🧵 Built for AI engineers, ML researchers, and builders.\n\nStrictly zero marketing PR hype, 100% hard engineering signal."
    ]

    print(f"Mengirim thread uji coba ke Bluesky (@{handle}) via AT Protocol...")
    from src.distribution.bluesky_poster import dispatch_bluesky_thread
    posts = dispatch_bluesky_thread(handle, password, test_posts)
    if posts:
        print(f"✅ SUKSES! {len(posts)} post thread berhasil dipublikasikan di Bluesky!")
        return True
    else:
        print("❌ GAGAL: Periksa kembali handle dan App Password Bluesky.")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Creavora Social Media Automation")
    parser.add_argument("--telegram", action="store_true", help="Test Telegram Channel")
    parser.add_argument("--discord", action="store_true", help="Test Discord Webhook")
    parser.add_argument("--twitter", action="store_true", help="Test X / Twitter")
    parser.add_argument("--bluesky", action="store_true", help="Test Bluesky AT Protocol")
    parser.add_argument("--all", action="store_true", help="Test all configured channels")

    args = parser.parse_args()

    run_all = args.all or (not args.telegram and not args.discord and not args.twitter and not args.bluesky)

    results = {}
    if run_all or args.telegram:
        results["Telegram"] = verify_telegram()
    if run_all or args.discord:
        results["Discord"] = verify_discord()
    if run_all or args.bluesky:
        results["Bluesky"] = verify_bluesky()
    if run_all or args.twitter:
        results["Twitter"] = verify_twitter()

    print("\n" + "=" * 50)
    print("📊 RINGKASAN TEST OTOMASI MEDSOS")
    print("=" * 50)
    for channel, ok in results.items():
        status = "✅ ACTIVE / VERIFIED" if ok else "⚠️ NOT CONFIGURED / FAILED"
        print(f"  • {channel:<12}: {status}")
    print("=" * 50)


if __name__ == "__main__":
    main()
