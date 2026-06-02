#!/usr/bin/env bash
# Deploy Glasshat to Cloud Run — HARD-SCOPED to the hackathon project.
#
# SAFETY: the active gcloud config may point at an unrelated PRODUCTION project.
# This script ALWAYS passes --project=panelyst-hackathon explicitly and never
# reads or changes the active config. Run from the repo root.
#
#   ARIZE_SPACE_ID=<id> bash infra/deploy.sh --confirm   # real Vertex + Arize AX tracing
#   bash infra/deploy.sh --confirm --no-phoenix          # real Vertex, tracing off
#   bash infra/deploy.sh --confirm --mock                # deterministic mock demo (no creds)
#
# Real (Arize AX) prerequisites (one-time, you run these):
#   1. Arize AX API key (the `ak-…` key) in Secret Manager as `phoenix-api-key`:
#        printf '%s' "<ARIZE_API_KEY>" | gcloud secrets create phoenix-api-key \
#          --data-file=- --project=panelyst-hackathon
#   2. export ARIZE_SPACE_ID=<your AX space id>   (from app.arize.com → Space → API Keys)
#   3. Cloud Run runtime SA needs roles/aiplatform.user + roles/secretmanager.secretAccessor.
set -euo pipefail

PROJECT="panelyst-hackathon"
REGION="us-central1"
REPO="glasshat"
ARIZE_SPACE_ID="${ARIZE_SPACE_ID:-}"

# --- Judging-window knobs (env-overridable) ---
# MIN_INSTANCES=1 keeps one warm instance so the first judge click is fast
# instead of a 5-7s cold start. Roll back after judging with:
#   MIN_INSTANCES=0 bash infra/deploy.sh --confirm
# Cost: one always-on instance per service while set to 1.
MIN_INSTANCES="${MIN_INSTANCES:-1}"
# The docstore default (memory) is process-local: /api/runs lookups are not
# durable across cold restarts. For durable run history set the backend to
# firestore AND grant the Cloud Run runtime SA roles/datastore.user with a
# Firestore (native mode) database present, then verify a run fetch across a
# cold-instance boundary. Default stays memory to avoid overclaiming persistence.
DOCSTORE_BACKEND="${DOCSTORE_BACKEND:-memory}"

# Live learning-loop + API-hardening flips (real mode). The container ships Node
# so the audit can reach Phoenix over MCP; set PHOENIX_COLLECTOR_ENDPOINT to your
# Phoenix base URL to genuinely activate the live-trace consultant + dataset
# write-back. Left empty, the audit gracefully falls back to the spike-D table
# (honest — no phantom Phoenix calls). CORS is locked to the web origin.
PHOENIX_COLLECTOR_ENDPOINT="${PHOENIX_COLLECTOR_ENDPOINT:-}"
WEB_ORIGIN="${WEB_ORIGIN:-https://glasshat-web-o366v7tl2q-uc.a.run.app}"

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
# Gemini 3.x runs on the Vertex GLOBAL endpoint (a regional endpoint → 404). The
# LLM client is location-aware (per-tier *_location, set to "global" below);
# embeddings (text-embedding-005) stay on the regional endpoint. Models: GA
# gemini-3.1-flash-lite drives the live eval path (flash + flash_lite tiers);
# gemini-3.1-pro-preview backs the pro tier (URL rubric synthesis only).
GEMINI_ENV="GLASSHAT_GEMINI_PRO=gemini-3.1-pro-preview,GLASSHAT_GEMINI_FLASH=gemini-3.1-flash-lite,GLASSHAT_GEMINI_FLASH_LITE=gemini-3.1-flash-lite,GLASSHAT_GEMINI_PRO_LOCATION=global,GLASSHAT_GEMINI_FLASH_LOCATION=global,GLASSHAT_GEMINI_FLASH_LITE_LOCATION=global"

if [[ "$MODE" == "real" && "$NO_PHOENIX" == "yes" ]]; then
  echo "==> Mode: REAL Vertex Gemini, tracing OFF (NoOp — phoenix extra omitted)"
  UV_EXTRAS="--extra vertex"
  API_ENV="LLM_BACKEND=vertex,MONITOR_BACKEND=phoenix-cloud,DOCSTORE_BACKEND=${DOCSTORE_BACKEND},GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_REGION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=true,${GEMINI_ENV}"
  API_SECRETS=()
