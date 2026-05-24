/**
 * Visual proof timeline — the main video-capturable moment.
 *
 *   Input → RubricSynthesizer → BluePlanner → SixHatPanel → Audit → Final score
 *           └──────────────── Arize AX observability rail ───────────────┘
 *                                          ▲ Phoenix MCP calibration path
 *
 * Each agent is a node; Arize AX is rendered as the observability rail beneath
 * the instrumented agents (not just a badge); Phoenix MCP is the calibration
 * lookup path feeding the Audit node; the Audit node shows the self-correction
 * as a before → after score movement. Driven by the live SSE stage during a run
 * and by `done` for the completed/sample state.
 */

export interface TimelineCorrection {
  label: string;
  from: number;
  to: number;
}

export interface ProofTimelineProps {
  /** Current SSE stage name during a live run (omit for the completed view). */
  stage?: string;
  /** True once the run completed — forces every node to done. */
  done?: boolean;
  /** Headline self-correction shown as before → after on the Audit node. */
  correction?: TimelineCorrection | null;
  className?: string;
}

type NodeId = "input" | "rubric" | "planner" | "panel" | "audit" | "score";
type NodeState = "done" | "active" | "pending";

interface PipelineNode {
  id: NodeId;
  label: string;
  sub: string;
  /** Emits an Arize AX span (sits over the observability rail). */
  instrumented: boolean;
}

export const TIMELINE_NODES: PipelineNode[] = [
  { id: "input", label: "Input", sub: "deck + rubric source", instrumented: false },
  { id: "rubric", label: "RubricSynthesizer", sub: "official rules → rubric", instrumented: true },
  { id: "planner", label: "BluePlanner", sub: "hats + weights", instrumented: true },
  { id: "panel", label: "SixHatPanel", sub: "6 hats · evidence", instrumented: true },
  { id: "audit", label: "Audit", sub: "calibrated self-correct", instrumented: true },
  { id: "score", label: "Final score", sub: "rubric native scale", instrumented: true },
];

const STAGE_TO_INDEX: Record<string, number> = {
  queued: 0,
  ingesting: 0,
  planning: 1,
  hats_running: 3,
  auditing: 4,
  audit_started: 4,
  inconsistency_flagged: 4,
  phoenix_consultation: 4,
  anchor_retrieval: 4,
  score_corrected: 4,
  scoring: 5,
  graph_reshape: 5,
  complete: 6,
};

/** Stages during which the Arize rail is actively emitting spans. */
const SPAN_STAGES = new Set<string>([
  "planning",
  "hats_running",
  "auditing",
  "audit_started",
  "inconsistency_flagged",
  "phoenix_consultation",
  "anchor_retrieval",
  "score_corrected",
  "scoring",
  "graph_reshape",
]);

/** Stages during which the Phoenix MCP calibration path is being consulted. */
const MCP_STAGES = new Set<string>(["phoenix_consultation", "anchor_retrieval"]);

/** Index of the active node (nodes before are done, after are pending). */
export function activeIndex(stage: string | undefined, done: boolean | undefined): number {
  if (done) return TIMELINE_NODES.length; // all done
  if (stage == null) return -1; // idle
  return STAGE_TO_INDEX[stage] ?? -1;
}

function nodeState(index: number, active: number, stage: string | undefined): NodeState {
  // "planning" is a single SSE stage covering both RubricSynthesizer (1) and
  // BluePlanner (2); light both so no node is skipped over during a live run.
  if (stage === "planning" && (index === 1 || index === 2)) return "active";
  if (index < active) return "done";
  if (index === active) return "active";
  return "pending";
}

const NODE_TONE: Record<NodeState, string> = {
  done: "border-[var(--color-good)]/55 text-[var(--color-good)]",
  active: "animate-pulse-ring border-[var(--color-accent)] text-[var(--color-ink)]",
  pending: "border-[var(--color-border)]/50 text-[var(--color-muted)]",
};

