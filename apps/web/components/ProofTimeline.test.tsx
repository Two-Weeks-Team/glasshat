import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { activeIndex, ProofTimeline } from "@/components/ProofTimeline";

describe("activeIndex", () => {
  it("maps stages onto the pipeline node index", () => {
    expect(activeIndex("queued", false)).toBe(0);
    expect(activeIndex("hats_running", false)).toBe(3);
    expect(activeIndex("phoenix_consultation", false)).toBe(4);
    expect(activeIndex("scoring", false)).toBe(5);
  });

  it("returns all-done past the last node when done, and idle when no stage", () => {
    expect(activeIndex(undefined, true)).toBe(6);
    expect(activeIndex(undefined, false)).toBe(-1);
  });
});

describe("ProofTimeline", () => {
  it("renders every agent node, the Arize rail, and the Phoenix MCP path", () => {
    render(<ProofTimeline done />);
    for (const id of ["input", "rubric", "planner", "panel", "audit", "score"]) {
      expect(screen.getByTestId(`timeline-node-${id}`)).toBeInTheDocument();
    }
    expect(screen.getByTestId("arize-rail")).toBeInTheDocument();
    expect(screen.getByTestId("phoenix-mcp-path")).toBeInTheDocument();
  });

  it("shows the audit correction as a before → after movement when complete", () => {
    render(
      <ProofTimeline done correction={{ label: "yellow hat · design", from: 9, to: 7.8 }} />,
    );
    const delta = screen.getByTestId("timeline-correction");
    expect(delta).toHaveTextContent("9.0");
    expect(delta).toHaveTextContent("7.8");
  });

  it("activates the Arize rail and Phoenix MCP path during consultation", () => {
    render(<ProofTimeline stage="phoenix_consultation" />);
    expect(screen.getByTestId("arize-rail")).toHaveAttribute("data-live", "true");
    expect(screen.getByTestId("phoenix-mcp-path")).toHaveAttribute("data-active", "true");
  });

  it("marks earlier nodes done and the current node active during a run", () => {
    render(<ProofTimeline stage="hats_running" />);
    expect(screen.getByTestId("timeline-node-input")).toHaveAttribute("data-state", "done");
    expect(screen.getByTestId("timeline-node-panel")).toHaveAttribute("data-state", "active");
    expect(screen.getByTestId("timeline-node-score")).toHaveAttribute("data-state", "pending");
  });
});
