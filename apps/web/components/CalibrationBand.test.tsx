import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CalibrationBand } from "@/components/CalibrationBand";

describe("CalibrationBand", () => {
  it("renders hit@k before/after, the audit effect, and the honesty caveat", () => {
    render(<CalibrationBand />);
    // "hit@13" appears in both the heading and the caveat — assert at least one.
    expect(screen.getAllByText(/hit@13/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/before audit/i)).toBeInTheDocument();
    expect(screen.getByText(/after audit/i)).toBeInTheDocument();
    expect(screen.getByText(/audit effect/i)).toBeInTheDocument();
    // The non-negotiable honesty disclaimer must be on screen.
    expect(screen.getByText(/not a rank curve/i)).toBeInTheDocument();
    expect(screen.getAllByText(/backend=mock/i).length).toBeGreaterThan(0);
    // The committed result has delta=0; it must read as "no change", not "+0 pts".
    expect(screen.getByText(/no change/i)).toBeInTheDocument();
    expect(screen.queryByText(/\+0 pts/i)).toBeNull();
  });
});