export function ProofTimeline({
  stage,
  done = false,
  correction = null,
  className = "",
}: ProofTimelineProps) {
  const active = activeIndex(stage, done);
  const railLive = done || (stage != null && SPAN_STAGES.has(stage));
  const mcpActive = stage != null && MCP_STAGES.has(stage);

  return (
    <div
      data-testid="proof-timeline"
      className={"flex flex-col gap-3 " + className}
      aria-label="Evaluation proof timeline"
    >
      {/* Agent pipeline */}
      <ol className="flex flex-wrap items-stretch gap-2">
        {TIMELINE_NODES.map((n, i) => {
          const state = nodeState(i, active, stage);
          const isAudit = n.id === "audit";
          return (
            <li
              key={n.id}
              data-testid={`timeline-node-${n.id}`}
              data-state={state}
              className={
                "relative flex min-w-[8.5rem] flex-1 flex-col gap-0.5 rounded-xl border px-3 py-2 text-xs transition " +
                NODE_TONE[state]
              }
            >
              <span className="flex items-center gap-1.5 font-medium">
                <span className="font-mono tabular-nums opacity-50">{i + 1}</span>
                {n.label}
                {n.instrumented && (
                  <span
                    aria-hidden
                    title="emits an Arize AX span"
                    className="ml-auto h-1.5 w-1.5 rounded-full bg-[var(--color-accent-2)]"
                  />
                )}
              </span>
              <span className="text-[var(--color-muted)]">{n.sub}</span>
              {isAudit && correction && (state === "active" || state === "done") && (
                <CorrectionDelta correction={correction} />
              )}
            </li>
          );
        })}
      </ol>

      {/* Arize AX observability rail — spans the instrumented agents */}
      <div
        data-testid="arize-rail"
        data-live={railLive}
        className={
          "flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs " +
          (railLive
            ? "border-[var(--color-accent-2)]/60 bg-[color-mix(in_oklch,var(--color-accent-2)_10%,transparent)]"
            : "border-[var(--color-border)]/50")
        }
      >
        <span
          aria-hidden
          className={
            "h-2 w-2 rounded-full " + (railLive ? "animate-pulse-ring" : "")
          }
          style={{ background: "var(--color-accent-2)" }}
        />
        <span className="font-medium text-[var(--color-accent-2)]">Arize AX</span>
        <span className="text-[var(--color-muted)]">
          OpenInference spans · one per agent → otlp.arize.com
        </span>
      </div>

      {/* Phoenix MCP calibration path — feeds the Audit node */}
      <div
        data-testid="phoenix-mcp-path"
        data-active={mcpActive}
        className={
          "flex flex-wrap items-center gap-2 rounded-lg border px-3 py-1.5 text-xs " +
          (mcpActive
            ? "border-[var(--color-warn)] bg-[color-mix(in_oklch,var(--color-warn)_10%,transparent)]"
            : "border-[var(--color-warn)]/40")
        }
      >
        <span aria-hidden className="text-[var(--color-warn)]">
          ↑
        </span>
        <span className="font-medium text-[var(--color-warn)]">Phoenix MCP</span>
        <span className="text-[var(--color-muted)]">
          calibration lookup → Audit{" "}
          <span className="italic">(E2E-verified; deployed audit uses the table prior)</span>
        </span>
      </div>

      <p className="text-xs text-[var(--color-muted)]">
        Every agent emits an Arize AX span; the audit consults the calibration path and
        self-corrects <span className="text-[var(--color-ink)]">before the score is locked</span>.
      </p>
    </div>
  );
}

function CorrectionDelta({ correction }: { correction: TimelineCorrection }) {
  const delta = correction.to - correction.from;
  const direction = delta < 0 ? "lowered" : delta > 0 ? "raised" : "held";
  const tone =
    direction === "lowered"
      ? "var(--color-warn)"
      : direction === "raised"
        ? "var(--color-good)"
        : "var(--color-muted)";
  const caret = direction === "lowered" ? "▾" : direction === "raised" ? "▴" : "—";
  return (
    <span
      data-testid="timeline-correction"
      data-direction={direction}
      className="mt-1 inline-flex items-center gap-1 font-mono tabular-nums"
      style={{ color: tone }}
      title={correction.label}
    >
      {correction.from.toFixed(1)}
      <span aria-hidden>→</span>
      {correction.to.toFixed(1)}
      <span aria-hidden>{caret}</span>
    </span>
  );
}
