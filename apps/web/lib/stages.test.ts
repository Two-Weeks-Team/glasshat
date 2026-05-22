import { describe, expect, it } from "vitest";

import { AUDIT_BEATS, railIndexForStage, TIMELINE_STAGES } from "@/lib/stages";

describe("stages", () => {
  it("has seven ordered headline stages ending in complete", () => {
    expect(TIMELINE_STAGES).toHaveLength(7);
    expect(TIMELINE_STAGES[0].name).toBe("queued");
    expect(TIMELINE_STAGES[TIMELINE_STAGES.length - 1].name).toBe("complete");
  });

  it("maps a headline stage to its rail index", () => {
    expect(railIndexForStage("queued")).toBe(0);
    expect(railIndexForStage("hats_running")).toBe(3);
    expect(railIndexForStage("complete")).toBe(6);
  });

  it("maps every audit wow-beat onto the auditing node", () => {
    const auditing = railIndexForStage("auditing");
    for (const beat of AUDIT_BEATS) {
      expect(railIndexForStage(beat)).toBe(auditing);
    }
  });

  it("maps graph_reshape onto the scoring node (it fires after scoring)", () => {
    expect(railIndexForStage("graph_reshape")).toBe(railIndexForStage("scoring"));
  });
});
