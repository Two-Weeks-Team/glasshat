import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AuditCallout } from "@/components/AuditCallout";
import type { AuditCorrection } from "@/lib/api";

const base: AuditCorrection = {
  hat: "yellow",
  criterion_id: "tech-implementation",
  original: 9,
  corrected: 7.2,
  mean_delta: 1.74,
  n: 14,
  reason: "optimism bias vs calibrated anchors",
};

describe("AuditCallout", () => {
  it("renders the hat, criterion, score delta, and basis", () => {
    render(<AuditCallout correction={base} />);
    const el = screen.getByTestId("audit-callout");
    expect(el).toHaveTextContent("yellow hat");
    expect(el).toHaveTextContent("tech-implementation");
    expect(el).toHaveTextContent("9.0");
    expect(el).toHaveTextContent("7.2");
    expect(el).toHaveTextContent("14 past evaluations");
    expect(el).toHaveTextContent("lowered");
  });

  it("uses singular phrasing for a single past evaluation", () => {
    render(<AuditCallout correction={{ ...base, n: 1, corrected: 9.5 }} />);
    expect(screen.getByTestId("audit-callout")).toHaveTextContent("1 past evaluation");
    expect(screen.getByTestId("audit-callout")).toHaveTextContent("raised");
  });
});
