# AutoDigest — GCP Resource Setup Script (PowerShell)
# Sets up Cloud Storage bucket and Secret Manager secrets for AutoDigest.

param(
    [string]$ProjectId = "",
    [string]$BucketName = "autodigest-cache",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 📦 AutoDigest — GCP Resource Provisioning " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not $ProjectId) {
    $ProjectId = (gcloud config get-value project 2>$null)
    if (-not $ProjectId) {
        Write-Error "No Google Cloud Project ID found. Please set: gcloud config set project YOUR_PROJECT_ID"
    }
}

# 1. Create Cloud Storage Bucket (if not exists)
Write-Host "`n[1/2] Creating Cloud Storage bucket ($BucketName)..." -ForegroundColor Yellow
$BucketExists = (gcloud storage buckets list --filter="name:$BucketName" --format="value(name)" 2>$null)
if (-not $BucketExists) {
    gcloud storage buckets create "gs://$BucketName" --location=$Region --project=$ProjectId
    Write-Host "Created bucket: gs://$BucketName" -ForegroundColor Green
} else {
    Write-Host "Bucket already exists: gs://$BucketName" -ForegroundColor Green
}

# 2. Setup Secret Manager Placeholders
Write-Host "`n[2/2] Configuring Secret Manager secrets..." -ForegroundColor Yellow
$Secrets = @("GEMINI_API_KEY", "BEEHIIV_API_KEY", "BEEHIIV_PUBLICATION_ID")

foreach ($Secret in $Secrets) {
    $Exists = (gcloud secrets list --filter="name:$Secret" --format="value(name)" --project=$ProjectId 2>$null)
    if (-not $Exists) {
        gcloud secrets create $Secret --replication-policy="automatic" --project=$ProjectId
        Write-Host "Created secret placeholder: $Secret" -ForegroundColor Cyan
        Write-Host " -> Add your secret value with: gcloud secrets versions add $Secret --data-file=YOUR_KEY.txt" -ForegroundColor Gray
    } else {
        Write-Host "Secret already exists: $Secret" -ForegroundColor Green
    }
}

Write-Host "`nDone! Cloud resources are ready." -ForegroundColor Green
