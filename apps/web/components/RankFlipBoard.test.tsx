import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RankFlipBoard } from "@/components/RankFlipBoard";
import type { AuditCorrection, Criterion, RunRecord, SynthesizedRubric } from "@/lib/api";
import { finalScoreFrom } from "@/lib/ranking";

const crit = (id: string): Criterion => ({
  id,
  label: id,
  weight: 0.25,
  scale: 5,
  bmad_mapping: ["B1"],
  descriptor_levels: { "1": "a", "2": "b", "3": "c", "4": "d", "5": "e" },
  evidence_required: true,
  source_clause: "",
  source_excerpt: "",
});

const rubric: SynthesizedRubric = {
  schema_version: "1.0",
  rubric_id: "r",
  rubric_schema_hash: "h",
  source: { type: "preset", identifier: "rapid-agent", fetched_at: null, source_text_excerpt: "" },
  scoring_rule: { aggregation: "weighted_sum", final_scale: "0-100" },
  criteria: [crit("tech"), crit("design"), crit("impact"), crit("idea")],
  tie_breakers: [
    { order: 1, criterion_id: "tech" },
    { order: 2, criterion_id: "design" },
  ],
  weights_vector: [0.25, 0.25, 0.25, 0.25],
  confidence: 1,
  warnings: [],
};

const yellowCorrection = (criterion_id: string, original: number, corrected: number): AuditCorrection => ({
  hat: "yellow",
  criterion_id,
  original,
  corrected,
  mean_delta: 1.45,
  n: 7,
  reason: `yellow (evidence=low, mean_delta=+1.45, n=7)`,
});

function record(scores: Record<string, number>, corrections: AuditCorrection[] = []): RunRecord {
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
    audit_corrections: corrections,
    mode: "judge",
    created_at: "",
  };
}

describe("RankFlipBoard", () => {
  it("renders nothing for a single-item cohort (no rank story to tell)", () => {
    const { container } = render(
      <RankFlipBoard
        items={[{ label: "Solo", record: record({ tech: 3, design: 3, impact: 3, idea: 3 }) }]}
      />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders two columns of rows when the cohort has >= 2 items", () => {
    render(
      <RankFlipBoard
        items={[
          { label: "A", record: record({ tech: 5, design: 5, impact: 5, idea: 5 }) },
          { label: "B", record: record({ tech: 3, design: 3, impact: 3, idea: 3 }) },
        ]}
      />,
    );
    const board = screen.getByTestId("rank-flip-board");
    // 2 items × 2 columns = 4 rows.
    expect(within(board).getAllByTestId("rank-flip-row")).toHaveLength(4);
  });

  it("highlights the row whose rank flips after the audit", () => {
    // A was the raw-consensus winner (heavy YELLOW corrections), B is the
    // audited winner — exactly the rank-flip the demo claims.
    const a = record(
      { tech: 3, design: 3, impact: 3, idea: 3 },
      [
        // delta=8 per criterion → per-hat shift ≈ 1.33 internal → A's
        // pre-audit final ≈ 70.7 vs B's 68.0; rank flips on the audit.
        yellowCorrection("tech", 9.0, 1.0),
        yellowCorrection("design", 9.0, 1.0),
        yellowCorrection("impact", 9.0, 1.0),
        yellowCorrection("idea", 9.0, 1.0),
      ],
    );
    const b = record({ tech: 3.4, design: 3.4, impact: 3.4, idea: 3.4 });
    render(
      <RankFlipBoard
        items={[
          { label: "A", record: a },
          { label: "B", record: b },
        ]}
      />,
    );
    const board = screen.getByTestId("rank-flip-board");

    // Audit moved exactly two positions (A and B swapped).
    expect(within(board).getByTestId("badge")).toHaveTextContent("audit moved 2 of 2 positions");

    // Right (audited) column: B@1 promoted, A@2 demoted.
    const indicators = within(board).getAllByTestId("rank-flip-indicator");
    expect(indicators.length).toBeGreaterThan(0);
    const upOnRight = indicators.find((el) => el.textContent === "↑1");
    const downOnRight = indicators.find((el) => el.textContent === "↓1");
    expect(upOnRight).toBeTruthy();
    expect(downOnRight).toBeTruthy();
  });

  it("reports 'no rank change' when the audit doesn't reorder anything", () => {
    render(
      <RankFlipBoard
        items={[
          { label: "A", record: record({ tech: 5, design: 5, impact: 5, idea: 5 }) },
          { label: "B", record: record({ tech: 3, design: 3, impact: 3, idea: 3 }) },
        ]}
      />,
    );
    const board = screen.getByTestId("rank-flip-board");
    expect(within(board).getByTestId("badge")).toHaveTextContent("no rank change");
    // No indicators rendered when nothing flipped.
    expect(within(board).queryAllByTestId("rank-flip-indicator")).toHaveLength(0);
  });
});
