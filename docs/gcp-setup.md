# GCP Setup — Panelyst

Verified working configuration as of **2026-05-14**. This is the recipe; the `.env` checked into `.env.example` matches it.

## Identity

| Item | Value |
|---|---|
| Owner | `app.2weeks@gmail.com` |
| Project ID | `panelyst-hackathon` |
| Project number | `916178791322` |
| Billing account | `01B677-A6E5C9-B265AF` ("크레딧계정") |
| Default region (Gemini 2.5 + Cloud Run + Firestore) | `us-central1` |
| Endpoint for Gemini 3 family | **`global`** (regional endpoints return 404) |

## Service account (the dev / local-code identity)

| Item | Value |
|---|---|
| Name | `panelyst-dev` |
| Email | `panelyst-dev@panelyst-hackathon.iam.gserviceaccount.com` |
| Key file | `~/.config/gcloud/panelyst-dev-sa-key.json` (mode 600, outside the repo) |
| Roles granted | `roles/aiplatform.user`, `roles/datastore.user`, `roles/storage.objectUser`, `roles/secretmanager.secretAccessor`, `roles/run.invoker`, `roles/eventarc.eventReceiver`, `roles/pubsub.subscriber`, `roles/iam.serviceAccountTokenCreator` |

Local code authenticates via `GOOGLE_APPLICATION_CREDENTIALS=/path/to/panelyst-dev-sa-key.json` (set in `.env`).

## Gemini model panel — verified live (2026-05-14)

| Tier | Model ID | Status | Endpoint | short-OK p50 | eval-JSON p50 (71 in, ≤800 out) | Notes |
|---|---|:--:|---|--:|--:|---|
| **Pro** | `gemini-3.1-pro-preview` | preview | **global** | 3,693 ms | 9,265 ms | Heavy reasoning; BLUE synthesis + BMAD scorer. Thinking model — give 4096+ output tokens. |
| **Flash** | `gemini-3-flash-preview` | preview | **global** | 1,346 ms | 4,036 ms | Mid-tier hats (RED, YELLOW, GREEN, WHITE). Sometimes wraps JSON in ` ```json ` fences — parser must strip. |
| **Flash-Lite** | `gemini-3.1-flash-lite` | **GA** | **global** | 959 ms | 1,267 ms | Cheap, fast. Code-Grader scoring, utility calls, web-search summarization. |
| Pro fallback | `gemini-2.5-pro` | GA | us-central1 | 3,156 ms | 11,007 ms (MAX_TOKENS at 800) | Reliable fallback. **Needs ≥2000 output tokens** — heavy thinker. |
| Flash fallback | `gemini-2.5-flash` | GA | us-central1 | 1,353 ms | 3,843 ms | Reliable mid-tier fallback. |
| Flash-Lite fallback | `gemini-2.5-flash-lite` | GA | us-central1 | 860 ms | **740 ms** | Fastest of the lot — good for tight loops. |

Source of truth for the test: [`/tmp/panelyst-model-test.json`](/tmp/panelyst-model-test.json). Reproducer: [`/tmp/panelyst-gemini-test.py`](/tmp/panelyst-gemini-test.py).

### Key gotchas

1. **`global` vs regional.** Gemini 3 publisher models appear in the catalog listing (`v1beta1/publishers/google/models`) returned by *any* region, but `generateContent` only succeeds when you target `https://aiplatform.googleapis.com/v1/projects/{P}/locations/global/publishers/google/models/{M}:generateContent`. Hitting `us-central1`/`asia-northeast3`/`us-east5`/etc. returns 404 "Publisher Model not found." Gemini 2.5 is the opposite — works on regional, not on global for some IDs.
2. **`gemini-3-pro-preview` is 404 even on global.** The 3-Pro slot is served as **`gemini-3.1-pro-preview`** (note the `.1`). `gemini-3-pro-image-preview` exists but is image-specialized.
3. **Thinking-model token budgets.** `gemini-2.5-pro` hit `finishReason: MAX_TOKENS` with `maxOutputTokens=800` on a tiny JSON-eval prompt. Give Pro tier ≥4096; Flash ≥2048; Flash-Lite ≥1024.
4. **ADC quota project must match.** A fresh GCP project pretty often inherits `quota_project_id` from whatever the previous `gcloud auth application-default login` set. If you see `403 PERMISSION_DENIED 'serviceusage.services.use'` errors, edit `~/.config/gcloud/application_default_credentials.json` and set `quota_project_id` to `panelyst-hackathon` — or use a service-account key (recommended; what we did).
5. **APIs enabled** (37 services total once deps resolved): `aiplatform`, `generativelanguage`, `discoveryengine`, `run`, `storage`, `eventarc`, `pubsub`, `firestore`, `secretmanager`, `cloudbuild`, `artifactregistry`, `iamcredentials`, `cloudresourcemanager`.

