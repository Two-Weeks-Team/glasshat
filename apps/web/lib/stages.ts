/**
 * Pipeline stage metadata for the live monitor.
 *
 * Mirrors `glasshat.pipeline.events.Stage`. The seven headline stages form the
 * timeline rail; the audit "wow-beats" are interleaved micro-events that drive
 * the self-correction callout and the 3D graph reshape.
 */

export type StageName =
  | "queued"
  | "ingesting"
  | "planning"
  | "hats_running"
  | "auditing"
  | "audit_started"
  | "inconsistency_flagged"
  | "phoenix_consultation"
  | "anchor_retrieval"
  | "score_corrected"
  | "scoring"
  | "graph_reshape"
  | "complete";

export interface StageMeta {
  name: StageName;
  label: string;
  blurb: string;
}

/** The ordered headline stages shown as the timeline rail. */
export const TIMELINE_STAGES: StageMeta[] = [
  { name: "queued", label: "Queued", blurb: "Run accepted" },
  { name: "ingesting", label: "Ingesting", blurb: "Chunk + embed the deck and repo" },
  { name: "planning", label: "Planning", blurb: "Synthesize the rubric, plan the hats" },
  { name: "hats_running", label: "6-Hat panel", blurb: "Each hat retrieves evidence and scores" },
  { name: "auditing", label: "Auditing", blurb: "Calibrate against past evaluations" },
  { name: "scoring", label: "Scoring", blurb: "Aggregate to the rubric's native scale" },
  { name: "complete", label: "Complete", blurb: "Immutable run record persisted" },
];

/** Human labels for the interleaved audit micro-events. */
export const WOW_BEATS: Record<string, string> = {
  audit_started: "Audit started",
  inconsistency_flagged: "Inconsistency flagged",
  phoenix_consultation: "Consulting the calibration prior for drift statistics",
  anchor_retrieval: "Retrieving calibrated anchors",
  score_corrected: "Score self-corrected",
  graph_reshape: "Reshaping the evaluation graph",
};

const RAIL_ORDER: StageName[] = TIMELINE_STAGES.map((s) => s.name);

/** Audit micro-events that visually belong to the "auditing" rail node. */
export const AUDIT_BEATS: StageName[] = [
  "audit_started",
  "inconsistency_flagged",
  "phoenix_consultation",
  "anchor_retrieval",
  "score_corrected",
];

/** Map any emitted stage onto its position in the headline rail. */
export function railIndexForStage(name: string): number {
  if (AUDIT_BEATS.includes(name as StageName)) return RAIL_ORDER.indexOf("auditing");
  if (name === "graph_reshape") return RAIL_ORDER.indexOf("scoring");
  return RAIL_ORDER.indexOf(name as StageName);
}
