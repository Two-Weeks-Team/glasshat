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

  it("marks the four core pillars live and Phoenix MCP as wired", () => {
    render(<ProofStrip />);
    for (const id of ["gemini", "adk", "cloudrun", "arize"]) {
      expect(screen.getByTestId(`proof-chip-${id}`)).toHaveAttribute("data-state", "live");
    }
    const mcp = screen.getByTestId("proof-chip-phoenixmcp");
    expect(mcp).toHaveAttribute("data-state", "wired");
    // Honesty: the Phoenix MCP chip must not claim "live".
    expect(mcp).toHaveAccessibleName(/wired/i);
  });

  it("shows the live model on the Gemini chip", () => {
    render(<ProofStrip />);
    expect(screen.getByTestId("proof-chip-gemini")).toHaveTextContent("3.1-flash-lite");
  });
});