elif [[ "$MODE" == "real" ]]; then
  echo "==> Mode: REAL (Vertex Gemini + Arize AX tracing)"
  if [[ -z "$ARIZE_SPACE_ID" ]]; then
    echo "Set ARIZE_SPACE_ID=<your AX space id> for real Arize tracing, or use --no-phoenix." >&2
    exit 4
  fi
  if ! gcloud secrets describe phoenix-api-key --project="$PROJECT" >/dev/null 2>&1; then
    echo "Missing secret 'phoenix-api-key' (your Arize AX API key). Create it first:" >&2
    echo "  printf '%s' \"<ARIZE_API_KEY>\" | gcloud secrets create phoenix-api-key --data-file=- --project=$PROJECT" >&2
    exit 3
  fi
  UV_EXTRAS="--extra vertex --extra arize"
  # Learning-loop + repo-grader + CORS flips. CONSULTANT/DATASET_WRITER=phoenix-mcp
  # genuinely consult/write the Phoenix calibration dataset when
  # PHOENIX_COLLECTOR_ENDPOINT is set (Node is in the image); empty endpoint →
  # graceful spike-D table fallback. REPO_GRADER=github-api folds repo evidence in.
  LEARNING_ENV="CONSULTANT_BACKEND=phoenix-mcp,DATASET_WRITER_BACKEND=phoenix-mcp,REPO_GRADER_BACKEND=github-api,PHOENIX_CALIBRATION_DATASET=glasshat-calibration,PHOENIX_COLLECTOR_ENDPOINT=${PHOENIX_COLLECTOR_ENDPOINT},CORS_ALLOW_ORIGINS=${WEB_ORIGIN}"
  API_ENV="LLM_BACKEND=vertex,MONITOR_BACKEND=arize,DOCSTORE_BACKEND=${DOCSTORE_BACKEND},GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_REGION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=true,${GEMINI_ENV},ARIZE_SPACE_ID=${ARIZE_SPACE_ID},PHOENIX_PROJECT_NAME=glasshat,${LEARNING_ENV}"
  API_SECRETS=(--set-secrets "PHOENIX_API_KEY=phoenix-api-key:latest")
  echo "==> Learning loop: CONSULTANT/DATASET_WRITER=phoenix-mcp (endpoint='${PHOENIX_COLLECTOR_ENDPOINT:-<unset → table fallback>}'), REPO_GRADER=github-api, CORS→${WEB_ORIGIN}"
else
  echo "==> Mode: MOCK (deterministic, no credentials)"
  UV_EXTRAS=""
  API_ENV="LLM_BACKEND=mock,MONITOR_BACKEND=phoenix-local,DOCSTORE_BACKEND=${DOCSTORE_BACKEND},GOOGLE_CLOUD_PROJECT=${PROJECT}"
  API_SECRETS=()
fi

echo "==> Building API image via Cloud Build (UV_EXTRAS='${UV_EXTRAS}')..."
gcloud builds submit --project="$PROJECT" \
  --config=infra/cloudbuild-api.yaml \
  --substitutions=_IMAGE="$API_IMAGE",_UV_EXTRAS="$UV_EXTRAS" .

echo "==> Deploying API to Cloud Run (min-instances=${MIN_INSTANCES})..."
gcloud run deploy glasshat-api --project="$PROJECT" --region="$REGION" \
  --image="$API_IMAGE" --min-instances="$MIN_INSTANCES" --allow-unauthenticated \
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
  --image="$WEB_IMAGE" --min-instances="$MIN_INSTANCES" --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_BASE=${API_URL}"

WEB_URL=$(gcloud run services describe glasshat-web \
  --project="$PROJECT" --region="$REGION" --format="value(status.url)")

echo ""
echo "Deployed (mode=${MODE}):"
echo "  API: ${API_URL}"
echo "  Web: ${WEB_URL}"

# Post-deploy smoke: assert the API actually serves before declaring success.
# Cold start can take a few seconds, so retry briefly. Non-zero exit on failure
# so an operator notices a broken deploy immediately (rollback: see infra/README.md).
echo "==> Verifying API health (${API_URL}/health)..."
health_ok=""
for attempt in 1 2 3 4 5 6; do
  if curl -fsS --max-time 10 "${API_URL}/health" | grep -q '"status":"ok"'; then
    health_ok="yes"
    break
  fi
  echo "   health not ready yet (attempt ${attempt}/6) — retrying in 5s..."
  sleep 5
done
if [ -z "$health_ok" ]; then
  echo "ERROR: ${API_URL}/health did not return status=ok after deploy." >&2
  echo "Rollback: gcloud run services update-traffic glasshat-api --project=${PROJECT} --region=${REGION} --to-revisions=PREVIOUS=100" >&2
  exit 1
fi
echo "==> API health OK."
