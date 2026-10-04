#!/usr/bin/env bash
# AutoDigest — Cloud Deployment Script (Bash for Linux/macOS/Cloud Shell)
set -euo pipefail

REGION="${1:-us-central1}"
PROJECT_ID="${2:-$(gcloud config get-value project 2>/dev/null)}"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No Google Cloud Project ID found. Please set: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "=========================================================="
echo " 🚀 AutoDigest — Deploying to Google Cloud Functions "
echo " Project: $PROJECT_ID | Region: $REGION"
echo "=========================================================="

echo "[1/4] Enabling required APIs..."
gcloud services enable \
    cloudfunctions.googleapis.com \
    run.googleapis.com \
    cloudscheduler.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com \
    --project="$PROJECT_ID"

echo "[2/4] Deploying Cloud Function: autodigest-daily..."
gcloud functions deploy autodigest-daily \
    --gen2 \
    --runtime=python312 \
    --region="$REGION" \
    --source=. \
    --entry-point=newsletter_handler \
    --trigger-http \
    --no-allow-unauthenticated \
    --memory=512MB \
    --timeout=300s \
    --max-instances=1 \
    --min-instances=0 \
    --project="$PROJECT_ID"

FUNCTION_URL=$(gcloud functions describe autodigest-daily --gen2 --region="$REGION" --format="value(serviceConfig.uri)" --project="$PROJECT_ID")
echo "Function deployed at: $FUNCTION_URL"

echo "[3/4] Setting up Cloud Scheduler (Daily @ 11:00 UTC / 7:00 AM EST)..."
JOB_NAME="autodigest-daily-trigger"

if gcloud scheduler jobs describe "$JOB_NAME" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    gcloud scheduler jobs update http "$JOB_NAME" \
        --location="$REGION" \
        --schedule="0 11 * * *" \
        --uri="$FUNCTION_URL" \
        --http-method=POST \
        --oidc-service-account-email="${PROJECT_ID}@appspot.gserviceaccount.com" \
        --project="$PROJECT_ID"
else
    gcloud scheduler jobs create http "$JOB_NAME" \
        --location="$REGION" \
        --schedule="0 11 * * *" \
        --uri="$FUNCTION_URL" \
        --http-method=POST \
        --oidc-service-account-email="${PROJECT_ID}@appspot.gserviceaccount.com" \
        --project="$PROJECT_ID"
fi

echo "=========================================================="
echo " 🎉 DEPLOYMENT SUCCESSFUL!"
echo " AutoDigest is now scheduled to run daily at 7:00 AM EST!"
echo "=========================================================="
