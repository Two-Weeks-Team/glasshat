import { describe, expect, it } from "vitest";

import type { Criterion, RunRecord, SynthesizedRubric } from "@/lib/api";
import { finalScoreFrom, rankSubmissions, topKHitRate } from "@/lib/ranking";

const crit = (id: string, weight: number): Criterion => ({
  id,
  label: id,
  weight,
  scale: 5,
  bmad_mapping: ["B1"],
  descriptor_levels: { "1": "a", "2": "b", "3": "c", "4": "d", "5": "e" },
  evidence_required: true,
  source_clause: "",
  source_excerpt: "",
});

const rubric: SynthesizedRubric = {
  schema_version: "1.0",
  rubric_id: "r1",
  rubric_schema_hash: "h",
  source: { type: "preset", identifier: "rapid-agent", fetched_at: null, source_text_excerpt: "" },
  scoring_rule: { aggregation: "weighted_sum", final_scale: "0-100" },
  criteria: [crit("tech", 0.25), crit("design", 0.25), crit("impact", 0.25), crit("idea", 0.25)],
  tie_breakers: [
    { order: 1, criterion_id: "tech" },
    { order: 2, criterion_id: "design" },
  ],
  weights_vector: [0.25, 0.25, 0.25, 0.25],
  confidence: 1,
  warnings: [],
};

function record(scores: Record<string, number>): RunRecord {
  return {
    run_id: Math.random().toString(36).slice(2),
    rubric,
    final_score: finalScoreFrom(rubric, scores),
    scores: Object.entries(scores).map(([criterion_id, score]) => ({
      criterion_id,
      score,
      evidence_refs: [],
      audit: null,
    })),
    audit_corrections: [],
    mode: "judge",
    created_at: "",
  };
}

describe("finalScoreFrom", () => {
  it("projects equal-weight fractions onto the display scale", () => {
    expect(finalScoreFrom(rubric, { tech: 5, design: 5, impact: 5, idea: 5 })).toBe(100);
    expect(finalScoreFrom(rubric, { tech: 3, design: 3, impact: 3, idea: 3 })).toBe(60);
  });
});

describe("rankSubmissions", () => {
  it("orders by effective final descending", () => {
    const ranked = rankSubmissions([
      { label: "low", record: record({ tech: 2, design: 2, impact: 2, idea: 2 }) },
      { label: "high", record: record({ tech: 5, design: 5, impact: 5, idea: 5 }) },
    ]);
    expect(ranked.map((r) => r.label)).toEqual(["high", "low"]);
    expect(ranked[0].rank).toBe(1);
  });

  it("breaks ties by the ordered tie-break chain (tech before design)", () => {
    // Same final (both average 3.0) but A wins on tech, B wins on design.
    const a = record({ tech: 4, design: 2, impact: 3, idea: 3 });
    const b = record({ tech: 2, design: 4, impact: 3, idea: 3 });
    const ranked = rankSubmissions([
      { label: "B", record: b },
      { label: "A", record: a },
    ]);
    expect(ranked[0].label).toBe("A"); // higher tech breaks the tie first
  });

  it("re-ranks when a gate-2 override changes a criterion score", () => {
    const top = record({ tech: 5, design: 5, impact: 5, idea: 5 });
    const other = record({ tech: 4, design: 4, impact: 4, idea: 4 });
    const ranked = rankSubmissions([
      { label: "top", record: top, overrides: { tech: 1, design: 1, impact: 1, idea: 1 } },
      { label: "other", record: other },
    ]);
    expect(ranked[0].label).toBe("other"); // override dropped "top" below "other"
  });
});

describe("topKHitRate", () => {
  it("scores predicted top-K against marked winners", () => {
    const ranked = rankSubmissions([
      { label: "a", record: record({ tech: 5, design: 5, impact: 5, idea: 5 }) },
      { label: "b", record: record({ tech: 4, design: 4, impact: 4, idea: 4 }) },
      { label: "c", record: record({ tech: 1, design: 1, impact: 1, idea: 1 }) },
    ]);
    expect(topKHitRate(ranked, new Set(["a", "b"]), 2)).toBe(1);
    expect(topKHitRate(ranked, new Set(["a", "c"]), 2)).toBe(0.5);
    expect(topKHitRate(ranked, new Set(), 2)).toBe(0);
  });
});
