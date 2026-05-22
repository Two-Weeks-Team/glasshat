#!/usr/bin/env bash
# Deploy Glasshat to Cloud Run — HARD-SCOPED to the hackathon project.
#
# SAFETY: the active gcloud config may point at an unrelated PRODUCTION project.
# This script ALWAYS passes --project=panelyst-hackathon explicitly and never
# reads or changes the active config. Run from the repo root.
#
#   bash infra/deploy.sh --confirm            # real Vertex Gemini + Phoenix Cloud
#   bash infra/deploy.sh --confirm --mock     # deterministic mock/memory demo (no creds)
#
# Real mode prerequisites (one-time, you run these):
#   1. Phoenix Cloud API key in Secret Manager:
#        printf '%s' "<PHOENIX_API_KEY>" | gcloud secrets create phoenix-api-key \
#          --data-file=- --project=panelyst-hackathon
#   2. The Cloud Run runtime service account needs:
#        roles/aiplatform.user           (call Vertex Gemini)
#        roles/secretmanager.secretAccessor on phoenix-api-key
#   3. Optional override: export PHOENIX_COLLECTOR_ENDPOINT=... (default below).
set -euo pipefail

PROJECT="panelyst-hackathon"
REGION="us-central1"
REPO="glasshat"
PHOENIX_COLLECTOR_ENDPOINT="${PHOENIX_COLLECTOR_ENDPOINT:-https://app.phoenix.arize.com}"

MODE="real"
CONFIRMED=""
NO_PHOENIX=""
for arg in "$@"; do
  case "$arg" in
    --confirm) CONFIRMED="yes" ;;
    --mock) MODE="mock" ;;
    --no-phoenix) NO_PHOENIX="yes" ;;  # real Vertex, tracing → NoOp (phoenix extra omitted)
  esac
done

if [[ "$CONFIRMED" != "yes" ]]; then
  echo "Refusing to deploy without --confirm."
  echo "  Target project : $PROJECT (Cloud Run, BILLABLE)"
  echo "  Active project : $(gcloud config get-value project 2>/dev/null || echo unknown) (IGNORED by this script)"
  echo "  Mode           : real (Vertex+Phoenix) unless --mock is passed"
  echo "  Re-run: bash infra/deploy.sh --confirm [--mock]"
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

# --- Per-mode build args + runtime env ---
# Gemini 3.x preview is global-endpoint-only (regional → 404); pin the proven
# 2.5 GA models that work on the us-central1 regional endpoint used by the client.
GEMINI_ENV="GLASSHAT_GEMINI_PRO=gemini-2.5-pro,GLASSHAT_GEMINI_FLASH=gemini-2.5-flash,GLASSHAT_GEMINI_FLASH_LITE=gemini-2.5-flash"

if [[ "$MODE" == "real" && "$NO_PHOENIX" == "yes" ]]; then
  echo "==> Mode: REAL Vertex Gemini, tracing OFF (NoOp — phoenix extra omitted)"
  UV_EXTRAS="--extra vertex"
  API_ENV="LLM_BACKEND=vertex,MONITOR_BACKEND=phoenix-cloud,DOCSTORE_BACKEND=memory,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_REGION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=true,${GEMINI_ENV}"
  API_SECRETS=()
elif [[ "$MODE" == "real" ]]; then
  echo "==> Mode: REAL (Vertex Gemini + Phoenix Cloud)"
  if ! gcloud secrets describe phoenix-api-key --project="$PROJECT" >/dev/null 2>&1; then
    echo "Missing secret 'phoenix-api-key'. Create it first:" >&2
    echo "  printf '%s' \"<PHOENIX_API_KEY>\" | gcloud secrets create phoenix-api-key --data-file=- --project=$PROJECT" >&2
    exit 3
  fi
  UV_EXTRAS="--extra vertex --extra phoenix"
  API_ENV="LLM_BACKEND=vertex,MONITOR_BACKEND=phoenix-cloud,DOCSTORE_BACKEND=memory,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_REGION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=true,${GEMINI_ENV},PHOENIX_COLLECTOR_ENDPOINT=${PHOENIX_COLLECTOR_ENDPOINT},PHOENIX_PROJECT_NAME=glasshat"
  API_SECRETS=(--set-secrets "PHOENIX_API_KEY=phoenix-api-key:latest")
else
  echo "==> Mode: MOCK (deterministic, no credentials)"
  UV_EXTRAS=""
  API_ENV="LLM_BACKEND=mock,MONITOR_BACKEND=phoenix-local,DOCSTORE_BACKEND=memory,GOOGLE_CLOUD_PROJECT=${PROJECT}"
  API_SECRETS=()
fi

echo "==> Building API image via Cloud Build (UV_EXTRAS='${UV_EXTRAS}')..."
gcloud builds submit --project="$PROJECT" \
  --config=infra/cloudbuild-api.yaml \
  --substitutions=_IMAGE="$API_IMAGE",_UV_EXTRAS="$UV_EXTRAS" .

echo "==> Deploying API to Cloud Run (min-instances=0)..."
gcloud run deploy glasshat-api --project="$PROJECT" --region="$REGION" \
  --image="$API_IMAGE" --min-instances=0 --allow-unauthenticated \
  --set-env-vars="$API_ENV" ${API_SECRETS[@]+"${API_SECRETS[@]}"}

API_URL=$(gcloud run services describe glasshat-api \
  --project="$PROJECT" --region="$REGION" --format="value(status.url)")

# The API URL must be baked into the web client bundle at BUILD time, so build
# the web image only after the API is up and its URL is known.
echo "==> Building web image via Cloud Build (NEXT_PUBLIC_API_BASE=${API_URL})..."
gcloud builds submit --project="$PROJECT" \
  --config=infra/cloudbuild-web.yaml \
  --substitutions=_IMAGE="$WEB_IMAGE",_API_BASE="$API_URL" .

echo "==> Deploying web to Cloud Run..."
gcloud run deploy glasshat-web --project="$PROJECT" --region="$REGION" \
  --image="$WEB_IMAGE" --min-instances=0 --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_BASE=${API_URL}"

WEB_URL=$(gcloud run services describe glasshat-web \
  --project="$PROJECT" --region="$REGION" --format="value(status.url)")

echo ""
echo "Deployed (mode=${MODE}):"
echo "  API: ${API_URL}"
echo "  Web: ${WEB_URL}"
echo "Verify: curl -fsS ${API_URL}/health"
