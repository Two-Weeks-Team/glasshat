# Glasshat — Team Onboarding

> **For**: a developer just added to the project. **Goal**: from zero context to first commit in ≤2 hours.
>
> **Last verified**: 2026-05-15. Update when the project structure or deploy story changes materially.

---

## 1. Read these in order (≤30 min total)

1. [`README.md`](../README.md) — one-paragraph + what it does + setup intro
2. [`docs/max-wins-plan.md`](max-wins-plan.md) §0-§4 — the dual-submission thesis + judging axes + wow moment narrative anchor
3. [`docs/wow-moment-design.md`](wow-moment-design.md) §1-§4 — the audit-the-auditor moment, decomposed
4. [`docs/architecture.md`](architecture.md) — topology + agent graph + abstractions
5. [`docs/rubric-synthesis-spec.md`](rubric-synthesis-spec.md) — RubricSynthesizer (new 2026-05-15)
6. [`docs/hybrid-mode-spec.md`](hybrid-mode-spec.md) — Judge × Participant viewports (new 2026-05-15)
7. [`PLAN.md`](../PLAN.md) — engineering inventory + Phase 1 task list (read PLAN's top ADDENDUM first; it points to max-wins-plan as the *authoritative* thesis)

**You don't need to read** (yet): `docs/technical-apex-features.md` (read when implementing a specific advanced feature), `docs/spike-results.md` (read if you're modifying the audit pipeline). `claudedocs/*` is historical — useful context but not authoritative.

---

## 2. Repo + tools setup (≤30 min)

### 2.1 Clone + check out

```bash
cd ~/Documents/GitHub/
gh repo clone Two-Weeks-Team/glasshat
cd glasshat
git remote -v   # expect: origin → https://github.com/Two-Weeks-Team/glasshat.git
```

### 2.2 Required toolchain versions

| Tool | Version | How to install |
|---|---|---|
| Python | **3.12** | `uv python install 3.12` (uv handles per-project versions) |
| uv (Python package manager) | ≥ 0.9 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node | **24** (or ≥ 22) | `nvm install 24 && nvm use 24` |
| npm | ships with Node | included |
| Docker | optional (for prod-style Phoenix self-host) | https://docs.docker.com/desktop/ |
| `gcloud` CLI | latest | https://cloud.google.com/sdk/docs/install |
| `gh` CLI | latest | https://cli.github.com/ |

Verify:

```bash
python3 --version       # → Python 3.12.x
node --version          # → v24.x or v22.x
uv --version            # → 0.9.x or later
gh auth status          # → Logged in to github.com
gcloud auth list        # → at least one ACTIVE account
```

### 2.3 Run the spikes (validates your environment + GCP setup)

```bash
cd spikes/
uv sync                 # installs Python 3.12 deps from pyproject + uv.lock
uv run python 01_spike_a_phoenix_mcp_smoke.py
uv run python 02_spike_b_adk_loop.py
# ... 03 through 07
```

All 7 should print `[PASS]`. If any fails:
- `01` (Phoenix MCP smoke) — Phoenix Cloud account needed (free tier at app.phoenix.arize.com). Set `PHOENIX_API_KEY` in `.env`.
- `02-03` (ADK) — Vertex auth needed. See `docs/gcp-setup.md` for the verified GCP bootstrap.
- `05` (SSE) — local Python server + browser; no external deps.

If you can't get a spike to pass, **don't push through** — ping the team. The spike was the bar for "environment ready"; if it fails, downstream Phase 1 code will fail in less visible ways.

### 2.4 `.env` setup (CRITICAL — never commit)

```bash
cp .env.example .env
# Open .env in your editor.
# Required for Phase 1 D (LLM adapter):
#   GLASSHAT_GOOGLE_CLOUD_PROJECT=panelyst-hackathon
#   GLASSHAT_GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/panelyst-dev-sa-key.json
#   GLASSHAT_VERTEX_LOCATION=us-central1
#   GLASSHAT_VERTEX_LOCATION_GLOBAL=global
# Required for Phase 1.4 (Phoenix):
#   GLASSHAT_PHOENIX_API_KEY=px_live_xxxxxxxx
#   GLASSHAT_PHOENIX_HOST=https://app.phoenix.arize.com
# Required for Phase 1.B (Qdrant):
#   GLASSHAT_QDRANT_URL=http://localhost:6333   (local docker)
#   GLASSHAT_QDRANT_API_KEY=                    (empty for local)
```

