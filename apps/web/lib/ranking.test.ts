import { describe, expect, it } from "vitest";

import type { AuditCorrection, Criterion, RunRecord, SynthesizedRubric } from "@/lib/api";
import {
  finalScoreFrom,
  preAuditFinalScore,
  preAuditScoreMap,
  rankSubmissions,
  rankSubmissionsPreAudit,
  topKHitRate,
} from "@/lib/ranking";

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

// --- Improvement B: rank-flip primitives ------------------------------------

function withCorrection(rec: RunRecord, correction: AuditCorrection): RunRecord {
  return { ...rec, audit_corrections: [...rec.audit_corrections, correction] };
}

const yellowCorrection = (criterion_id: string, original: number, corrected: number): AuditCorrection => ({
  hat: "yellow",
  criterion_id,
  original,
  corrected,
  mean_delta: 1.45,
  n: 7,
  reason: `yellow over/under-confident on '${criterion_id}' (evidence=low, mean_delta=+1.45, n=7)`,
});

describe("preAuditScoreMap", () => {
  it("equals the audited scores when no corrections were applied", () => {
    const rec = record({ tech: 3, design: 3, impact: 3, idea: 3 });
    expect(preAuditScoreMap(rec)).toEqual({ tech: 3, design: 3, impact: 3, idea: 3 });
  });

  it("adds back the per-hat shift on the criterion that was corrected", () => {
    // YELLOW was 9.0, pulled to 7.84 → per-hat shift = (9.0 - 7.84) / 6 = 0.193…
    // audited internal for tech=3 is (3 - 1) * 10 / (5 - 1) = 5.0
    // pre-audit internal ≈ 5.193, native ≈ 1 + 5.193/10 * 4 ≈ 3.0773
    const rec = withCorrection(
      record({ tech: 3, design: 3, impact: 3, idea: 3 }),
      yellowCorrection("tech", 9.0, 7.84),
    );
    const pre = preAuditScoreMap(rec);
    expect(pre.tech).toBeGreaterThan(3);
    expect(pre.tech).toBeCloseTo(3.0773, 3);
    // Untouched criteria stay equal to the audited score.
    expect(pre.design).toBe(3);
  });
});

describe("preAuditFinalScore", () => {
  it("reads pre_audit_final_score from the record when present (non-zero)", () => {
    const rec = { ...record({ tech: 3, design: 3, impact: 3, idea: 3 }), pre_audit_final_score: 88.5 };
    expect(preAuditFinalScore(rec)).toBe(88.5);
  });

  it("reconstructs from corrections when the field is absent (legacy cache)", () => {
    const rec = withCorrection(
      record({ tech: 3, design: 3, impact: 3, idea: 3 }),
      yellowCorrection("tech", 9.0, 7.84),
    );
    const expected = finalScoreFrom(rec.rubric, preAuditScoreMap(rec));
    expect(preAuditFinalScore(rec)).toBe(expected);
    // The reconstructed pre-audit final is strictly greater than the audited
    // final whenever YELLOW was pulled down — that's the rank-flip claim.
    expect(preAuditFinalScore(rec)).toBeGreaterThan(rec.final_score);
  });
});

describe("rankSubmissionsPreAudit", () => {
  it("can rank a winner *behind* the audited winner when the audit lifts the loser", () => {
    // Project A had every criterion's YELLOW pulled hard from 9 → 1 (delta 8);
    // per-criterion per-hat shift = 8 / 6 ≈ 1.33 internal → pre-audit native
    // ≈ 3.53 per criterion → pre-audit final ≈ 70.7. Project B had no
    // corrections and an audited final of 68.0. So B wins the audited rank,
    // A wins the pre-audit rank — the canonical rank flip.
    const auditedA = record({ tech: 3, design: 3, impact: 3, idea: 3 });
    const a: RunRecord = {
      ...auditedA,
      audit_corrections: [
        yellowCorrection("tech", 9.0, 1.0),
        yellowCorrection("design", 9.0, 1.0),
        yellowCorrection("impact", 9.0, 1.0),
        yellowCorrection("idea", 9.0, 1.0),
      ],
    };
    const b = record({ tech: 3.4, design: 3.4, impact: 3.4, idea: 3.4 });
    const audited = rankSubmissions([
      { label: "A", record: a },
      { label: "B", record: b },
    ]);
    const preAudited = rankSubmissionsPreAudit([
      { label: "A", record: a },
      { label: "B", record: b },
    ]);
    expect(audited[0].label).toBe("B"); // post-audit: B wins
    expect(preAudited[0].label).toBe("A"); // pre-audit: A would have won
  });

  it("matches `rankSubmissions` when no corrections exist", () => {
    const items = [
      { label: "a", record: record({ tech: 5, design: 5, impact: 5, idea: 5 }) },
      { label: "b", record: record({ tech: 4, design: 4, impact: 4, idea: 4 }) },
    ];
    const auditedOrder = rankSubmissions(items).map((r) => r.label);
    const preOrder = rankSubmissionsPreAudit(items).map((r) => r.label);
    expect(preOrder).toEqual(auditedOrder);
  });

  it("ignores gate-2 overrides (pre-audit is the raw agent verdict)", () => {
    // Even with a heavy override that re-ranks the audited view, the pre-audit
    // ranking must reflect the agent's raw consensus on the original scores.
    const top = record({ tech: 5, design: 5, impact: 5, idea: 5 });
    const other = record({ tech: 4, design: 4, impact: 4, idea: 4 });
    const items = [
      { label: "top", record: top, overrides: { tech: 1, design: 1, impact: 1, idea: 1 } },
      { label: "other", record: other },
    ];
    const audited = rankSubmissions(items);
    const pre = rankSubmissionsPreAudit(items);
    expect(audited[0].label).toBe("other"); // override moved "top" down
    expect(pre[0].label).toBe("top"); // raw agent verdict unchanged
  });
});
