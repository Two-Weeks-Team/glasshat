import { describe, expect, it } from "vitest";

import type { RunRecord } from "@/lib/api";
import {
  constellationNodes,
  initialRunState,
  reduceEvent,
  scoreRows,
  weakestAxis,
  type RunState,
} from "@/lib/participate-state";
import type { SseEvent } from "@/lib/sse";

function fold(events: SseEvent[]): RunState {
  return events.reduce(reduceEvent, initialRunState);
}

describe("reduceEvent", () => {
  it("captures run_id, beats, corrections, and completion across a stream", () => {
    const state = fold([
      { stage: "queued", data: { run_id: "run-1" } },
      { stage: "ingesting", data: {} },
      { stage: "planning", data: { rubric_id: "r1" } },
      { stage: "hats_running", data: { hats: ["white", "yellow"] } },
      { stage: "auditing", data: {} },
      { stage: "audit_started", data: {} },
      { stage: "phoenix_consultation", data: { mean_delta: 1.74, n: 14 } },
      { stage: "score_corrected", data: { criterion: "design", from: 9, to: 7.2 } },
      { stage: "scoring", data: {} },
      { stage: "complete", data: { final_score: 54 } },
    ]);

    expect(state.runId).toBe("run-1");
    expect(state.done).toBe(true);
    expect(state.current).toBe("complete");
    expect(state.corrections).toEqual([{ criterion: "design", from: 9, to: 7.2 }]);
    // beats: audit_started, phoenix_consultation, score_corrected
    expect(state.beats.map((b) => b.stage)).toEqual([
      "audit_started",
      "phoenix_consultation",
      "score_corrected",
    ]);
    expect(state.beats[1].detail).toBe("Δ1.74 · n=14");
    expect(state.beats[2].detail).toBe("design: 9.0→7.2");
  });

  it("does not mutate the input state", () => {
    const before = { ...initialRunState };
    reduceEvent(initialRunState, { stage: "queued", data: { run_id: "x" } });
    expect(initialRunState).toEqual(before);
  });
});

const record: RunRecord = {
  run_id: "run-1",
  final_score: 54,
  mode: "participant",
  created_at: "2026-05-22T00:00:00Z",
  // A real RunRecord lists each correction in BOTH `audit_corrections` (drives
  // the 2D ScoreBar ghost via preAuditScoreMap) and the matching score's `audit`
  // (the 3D origin now reads the same aggregate — see L3 in participate-state).
  audit_corrections: [
    {
      hat: "yellow",
      criterion_id: "design",
      original: 9,
      corrected: 5,
      mean_delta: 1.7,
      n: 14,
      reason: "optimism",
    },
  ],
  scores: [
    { criterion_id: "tech", score: 4, evidence_refs: ["deck#1"], audit: null },
    {
      criterion_id: "design",
      score: 2,
      evidence_refs: [],
      audit: {
        hat: "yellow",
        criterion_id: "design",
        original: 9,
        corrected: 5,
        mean_delta: 1.7,
        n: 14,
        reason: "optimism",
      },
    },
  ],
  rubric: {
    schema_version: "1.0",
    rubric_id: "r1",
    rubric_schema_hash: "h",
    source: { type: "preset", identifier: "rapid-agent", fetched_at: null, source_text_excerpt: "" },
    scoring_rule: { aggregation: "weighted_sum", final_scale: "0-100" },
    criteria: [
      {
        id: "tech",
        label: "Technological Implementation",
        weight: 0.25,
        scale: 5,
        bmad_mapping: ["B1"],
        descriptor_levels: { "1": "a", "2": "b", "3": "c", "4": "d", "5": "e" },
        evidence_required: true,
        source_clause: "",
        source_excerpt: "",
      },
      {
        id: "design",
        label: "Design",
        weight: 0.25,
        scale: 5,
        bmad_mapping: ["D1"],
        descriptor_levels: { "1": "a", "2": "b", "3": "c", "4": "d", "5": "e" },
        evidence_required: true,
        source_clause: "",
        source_excerpt: "",
      },
    ],
    tie_breakers: [],
    weights_vector: [0.25, 0.25],
    confidence: 1,
    warnings: [],
  },
};

describe("scoreRows", () => {
  it("joins scores with rubric label/scale/weight", () => {
    const rows = scoreRows(record);
    expect(rows[0]).toMatchObject({ label: "Technological Implementation", scale: 5, weightPct: 25 });
    expect(rows[1].audit?.original).toBe(9);
  });
});

describe("weakestAxis", () => {
  it("returns the lowest score fraction", () => {
    expect(weakestAxis(scoreRows(record))?.id).toBe("design");
  });

  it("handles an empty list", () => {
    expect(weakestAxis([])).toBeNull();
  });
});

describe("constellationNodes", () => {
  it("flags corrected nodes and places their pre-correction origin to the right", () => {
    const nodes = constellationNodes(record);
    const design = nodes.find((n) => n.label === "Design")!;
    expect(design.corrected).toBe(true);
    // corrected DOWN → final x is left of the over-confident origin
    expect(design.x).toBeLessThan(design.fromX);
    const tech = nodes.find((n) => n.label === "Technological Implementation")!;
    expect(tech.corrected).toBe(false);
    expect(tech.fromX).toBe(tech.x);
  });
});
