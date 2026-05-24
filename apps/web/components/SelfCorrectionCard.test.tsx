import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SelfCorrectionCard } from "@/components/SelfCorrectionCard";
import type { AuditCorrection } from "@/lib/api";

const lowered: AuditCorrection = {
  hat: "yellow",
  criterion_id: "design",
  original: 9,
  corrected: 7.8,
  mean_delta: 1.5,
  n: 12,
  reason: "optimism bias vs calibrated anchors",
};

describe("SelfCorrectionCard", () => {
  it("shows the hat, original, corrected, delta, basis, and reason", () => {
    render(<SelfCorrectionCard correction={lowered} />);
    const card = screen.getByTestId("self-correction-card");
    expect(card).toHaveAttribute("data-direction", "lowered");
    expect(card).toHaveTextContent(/yellow/i);
    expect(card).toHaveTextContent("9.0");
    expect(card).toHaveTextContent("7.8");
    expect(card).toHaveTextContent("-1.20");
    expect(card).toHaveTextContent("12 past evaluations");
    expect(card).toHaveTextContent("calibrated prior");
    expect(card).toHaveTextContent("optimism bias vs calibrated anchors");
  });

  it("states the audit-the-auditor message in-line (not hidden)", () => {
    render(<SelfCorrectionCard correction={lowered} />);
    expect(screen.getByTestId("self-correction-card")).toHaveTextContent(
      /catches its own over-confidence and corrects the score before the judge locks it/i,
    );
  });

  it("renders the correction bar", () => {
    render(<SelfCorrectionCard correction={lowered} />);
    expect(screen.getByTestId("correction-bar")).toBeInTheDocument();
  });
});