`.env` is in `.gitignore`. **Never commit it.** If you accidentally stage it: `git restore --staged .env && git update-index --assume-unchanged .env`.

### 2.5 GCP service account key

The SA key is at `~/.config/gcloud/panelyst-dev-sa-key.json` (mode 600). If you don't have it:

1. Ask a team admin for the key (1Password vault item: "Glasshat panelyst-dev SA key").
2. Save to `~/.config/gcloud/panelyst-dev-sa-key.json` with `chmod 600`.
3. Verify: `cat $GLASSHAT_GOOGLE_APPLICATION_CREDENTIALS | jq -r .client_email` should return `panelyst-dev@panelyst-hackathon.iam.gserviceaccount.com`.

**Production safety rule**: the SA can only impersonate the dev project. It has **no access** to any production system. Even so, treat it like a secret — `chmod 600`, never commit, never log to stdout.

---

## 3. Code conventions (≤15 min)

### 3.1 Python (services, agents)

- **Style**: ruff (formatter + linter). `uv run ruff format` + `uv run ruff check --fix`.
- **Types**: mypy strict on `services/shared/**`, `services/pipeline_orchestrator/**`. Use `pydantic` for I/O DTOs.
- **Imports**: absolute from `glasshat.*` root. No relative imports across packages.
- **Async**: every I/O function is `async`. Sync I/O is a code smell.
- **Errors**: typed exceptions (`GlasshatLLMError`, `QdrantRetrievalError`, etc.) inheriting `GlasshatError`. Never `raise Exception(...)` without a subclass.
- **Logging**: `structlog` with JSON output in prod, console in dev. No `print()` outside of `spikes/`.

### 3.2 TypeScript (Next.js web)

- **Style**: Biome (formatter + linter). `npx biome check --apply .`.
- **Types**: TypeScript strict. No `any`; use `unknown` + narrow.
- **Components**: function components only. No class components.
- **State**: Server state via Server Components + Route Handlers. Client state via React state / `useReducer`. Avoid global state unless cross-route persistence is required (then use Zustand).
- **Errors**: Error boundaries on every route segment. Show user-friendly fallback, log to console + Phoenix.

### 3.3 Comments

- **Default: NO comments.** Code should be self-explanatory via good naming.
- **Exception 1**: load-bearing constants ("Phoenix MCP requires npx stdio, not HTTP — see `docs/wow-moment-design.md` §5").
- **Exception 2**: workarounds for external bugs ("ADK MCPToolset requires double-wrapped StdioConnectionParams; documented bug XYZ").
- **Never**: `# This function does X` style — the function name should already say that.

### 3.4 Tests

- **Unit**: vitest (TS) / pytest (Python). Per-file colocated as `*.test.ts` / `test_*.py`.
- **Integration**: spikes-style scripts in `tests/integration/`. Hit real Vertex + Qdrant + Phoenix endpoints.
- **No mocks** for Vertex / Qdrant / Phoenix in integration tests — see [[user-local-first-then-cloud]] memory: real services or none.

---

## 4. Git workflow

### 4.1 Branching

- `main` is protected. **Never push to main directly.**
- Feature branches: `feat/<short-desc>`, `fix/<bug>`, `docs/<area>`, `chore/<thing>`.
- One feature = one branch = one PR.

### 4.2 Commits

