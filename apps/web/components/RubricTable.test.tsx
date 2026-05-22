import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RubricTable } from "@/components/RubricTable";
import type { SynthesizedRubric } from "@/lib/api";

const rubric: SynthesizedRubric = {
  schema_version: "1.0",
  rubric_id: "r1",
  rubric_schema_hash: "abc",
  source: { type: "preset", identifier: "rapid-agent", fetched_at: null, source_text_excerpt: "" },
  scoring_rule: { aggregation: "weighted_sum", final_scale: "0-100" },
  criteria: [
    {
      id: "tech-implementation",
      label: "Technological Implementation",
      weight: 0.25,
      scale: 5,
      bmad_mapping: ["B1", "C2"],
      descriptor_levels: { "1": "a", "2": "b", "3": "c", "4": "d", "5": "e" },
      evidence_required: true,
      source_clause: "criterion 1 of 4",
      source_excerpt: "",
    },
  ],
  tie_breakers: [{ order: 1, criterion_id: "tech-implementation" }],
  weights_vector: [0.25],
  confidence: 1,
  warnings: [],
};

describe("RubricTable", () => {
  it("renders criterion label, weight %, scale, BMAD codes, and tie-break order", () => {
    render(<RubricTable rubric={rubric} />);
    const el = screen.getByTestId("rubric-table");
    expect(el).toHaveTextContent("Technological Implementation");
    expect(el).toHaveTextContent("25%");
    expect(el).toHaveTextContent("1–5");
    expect(el).toHaveTextContent("B1");
    expect(el).toHaveTextContent("C2");
    expect(el).toHaveTextContent("rapid-agent");
    expect(el).toHaveTextContent("weighted_sum");
  });
});
