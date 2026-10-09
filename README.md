# ⚡ Creavora — Autonomous Technical AI Intelligence Publication

<div align="center">

[![Website](https://img.shields.io/badge/Website-creavora.my.id-amber?style=for-the-badge&logo=googlechrome&logoColor=white)](https://creavora.my.id)
[![Telegram](https://img.shields.io/badge/Telegram-@CreavoraAI-blue?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/CreavoraAI)
[![X / Twitter](https://img.shields.io/badge/X-@creavora__-black?style=for-the-badge&logo=x&logoColor=white)](https://x.com/creavora_)
[![Cost](https://img.shields.io/badge/Cost-$0%2Fmonth-emerald?style=for-the-badge&logo=cashapp&logoColor=white)](https://creavora.my.id)
[![License](https://img.shields.io/badge/License-MIT-slate?style=for-the-badge)](LICENSE)

<br/>

**The Technical AI Briefing You Read Before Your First Commit.**  
*Autonomous 3-minute morning briefings filtering arXiv preprints, model architecture shifts, GPU kernels, and developer tools. Strictly zero PR hype. 100% hard engineering signal.*

</div>

---

## 🏛️ Live Production Infrastructure

| Platform | Endpoint / Handle | Status |
| :--- | :--- | :---: |
| **Official Web Publication** | [https://creavora.my.id](https://creavora.my.id) | 🟢 Live (HTTPS) |
| **Telegram Channel** | [@CreavoraAI](https://t.me/CreavoraAI) | 🟢 Broadcast Active |
| **X / Twitter Teasers** | [@creavora_](https://x.com/creavora_) | 🟢 Daily Threads |
| **RSS 2.0 Syndication** | [https://creavora.my.id/feed.xml](https://creavora.my.id/feed.xml) | 🟢 Auto-updating |
| **Search Engine Sitemap** | [https://creavora.my.id/sitemap.xml](https://creavora.my.id/sitemap.xml) | 🟢 IndexNow Verified |
| **Daily Email Delivery** | `Creavora <newsletter@creavora.my.id>` | 🟢 DKIM/DMARC Verified |

---

## ⚙️ Architecture & Autonomous Pipeline

Every morning at **23:00 UTC (06:00 AM WIB)**, GitHub Actions triggers the autonomous pipeline with zero human intervention:

```
┌────────────────────────────────────────────────────────┐
│ 1. INGESTION & MONITORING                              │
│    • arXiv CS.AI, CL, LG, NE preprints                 │
│    • Hacker News Show & Top AI threads                 │
│    • Hugging Face Models & GitHub Trending             │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ 2. DEDUPLICATION & FILTERING                           │
│    • SHA-256 fingerprint matching against seen history │
│    • Strips 100% marketing fluff & PR claims          │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ 3. COGNITIVE SYNTHESIS (Google Gemini Flash-Lite)      │
│    • Extracts latency, VRAM, and kernel trade-offs     │
│    • Synthesizes code reproduction snippets            │
│    • Nominates open-source Tool of the Day             │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ 4. MULTI-CHANNEL AUTONOMOUS BROADCAST                  │
│    ├─► Email Blast: Resend API (DKIM/DMARC verified)   │
│    ├─► Web Publication: Vercel Edge (creavora.my.id)   │
│    ├─► Dynamic Social Card: 1200x630 dark banner (PIL) │
│    ├─► Telegram Channel: Photo + pinned post @Creavora │
│    ├─► Bluesky Network: 4-part AT Protocol thread      │
│    ├─► Webhook Bridge: Make.com/n8n (X & LinkedIn)     │
│    ├─► RSS 2.0 Feed: Auto-updates docs/feed.xml        │
│    └─► Social Memory: Persistent social_history.json   │
└────────────────────────────────────────────────────────┘
```

---

## 💰 Operating Cost: Strictly $0.00 / month

Creavora is engineered to operate indefinitely within the **Always Free** tiers of cloud providers:

| Component | Provider & Free Allowance | Our Usage | Cost |
| :--- | :--- | :--- | :---: |
| **AI Synthesis** | Google Gemini (AI Studio Free Tier) | 2–3 requests / day | **$0.00** |
| **Automation Runner** | GitHub Actions (2,000 min/mo free) | ~1.5 min / day | **$0.00** |
| **Edge Web Hosting** | Vercel Serverless (Hobby Free) | Static + Edge Functions | **$0.00** |
| **Email Infrastructure** | Resend Free (3,000 emails/mo) | Daily verified dispatch | **$0.00** |
| **Community Broadcast** | Telegram Bot API | Instant & unlimited | **$0.00** |
| **Decentralized Social** | Bluesky AT Protocol | Direct API & Threads | **$0.00** |
| **Social Webhook Bridge**| Make.com / n8n Free Tier | X, LinkedIn, Threads sync | **$0.00** |
| **Search Syndication** | IndexNow Protocol (Bing, Yandex) | Real-time push | **$0.00** |

---

## 🛠️ Local Development & Diagnostics

### 1. Prerequisites
- Python 3.12+
- `uv` package manager (recommended) or `pip`

### 2. Setup
```bash
git clone https://github.com/mhsbarsai/autodigest.git
cd autodigest
cp .env.example .env
```

### 3. Run Test Suite
```bash
uv run pytest
```

### 4. Test Multi-Channel Social & Telegram Dispatch
```bash
uv run python scripts/test_social.py --telegram
```

### 5. Run Full Dry-Run Pipeline
```bash
uv run python -m src.main
```

---

## 🤝 Sponsorship & Partnerships

Reach software engineers, ML researchers, and technical founders every morning:
- **Web:** [creavora.my.id/#sponsor](https://creavora.my.id/#sponsor)
- **Inquiries:** `mahsabar98@gmail.com`

---

## 📄 License

MIT License © 2026 Creavora Engineering Press. Built for the developer and AI research community.
