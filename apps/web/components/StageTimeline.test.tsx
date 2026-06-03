import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StageTimeline } from "@/components/StageTimeline";

describe("StageTimeline", () => {
  it("marks earlier stages done and the current one active", () => {
    render(<StageTimeline current="hats_running" />);
    const tl = screen.getByTestId("stage-timeline");
    const active = tl.querySelectorAll('[data-state="active"]');
    expect(active).toHaveLength(1);
    expect(active[0]).toHaveTextContent("6-Hat panel");
    expect(tl.querySelectorAll('[data-state="done"]').length).toBe(3); // queued, ingesting, planning
  });

  it("maps audit wow-beats onto the auditing rail node", () => {
    render(<StageTimeline current="phoenix_consultation" />);
    const active = screen
      .getByTestId("stage-timeline")
      .querySelector('[data-state="active"]');
    expect(active).toHaveTextContent("Auditing");
  });

  it("renders the wow-beat ticker with human labels", () => {
    render(
      <StageTimeline
        current="auditing"
        beats={[{ stage: "phoenix_consultation" }, { stage: "score_corrected", detail: "9.0→7.2" }]}
      />,
    );
    const log = screen.getByTestId("beat-log");
    expect(log).toHaveTextContent("Consulting the calibration prior for drift statistics");
    expect(log).toHaveTextContent("Score self-corrected");
    expect(log).toHaveTextContent("9.0→7.2");
  });

  it("forces all nodes done when complete", () => {
    render(<StageTimeline current="complete" done />);
    expect(
      screen.getByTestId("stage-timeline").querySelectorAll('[data-state="done"]').length,
    ).toBe(7);
  });
});
