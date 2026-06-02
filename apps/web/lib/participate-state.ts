/**
 * Pure state logic for the /participate run, kept out of the React component so
 * it can be unit-tested. Three concerns:
 *   1. reduceEvent  — fold the SSE stream into a live monitor state.
 *   2. scoreRows    — join the final RunRecord's scores with their rubric criteria.
 *   3. constellationNodes — project the result into the 3D self-correction graph,
 *      with a pre-correction origin so corrected nodes visibly "reshape".
 */

import type { AuditCorrection, RunRecord } from "@/lib/api";
import { projectCriterion, type Node3D } from "@/lib/projection";
import { preAuditScoreMap } from "@/lib/ranking";
import type { SseEvent } from "@/lib/sse";
import { AUDIT_BEATS } from "@/lib/stages";

const HAT_SCALE = 10; // hat assessments are 0–10 (see agents/types.py HatAssessment)

export interface BeatEntry {
  stage: string;
  detail?: string;
}

export interface LiveCorrection {
  criterion: string;
  from: number;
  to: number;
}

export interface RunState {
  runId: string;
  current: string;
  beats: BeatEntry[];
  corrections: LiveCorrection[];
  done: boolean;
}

export const initialRunState: RunState = {
  runId: "",
  current: "queued",
  beats: [],
  corrections: [],
  done: false,
};

const num = (v: unknown): number => (typeof v === "number" ? v : Number(v));
const fmt1 = (v: unknown): string => num(v).toFixed(1);

function isBeat(stage: string): boolean {
  return (AUDIT_BEATS as string[]).includes(stage) || stage === "graph_reshape";
}

/** Fold one SSE event into the live run state (pure). */
export function reduceEvent(state: RunState, e: SseEvent): RunState {
  const next: RunState = {
    ...state,
    beats: state.beats,
    corrections: state.corrections,
    current: e.stage,
  };

  if (e.stage === "queued" && typeof e.data.run_id === "string") {
    next.runId = e.data.run_id;
  }

  if (isBeat(e.stage)) {
    let detail: string | undefined;
    if (e.stage === "phoenix_consultation") {
      detail = `Δ${num(e.data.mean_delta).toFixed(2)} · n=${num(e.data.n)}`;
    } else if (e.stage === "score_corrected") {
      detail = `${String(e.data.criterion)}: ${fmt1(e.data.from)}→${fmt1(e.data.to)}`;
      next.corrections = [
        ...state.corrections,
        {
          criterion: String(e.data.criterion),
          from: num(e.data.from),
          to: num(e.data.to),
        },
      ];
    }
    next.beats = [...state.beats, { stage: e.stage, detail }];
  }

  if (e.stage === "complete") next.done = true;
  return next;
}

export interface ScoreRow {
  id: string;
  label: string;
  score: number;
  /** Pre-audit native score (over-confident origin) — drives the ScoreBar ghost. */
  originScore: number;
  scale: number;
  weightPct: number;
  evidenceRefs: string[];
  audit: AuditCorrection | null;
}

/** Join the record's per-criterion scores with their rubric metadata (label, scale, weight). */
export function scoreRows(rec: RunRecord): ScoreRow[] {
  const byId = new Map(rec.rubric.criteria.map((c) => [c.id, c]));
  const preAudit = preAuditScoreMap(rec);
  return rec.scores.map((s) => {
    const c = byId.get(s.criterion_id);
    return {
      id: s.criterion_id,
      label: c?.label ?? s.criterion_id,
      score: s.score,
      originScore: preAudit[s.criterion_id] ?? s.score,
      scale: c?.scale ?? 5,
      weightPct: Math.round((c?.weight ?? 0) * 100),
      evidenceRefs: s.evidence_refs,
      audit: s.audit,
    };
  });
}

/** The lowest-scoring axis (by score fraction); the participant's iterate target. */
export function weakestAxis(rows: ScoreRow[]): ScoreRow | null {
  if (rows.length === 0) return null;
  return rows.reduce((lo, r) => (r.score / r.scale < lo.score / lo.scale ? r : lo));
}

export interface ConstellationNode extends Node3D {
  label: string;
  corrected: boolean;
  fromX: number; // pre-correction x, so corrected nodes animate into place
}

const clamp01 = (v: number): number => Math.max(0, Math.min(1, v));

/**
 * Project each scored criterion into the cube. x = score fraction, y = weight,
 * z = evidence depth (deeper when uncorrected). Corrected nodes carry a `fromX`
 * derived from their pre-correction (over-confident) hat score, so the graph
 * reshapes when results land.
 */
export function constellationNodes(rec: RunRecord): ConstellationNode[] {
  return scoreRows(rec).map((r) => {
    const scoreFrac = clamp01(r.score / r.scale);
    const node = projectCriterion({
      id: r.id,
      scoreFrac,
      weight: clamp01(r.weightPct / 100),
      evidenceDepth: r.audit ? 0.3 : 0.7,
    });
    let fromX = node.x;
    if (r.audit) {
      // Convert the hat-scale over-confidence (original − corrected) into native scale.
      const overFrac = ((r.audit.original - r.audit.corrected) / HAT_SCALE) * 1;
      fromX = clamp01(scoreFrac + overFrac) * 2 - 1;
    }
    return { ...node, label: r.label, corrected: r.audit != null, fromX };
  });
}
