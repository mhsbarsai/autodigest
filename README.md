# 🤖 AutoDigest — Fully Automated AI Newsletter System

> **A 100% autonomous, zero-maintenance newsletter engine powered by Google Gemini AI, Beehiiv, and Google Cloud Functions.**

---

## 📖 Overview

**AutoDigest** runs every morning on autopilot:
1. **Scrapes & Ingests:** Fetches 30–50 trending tech & AI stories from 15+ curated RSS feeds.
2. **Deduplicates:** Filters out any article previously published using cryptographic hashing.
3. **AI Curation & Scoring:** Uses **Gemini 2.5 Flash** to evaluate and rank articles by relevance and impact.
4. **AI Synthesis:** Summarizes the top 3–5 stories with catchy headlines, key takeaways, and a "Tool of the Day".
5. **Assembly:** Renders a mobile-responsive, email-client-optimized HTML template with automatic affiliate links.
6. **Publishing:** Automatically schedules and blasts the newsletter to subscribers via **Beehiiv REST API**.

**Your operational effort:** 0 minutes/day. Check the dashboard once a week to track subscriber growth and sponsorship revenue.

---

## 💰 Operating Cost: $0.00 / month

AutoDigest is engineered to operate strictly within the **Always Free** tiers of every provider:

| Service | Free Tier Allowance | Our Daily Usage | Monthly Cost |
|---|---|---|:---:|
| **Google Gemini API** | 1,500 requests / day | 2–3 requests / day | **$0.00** |
| **Resend** (or Beehiiv) | 3,000 emails / month (100/day) | 1 daily blast | **$0.00** |
| **Google Cloud Functions** | 2,000,000 invocations / month | 30 invocations / month | **$0.00** |
| **Google Cloud Scheduler** | 3 free cron jobs | 1 daily cron job | **$0.00** |
| **Google Cloud Storage** | 5 GB standard storage | < 1 MB cache | **$0.00** |

---

## 🚀 Quick Start (5-Minute Local Setup)

### 1. Prerequisites
- Python 3.12+
- A free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)
- A free **Resend Account** from [resend.com](https://resend.com/) *(Bisa kirim email langsung tanpa geoblock)*

### 2. Clone / Open Project
```bash
cd autodigest
```

### 3. Create Virtual Environment & Install Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Open `.env` and fill in your keys:
```ini
GEMINI_API_KEY=AIzaSy...
DISTRIBUTION_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxxxxxx
RESEND_FROM_EMAIL=AutoDigest <onboarding@resend.dev>
RESEND_TO_EMAIL=your_email@gmail.com
NEWSLETTER_NAME=AutoDigest
```
*(How to get Resend API Key: Resend Dashboard → API Keys → Create API Key).*

### 5. Run a Local Test (Dry-Run Mode)
```powershell
python scripts/test_local.py --dry-run
```
- Fetches real live RSS news.
- Calls Gemini AI to curate and summarize.
- Generates the email HTML inside `output/latest_preview.html`.
- Automatically opens the rendered newsletter in your default browser.
- **Does NOT send any emails or touch your Beehiiv live list.**

---

## ☁️ Cloud Deployment (Autopilot 24/7)

When you're ready to let the AI run on autopilot without needing your computer on:

### Option A: Windows PowerShell
```powershell
.\scripts\setup_gcp.ps1 -ProjectId "your-gcp-project-id"
.\scripts\deploy.ps1 -ProjectId "your-gcp-project-id"
```

### Option B: Linux / macOS / Cloud Shell
```bash
chmod +x scripts/*.sh
./scripts/setup_gcp.sh "your-gcp-project-id"
./scripts/deploy.sh us-central1 "your-gcp-project-id"
```

Once deployed, **Google Cloud Scheduler** will automatically invoke the function every day at **6:00 AM EST**, assemble the issue, and schedule it on Beehiiv for **7:00 AM EST delivery**.

---

## 📁 Project Architecture

```
autodigest/
├── README.md                      # Complete guide & documentation
├── requirements.txt               # Dependencies
├── .env.example                   # Environment configuration template
│
├── src/
│   ├── config.py                  # App configuration & dataclasses
│   ├── main.py                    # Pipeline orchestrator & Cloud Function entrypoint
│   │
│   ├── ai/                        # AI Processing Layer
│   │   ├── gemini_client.py       # Google GenAI SDK client with retries
│   │   ├── content_scorer.py      # Relevance & newsworthiness scoring
│   │   ├── summarizer.py          # Digest synthesis & structured output
│   │   ├── subject_generator.py   # High-CTR subject line generation
│   │   └── prompts.py             # Editorial system prompts
│   │
│   ├── ingestion/                 # Content Ingestion Layer
│   │   ├── feed_registry.py       # 15+ curated RSS feed sources
│   │   ├── rss_fetcher.py         # Multi-feed RSS parser
│   │   ├── article_extractor.py   # Trafilatura full-text article extractor
│   │   └── deduplicator.py        # Cryptographic content deduplication
│   │
│   ├── assembly/                  # Newsletter Assembly Layer
│   │   ├── template_engine.py     # Jinja2 mobile-first HTML email builder
│   │   ├── affiliate_injector.py  # Safe regex affiliate link insertion
│   │   └── sponsor_slot.py        # Dedicated ad slot placeholder
│   │
│   ├── distribution/              # Distribution Layer
│   │   └── beehiiv_client.py      # Beehiiv REST API v2 client
│   │
│   ├── storage/                   # Storage Layer
│   │   └── gcs_cache.py           # GCS / Local seen-articles cache
│   │
│   └── models/                    # Pydantic Schemas
│       └── schemas.py             # Shared data contracts
│
├── templates/
│   └── newsletter.html.j2         # Responsive HTML email template
│
├── scripts/
│   ├── test_local.py              # Local runner with browser preview
│   ├── verify_pipeline.py         # Automated self-test suite
│   ├── deploy.ps1 / deploy.sh     # Cloud Function deployment
│   └── setup_gcp.ps1 / .sh        # GCP resource provisioning
│
└── tests/
    └── test_pipeline.py           # Pytest unit test suite
```

---

## 📈 Monetization Roadmap

Once AutoDigest starts collecting subscribers:

1. **0 – 1,000 Subscribers:**
   - Focus on consistent delivery and list building.
   - Earn affiliate commissions from AI tools mentioned in the newsletter (ChatGPT, Claude, Cursor, Notion AI).
2. **1,000 – 2,500 Subscribers:**
   - Activate **Beehiiv Boosts** (earn $1 – $3 for every reader that subscribes to recommended partner newsletters).
3. **2,500 – 5,000 Subscribers:**
   - Turn on the **Beehiiv Ad Network** (programmatic sponsorships paying $30 – $60 CPM).
   - Expected revenue: **$300 – $800 / month**.
4. **5,000 – 10,000+ Subscribers:**
   - Direct brand sponsorships ($200 – $500 per email slot).
   - Expected revenue: **$1,500 – $4,000+ / month**.

---

## 🛡️ License & Ethics
- Only fair-use article summaries and quotes are published.
- Original sources and author publications are always credited with direct back-links.
- Built-in one-click unsubscribe links comply with CAN-SPAM and GDPR regulations.
