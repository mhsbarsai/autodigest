# AutoDigest — Cloud Deployment Script (PowerShell for Windows)
# Deploys AutoDigest to Google Cloud Functions (Gen 2) with Cloud Scheduler.

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 🚀 AutoDigest — Deploying to Google Cloud Functions " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not $ProjectId) {
    $ProjectId = (gcloud config get-value project 2>$null)
    if (-not $ProjectId) {
        Write-Error "No Google Cloud Project ID found. Please run: gcloud config set project YOUR_PROJECT_ID"
    }
}

Write-Host "Using Project: $ProjectId" -ForegroundColor Green
Write-Host "Using Region:  $Region" -ForegroundColor Green

# 1. Enable Required GCP APIs
Write-Host "`n[1/4] Enabling required APIs (Cloud Run, Functions, Scheduler, Secret Manager)..." -ForegroundColor Yellow
gcloud services enable `
    cloudfunctions.googleapis.com `
    run.googleapis.com `
    cloudscheduler.googleapis.com `
    secretmanager.googleapis.com `
    storage.googleapis.com `
    --project=$ProjectId

# 2. Deploy Cloud Function (Gen 2)
Write-Host "`n[2/4] Deploying Cloud Function: autodigest-daily..." -ForegroundColor Yellow
gcloud functions deploy autodigest-daily `
    --gen2 `
    --runtime=python312 `
    --region=$Region `
    --source=. `
    --entry-point=newsletter_handler `
    --trigger-http `
    --no-allow-unauthenticated `
    --memory=512MB `
    --timeout=300s `
    --max-instances=1 `
    --min-instances=0 `
    --project=$ProjectId

# 3. Get Function URL
$FunctionUrl = (gcloud functions describe autodigest-daily --gen2 --region=$Region --format="value(serviceConfig.uri)" --project=$ProjectId)
Write-Host "`nFunction Deployed! Endpoint: $FunctionUrl" -ForegroundColor Green

# 4. Create/Update Cloud Scheduler Trigger (Daily at 11:00 UTC = 7:00 AM EST)
Write-Host "`n[3/4] Setting up Cloud Scheduler (Daily @ 11:00 UTC / 7:00 AM EST)..." -ForegroundColor Yellow
$JobName = "autodigest-daily-trigger"

$ExistingJob = (gcloud scheduler jobs list --location=$Region --format="value(ID)" --filter="ID:$JobName" --project=$ProjectId)

if ($ExistingJob) {
    Write-Host "Updating existing scheduler job: $JobName" -ForegroundColor Cyan
    gcloud scheduler jobs update http $JobName `
        --location=$Region `
        --schedule="0 11 * * *" `
        --uri=$FunctionUrl `
        --http-method=POST `
        --oidc-service-account-email="$ProjectId@appspot.gserviceaccount.com" `
        --project=$ProjectId
} else {
    Write-Host "Creating new scheduler job: $JobName" -ForegroundColor Cyan
    gcloud scheduler jobs create http $JobName `
        --location=$Region `
        --schedule="0 11 * * *" `
        --uri=$FunctionUrl `
        --http-method=POST `
        --oidc-service-account-email="$ProjectId@appspot.gserviceaccount.com" `
        --project=$ProjectId
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " 🎉 DEPLOYMENT SUCCESSFUL! " -ForegroundColor Green
Write-Host " AutoDigest is now scheduled to run daily at 7:00 AM EST on autopilot!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
