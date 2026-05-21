import { describe, expect, it } from "vitest";

import { projectCriterion, reshapeOnCorrection } from "@/lib/projection";

describe("projection", () => {
  it("maps score fraction onto x in [-1, 1]", () => {
    const f = { weight: 0.5, evidenceDepth: 0.5 };
    expect(projectCriterion({ id: "a", scoreFrac: 1, ...f }).x).toBe(1);
    expect(projectCriterion({ id: "a", scoreFrac: 0, ...f }).x).toBe(-1);
    expect(projectCriterion({ id: "a", scoreFrac: 0.5, ...f }).x).toBe(0);
  });

  it("clamps out-of-range inputs", () => {
    expect(projectCriterion({ id: "a", scoreFrac: 2, weight: 0.5, evidenceDepth: 0.5 }).x).toBe(1);
  });

  it("reshapes lower when a score self-corrects down", () => {
    const f = { id: "a", scoreFrac: 1, weight: 0.5, evidenceDepth: 0.3 };
    const before = projectCriterion(f).x;
    const after = reshapeOnCorrection(f, 0.76).x;
    expect(after).toBeLessThan(before);
  });
});