- Conventional Commits format: `<type>: <subject>`.
- Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`.
- Subject ≤ 72 chars, imperative ("add X", not "added X" or "adds X").
- Body optional; if used, separate by blank line. Explain *why*, not *what*.

### 4.3 PRs

- Open a PR as soon as the branch exists (draft if WIP). Visibility > silence.
- PR description includes:
  - **What**: 1-3 bullets summarizing the change
  - **Why**: link to issue / docs reference
  - **Test plan**: how the reviewer should verify
- Request review from at least one teammate.
- **CI must pass** before merge (typecheck + tests + lint).

### 4.4 Merge strategy

- **Default**: `gh pr merge --merge` (preserves commit history).
- **Do NOT squash** (`--squash`). Commit history is preserved for audit-trail discipline — Glasshat sells "every score has a receipt"; our own engineering history must demonstrate the same.
- **Rebase** (`--rebase`) is allowed only when resolving conflicts or for hot-fix linearization.

### 4.5 What never to do

- ❌ `git push --force` to `main` or any shared branch
- ❌ `git rebase -i` on commits already on `origin`
- ❌ Commit `.env`, `.env.local`, service account keys, or any `*.key` file
- ❌ `git commit --no-verify` (skipping hooks) without team agreement
- ❌ Edit files in `claudedocs/` — those are historical session snapshots

---

## 5. The 5-team structure (for context)

Glasshat is built by 5 functional roles (one person may wear multiple hats in early Phase 1):

| Role | Owns | Primary docs |
|---|---|---|
| **Backend (LLM + Agent)** | `services/pipeline_orchestrator/`, `services/rubric_synthesizer/`, `services/shared/llm.py`, ADK wiring | wow-moment-design, rubric-synthesis-spec, technical-apex-features §3-§4 |
| **Data (Qdrant + corpus)** | `packages/shared/qdrant-schemas/`, `data/devpost-gemini3/`, `services/shared/qdrant.py`, calibration corpus pipeline | technical-apex-features §1, data/devpost-gemini3/INTEGRATION.md |
| **Frontend (Next.js)** | `apps/web/`, react-three-fiber 3D graph, Judge/Participant viewports, SSE consumption | hybrid-mode-spec, max-wins-plan §5 (demo scripts) |
| **DevOps / Infra** | `.env.example`, Cloud Run deploy, Eventarc, Firestore rules, CI/CD | architecture.md §4, gcp-setup.md |
| **QA / Demo** | Spike scripts, demo videos, end-to-end runs, threshold gate verification | spike-results, max-wins-plan §5 demo timing, hybrid-mode §3-§4 |

**Cross-cutting discipline**: every role emits OpenInference spans (Phoenix instrumented), every change goes through PR review, every external system sits behind an interface (`docs/architecture.md` §5).

---

## 6. Daily workflow (Phase 1)

1. **Morning standup** (async or sync, team norm): "yesterday I X, today I Y, blocked by Z."
2. **`/handon` at session start** (if using Claude Code): auto-loads latest handoff for context.
3. **Pick a task**: `gh issue list --assignee @me` or grab from the [Phase 1 task tracker](../PLAN.md) (see PLAN.md for the latest task breakdown).
4. **Branch, code, test**: feature branch → implement → test locally → push.
5. **Open PR**: link to issue, fill `What/Why/Test plan`, request review.
6. **Review etiquette**: respond to comments within 24h. Reviewers: prioritize unblocking over perfection.
7. **Merge**: `gh pr merge --merge` after approval + green CI.
8. **`/handoff` at session end** (if using Claude Code): creates `claudedocs/YYYY-MM-DD-session-handoff.md` for the next session.

---

## 7. Where to get help

| Question | Where to look |
|---|---|
| "How does the audit moment work?" | `docs/wow-moment-design.md` §3 (5-step decomposition) |
| "How is Qdrant used?" | `docs/architecture.md` §3, `technical-apex-features.md` §1 |
| "What's the rubric structure?" | `docs/rubric-synthesis-spec.md` §3 (output schema) |
| "How do I add a new preset rubric?" | `docs/rubric-synthesis-spec.md` §4 (Path A) — copy `qdrant.yaml` as template |
| "How do the two modes share data?" | `docs/hybrid-mode-spec.md` §6 (Firestore data model) |
| "What's the GCP setup?" | `docs/gcp-setup.md` (verified bootstrap recipe) |
| "What's the current task list?" | `PLAN.md` + GitHub issues |
| "What was decided when and why?" | `docs/max-wins-plan.md` §12 (decision log) + memory `~/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/` |

---

## 8. First commit checklist

Before your first PR is merged, verify:

- [ ] You've read README + max-wins-plan §0-§4 + architecture.md + the spec for the area you're touching
- [ ] You ran the 7 spikes and all passed (or you understand why a non-blocking one didn't)
- [ ] `.env` is local and never committed
- [ ] Branch name follows `<type>/<desc>` convention
- [ ] Commit messages follow Conventional Commits
- [ ] PR description has `What / Why / Test plan`
- [ ] No `any` in TS, no `print` in non-spike Python, no skipped tests
- [ ] You're using `gh pr merge --merge` (not squash) after approval

Welcome to Glasshat.

---

*Last updated: 2026-05-15 KST. Update when toolchain, conventions, or team structure changes.*
