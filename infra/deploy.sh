#!/usr/bin/env bash
# Deploy Glasshat to Cloud Run — HARD-SCOPED to the hackathon project.
#
# SAFETY: the active gcloud config may point at an unrelated PRODUCTION project.
# This script ALWAYS passes --project=panelyst-hackathon explicitly and never
# reads or changes the active config. Run from the repo root.
#
#   bash infra/deploy.sh --confirm
set -euo pipefail

PROJECT="panelyst-hackathon"
REGION="us-central1"
REPO="glasshat"

if [[ "${1:-}" != "--confirm" ]]; then
  echo "Refusing to deploy without --confirm."
  echo "  Target project : $PROJECT (Cloud Run, BILLABLE)"
  echo "  Active project : $(gcloud config get-value project 2>/dev/null || echo unknown) (IGNORED by this script)"
  echo "  Re-run: bash infra/deploy.sh --confirm"
  exit 1
fi

if [[ "$PROJECT" != "panelyst-hackathon" ]]; then
  echo "Guard: refusing — PROJECT is not panelyst-hackathon." >&2
  exit 2
fi

API_IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/api:latest"
WEB_IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/web:latest"

echo "==> Ensuring Artifact Registry repo exists..."
gcloud artifacts repositories describe "$REPO" \
  --project="$PROJECT" --location="$REGION" >/dev/null 2>&1 ||
  gcloud artifacts repositories create "$REPO" \
    --project="$PROJECT" --location="$REGION" --repository-format=docker

echo "==> Building API image via Cloud Build..."
gcloud builds submit --project="$PROJECT" \
  --config=infra/cloudbuild-api.yaml --substitutions=_IMAGE="$API_IMAGE" .

echo "==> Building web image via Cloud Build..."
gcloud builds submit --project="$PROJECT" \
  --config=infra/cloudbuild-web.yaml --substitutions=_IMAGE="$WEB_IMAGE" .

echo "==> Deploying API to Cloud Run (min-instances=0)..."
gcloud run deploy glasshat-api --project="$PROJECT" --region="$REGION" \
  --image="$API_IMAGE" --min-instances=0 --allow-unauthenticated \
  --set-env-vars="LLM_BACKEND=vertex,MONITOR_BACKEND=phoenix-cloud,DOCSTORE_BACKEND=firestore,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_GENAI_USE_VERTEXAI=true"

API_URL=$(gcloud run services describe glasshat-api \
  --project="$PROJECT" --region="$REGION" --format="value(status.url)")

echo "==> Deploying web to Cloud Run (NEXT_PUBLIC_API_BASE=${API_URL})..."
gcloud run deploy glasshat-web --project="$PROJECT" --region="$REGION" \
  --image="$WEB_IMAGE" --min-instances=0 --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_BASE=${API_URL}"

WEB_URL=$(gcloud run services describe glasshat-web \
  --project="$PROJECT" --region="$REGION" --format="value(status.url)")

echo ""
echo "Deployed:"
echo "  API: ${API_URL}"
echo "  Web: ${WEB_URL}"
echo "Verify: curl -fsS ${API_URL}/health"
