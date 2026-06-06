import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ProofStrip } from "@/components/ProofStrip";

describe("ProofStrip", () => {
  it("renders all five stack-proof chips", () => {
    render(<ProofStrip />);
    const strip = screen.getByTestId("proof-strip");
    for (const id of ["gemini", "adk", "cloudrun", "arize", "phoenixmcp"]) {
      expect(within(strip).getByTestId(`proof-chip-${id}`)).toBeInTheDocument();
    }
  });

  it("marks all five pillars live (incl. the live Phoenix-MCP loop)", () => {
    render(<ProofStrip />);
    for (const id of ["gemini", "adk", "cloudrun", "arize", "phoenixmcp"]) {
      expect(screen.getByTestId(`proof-chip-${id}`)).toHaveAttribute("data-state", "live");
    }
    // The Phoenix MCP chip is live: the deployed audit reads + writes the
    // calibration dataset over MCP per request (verified against prod).
    const mcp = screen.getByTestId("proof-chip-phoenixmcp");
    expect(mcp).toHaveAccessibleName(/live/i);
  });

  it("shows the live model on the Gemini chip", () => {
    render(<ProofStrip />);
    expect(screen.getByTestId("proof-chip-gemini")).toHaveTextContent("3.1-flash-lite");
  });
});
