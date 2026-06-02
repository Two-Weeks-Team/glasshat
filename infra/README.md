# infra

Deployment for the live Cloud Run demo (project `panelyst-hackathon`, us-central1):

- `Dockerfile.api` / `Dockerfile.web` — multi-stage builds (web bakes
  `NEXT_PUBLIC_API_BASE` at build time).
- `docker-compose.yml` — local full stack (web + api).
- `cloudbuild-api.yaml` / `cloudbuild-web.yaml` — Cloud Build configs.
- `deploy.sh` — hard-scoped to `panelyst-hackathon` (ignores the active gcloud
  project). Modes: real (Vertex `gemini-3.1-flash-lite` + Arize AX), `--no-phoenix`
  (real Vertex, tracing off), `--mock` (deterministic, no creds).

No Firebase Auth — the demo endpoints are intentionally open (but rate-limited
per IP and CORS-restricted to the deployed web origin via `RATE_LIMIT_PER_MINUTE`
/ `CORS_ALLOW_ORIGINS`). The Arize AX key lives in Secret Manager
(`phoenix-api-key`); the runtime SA has `aiplatform.user` +
`secretmanager.secretAccessor`.

`deploy.sh` runs a post-deploy health assertion (`/health` must return
`status=ok`, with cold-start retries) and exits non-zero on failure.

## Rollback

Cloud Run keeps every revision. To roll the API back to the previous good
revision (instant, no rebuild):

```bash
gcloud run services update-traffic glasshat-api \
  --project=panelyst-hackathon --region=us-central1 --to-revisions=PREVIOUS=100
```

List revisions / pin a specific one:

```bash
gcloud run revisions list --service=glasshat-api \
  --project=panelyst-hackathon --region=us-central1
gcloud run services update-traffic glasshat-api \
  --project=panelyst-hackathon --region=us-central1 --to-revisions=<REVISION>=100
```

(Same commands for `glasshat-web`.)
