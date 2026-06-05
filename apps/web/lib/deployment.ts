/**
 * Single source of truth for the Rapid Agent / Arize-track stack proof.
 *
 * These describe the *deployed* configuration (infra/deploy.sh real mode) and
 * are intentionally honest about state: four pillars run on every live request;
 * the Phoenix MCP calibration path is real and E2E-verified but is NOT the
 * default deployed audit path (the deployed audit uses the spike-D calibrated
 * table prior). Consumed by ProofStrip (first-screen chips) and ProofReceipt
 * (post-run receipt) so the two never drift.
 */

export type ProofState = "live" | "wired" | "muted";

export interface ProofChip {
  id: string;
  /** Short pillar name, readable in a 3-second video frame. */
  label: string;
  /** One- or two-word qualifier. */
  detail: string;
  state: ProofState;
  /** Tooltip / verification hint (how a judge confirms it). */
  title: string;
}

/** The five first-screen proof chips, in stack order. */
export const PROOF_CHIPS: ProofChip[] = [
  {
    id: "gemini",
    label: "Gemini / GEAP",
    detail: "3.1-flash-lite",
    state: "live",
    title: "Gemini generation on the Gemini Enterprise Agent Platform (Vertex AI SDK · global endpoint).",
  },
  {
    id: "adk",
    label: "Google ADK",
    detail: "orchestrating",
    state: "live",
    title: "Google ADK runtime instruments the evaluation pipeline.",
  },
  {
    id: "cloudrun",
    label: "Cloud Run",
    detail: "deployed",
    state: "live",
    title: "API + web on Cloud Run (panelyst-hackathon, us-central1).",
  },
  {
    id: "arize",
    label: "Arize AX",
    detail: "tracing",
    state: "live",
    title: "OpenInference/OTLP spans exported to otlp.arize.com (one per agent).",
  },
  {
    id: "phoenixmcp",
    label: "Phoenix MCP",
    detail: "calibration path",
    state: "wired",
    title:
      "ADK MCPToolset over stdio (npx @arizeai/phoenix-mcp); E2E-verified. " +
      "The deployed audit uses the calibrated table prior, not a live MCP call per request.",
  },
];

/** State → presentation. `live` = green/check, `wired` = amber, `muted` = grey. */
export const PROOF_STATE_UI: Record<
  ProofState,
  { color: string; mark: string; word: string }
> = {
  live: { color: "var(--color-good)", mark: "✓", word: "live" },
  wired: { color: "var(--color-warn)", mark: "~", word: "wired · E2E" },
  muted: { color: "var(--color-muted)", mark: "·", word: "unavailable" },
};

/**
 * Deployment metadata for the proof receipt. Fields here are *static deployment
 * config* (from infra/deploy.sh real mode), distinct from the live values a
 * RunRecord carries (run id, correction count, criteria count, timestamp).
 */
export const DEPLOYMENT_META = {
  modelFamily: "gemini-3.1-flash-lite",
  modelTier: "flash-lite · Vertex global endpoint",
  tracerBackend: "Arize AX · otlp.arize.com",
  deploymentTarget: "Cloud Run · panelyst-hackathon · us-central1",
  /** Deployed default. The Phoenix MCP consultant is the E2E-only variant. */
  consultantMode: "table-prior",
} as const;

/**
 * Genuine Gemini Enterprise Agent Platform (Agent Engine) deployment + live Arize AX
 * results, captured 2026-06-05. Every number here is verifiable (see
 * `claudedocs/arize-evidence/`): the resource serves live `stream_query`s and the
 * trace-span count came from `client.spans.list(project="glasshat")`.
 */
export const AGENT_PLATFORM = {
  platform: "Gemini Enterprise Agent Platform",
  surface: "Agent Engine / Runtime",
  runtime: "ADK 2.0 Workflow graph",
  resource: "reasoningEngines/7480191458771730432",
  /** spans for two live queries: agent_run → invocation → 6 hats' Gemini calls. */
  traceSpans: 104,
  traceShape: "agent → Workflow → 6 hats (generate + embed)",
  /** Arize AX Experiment hit@13 — winners ranked into the top-13. */
  hitAt13: { live: 0.6154, mock: 0.3846, chance: 0.26, winnersInTop13: "8 / 13" },
  axDataset: "glasshat-golden",
  axExperiment: "glasshat-hit-at-13-gemini",
  /** Honesty rails (do NOT remove): binary-label hit@13, never a rank curve. */
  caveat: "hit@13 on binary Winner labels — not a rank curve; audit Δ=0 on this set",
} as const;
