# infra

Deployment for the live Cloud Run demo (project `panelyst-hackathon`, us-central1):

- `Dockerfile.api` / `Dockerfile.web` — multi-stage builds (web bakes
  `NEXT_PUBLIC_API_BASE` at build time).
- `docker-compose.yml` — local full stack (web + api).
- `cloudbuild-api.yaml` / `cloudbuild-web.yaml` — Cloud Build configs.
- `deploy.sh` — hard-scoped to `panelyst-hackathon` (ignores the active gcloud
  project). Modes: real (Vertex `gemini-3.1-flash-lite` + Arize AX), `--no-phoenix`
  (real Vertex, tracing off), `--mock` (deterministic, no creds).

No Firebase Auth — the demo endpoints are intentionally open. The Arize AX key
lives in Secret Manager (`phoenix-api-key`); the runtime SA has
`aiplatform.user` + `secretmanager.secretAccessor`.
