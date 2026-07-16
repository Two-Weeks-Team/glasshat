# Dedicated-server migration TODO

Status: **deferred** (2026-07-16)

Glasshat/Panelyst is intentionally outside the current three-service cutover.  This
document is a backlog, not a deployment authorization.  Do not change the two
MongoDB hosts, GCP resources, DNS, nginx, Cloudflare, host ports, or running
containers while completing it.

## Binding target contract

- Run the application in an isolated Docker Compose project; publish no container
  port directly on the host.
- Attach a reverse proxy or Cloudflare Tunnel only after a read-only host inventory
  and an explicit cutover approval.
- Use the existing private MongoDB replica set only as an application dependency.
  Do not install containers on, reconfigure, back up, restore, or administer MongoDB.
- Use OpenAI Responses API model `gpt-5.4-mini-2026-03-17` with `store=false`, no
  hosted tools, and a shared UTC-day hard stop below 10 million tokens.
- Keep GCP integrations read-only until their data has been inventoried and an
  archive/retention decision has been approved.  Do not deploy to GCP.
- Preserve the current production revision for rollback until post-cutover
  validation and the observation window have passed.

## Implementation TODO

- [ ] Inventory the active Glasshat routes, workers, schedules, domains, GCP
  resources, secrets, databases, object storage, and current CI/CD triggers.
- [ ] Inspect the archived `kb` and `phoenix` PostgreSQL dump headers and record the
  source PostgreSQL major version and SHA-256.  Do not choose a restore image before
  this evidence exists.
- [ ] Pin the source-major PostgreSQL image and the self-hosted Phoenix image by
  digest; prove restore, schema migration, restart, and rollback against disposable
  volumes.
- [ ] Replace active Gemini/Vertex inference with the exact OpenAI snapshot above;
  add real-call contract tests for ingest, extraction, scoring, and structured output.
- [ ] Implement the shared Mongo-backed daily token reservation/reconciliation
  contract used by the other migrated services.
- [ ] Produce non-root, read-only, resource-limited API, web, edge, PostgreSQL, and
  Phoenix containers with private networks and zero host-published ports.
- [ ] Move runtime secrets to root-owned files; keep only secret names and schemas in
  Git.  Validate that images, logs, Compose output, and CI artifacts contain no
  secret values.
- [ ] Quarantine every GCP deploy workflow and replace it with manual, signed,
  vulnerability-scanned image publication that performs no deployment.
- [ ] Add health, readiness, dependency, restart, disk-headroom, backup/restore, and
  smoke-test gates.  Capture exact rollback commands before any cutover.
- [ ] Run unit, integration, restore, Compose, amd64 image, supply-chain, and
  application-level acceptance tests; attach evidence to a Draft PR.

## Preflight gates before implementation can become deployable

- [ ] Source PostgreSQL major version is proven from the dump.
- [ ] Required disk footprint is measured from immutable images plus restored data;
  the result fits current free space and the approved safety reserve.
- [ ] Both servers have read-only inventories of ports, listeners, nginx,
  Cloudflare, Docker networks, volumes, CPU, memory, and filesystem capacity.
- [ ] A collision-free placement and service-specific Compose project naming plan is
  approved.
- [ ] Secret ownership, DNS/Tunnel routing, maintenance window, rollback owner, and
  observation window are approved.
- [ ] The existing three priority services are stable; Glasshat cutover receives a
  separate explicit approval.

## Definition of done

The migration is complete only when a fresh deploy from immutable artifacts passes
application acceptance checks, restart and rollback drills, monitoring and backup
restore checks, and a post-cutover observation window without changing any existing
service.  A merged PR or a running container alone is not completion.