## Bootstrap reproducer (gcloud CLI)

```bash
PROJECT_ID=panelyst-hackathon
BILLING=01B677-A6E5C9-B265AF
REGION=us-central1

# project
gcloud projects create "$PROJECT_ID" --name="Panelyst"
gcloud config set project "$PROJECT_ID"
gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING"

# APIs
gcloud services enable \
  aiplatform.googleapis.com generativelanguage.googleapis.com discoveryengine.googleapis.com \
  run.googleapis.com storage.googleapis.com eventarc.googleapis.com pubsub.googleapis.com \
  firestore.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com iamcredentials.googleapis.com cloudresourcemanager.googleapis.com \
  --project="$PROJECT_ID"

# Service account + roles
SA_NAME=panelyst-dev
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
gcloud iam service-accounts create "$SA_NAME" --display-name="Panelyst dev (local + Cloud Run)" --project="$PROJECT_ID"
for role in aiplatform.user datastore.user storage.objectUser \
            secretmanager.secretAccessor run.invoker \
            eventarc.eventReceiver pubsub.subscriber iam.serviceAccountTokenCreator; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" --role="roles/$role" --condition=None --quiet
done

# Key (outside the repo)
KEY="$HOME/.config/gcloud/panelyst-dev-sa-key.json"
gcloud iam service-accounts keys create "$KEY" --iam-account="$SA_EMAIL" --project="$PROJECT_ID"
chmod 600 "$KEY"

# Storage buckets (Phase 3)
gcloud storage buckets create "gs://$PROJECT_ID-uploads" --location="$REGION" --uniform-bucket-level-access
gcloud storage buckets create "gs://$PROJECT_ID-reports" --location="$REGION" --uniform-bucket-level-access

# Artifact Registry (Phase 3)
gcloud artifacts repositories create panelyst --repository-format=docker --location="$REGION"

# Firestore Native (do once via Console: Firestore → Create database → Native mode → region)

# Use the SA from local code
export GOOGLE_APPLICATION_CREDENTIALS="$KEY"
```

## Health-check (post-setup smoke test)

```bash
python3 - <<'PY'
from google.oauth2 import service_account
import google.auth.transport.requests, requests, os, time
creds = service_account.Credentials.from_service_account_file(
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
  scopes=["https://www.googleapis.com/auth/cloud-platform"])
creds.refresh(google.auth.transport.requests.Request())
project = os.environ["GOOGLE_CLOUD_PROJECT"]
for tier, (model, loc) in {
    "PRO":        ("gemini-3.1-pro-preview", "global"),
    "FLASH":      ("gemini-3-flash-preview",  "global"),
    "FLASH_LITE": ("gemini-3.1-flash-lite",   "global"),
}.items():
    host = "aiplatform.googleapis.com" if loc=="global" else f"{loc}-aiplatform.googleapis.com"
    url = f"https://{host}/v1/projects/{project}/locations/{loc}/publishers/google/models/{model}:generateContent"
    body = {"contents":[{"role":"user","parts":[{"text":"Reply OK"}]}],"generationConfig":{"maxOutputTokens":200,"temperature":0}}
    t0=time.perf_counter()
    r = requests.post(url, headers={"Authorization":f"Bearer {creds.token}","Content-Type":"application/json"}, json=body, timeout=60)
    dt=(time.perf_counter()-t0)*1000
    txt = r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","") if r.status_code==200 else r.text[:100]
    print(f"{tier:11s} {model:30s} {loc:12s} {dt:6.0f}ms HTTP {r.status_code} → {txt.strip()[:30]!r}")
PY
```

Expected: all three return HTTP 200 with `'OK'` (or similar) in under ~5s.
