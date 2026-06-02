import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScoreBar } from "@/components/ScoreBar";

describe("ScoreBar", () => {
  it("renders the label, corrected flag, and fill width", () => {
    render(<ScoreBar label="Tech" score={4} max={5} corrected />);
    expect(screen.getByText("Tech")).toBeInTheDocument();
    expect(screen.getByText(/self-corrected/)).toBeInTheDocument();
    expect(screen.getByTestId("score-bar-fill").style.width).toBe("80%");
  });

  it("draws a ghost-origin when the audit pulled the score down", () => {
    render(<ScoreBar label="Tech" score={3.5} max={5} corrected originScore={4.5} />);
    const ghost = screen.getByTestId("score-bar-ghost");
    expect(ghost.style.width).toBe("90%"); // origin 4.5/5
    expect(screen.getByTestId("score-bar-fill").style.width).toBe("70%"); // audited 3.5/5
    // The struck-through origin value is shown alongside the audited value.
    expect(screen.getByText("4.5")).toBeInTheDocument();
  });

  it("omits the ghost when there was no downward correction", () => {
    render(<ScoreBar label="Tech" score={4} max={5} originScore={4} />);
    expect(screen.queryByTestId("score-bar-ghost")).toBeNull();
  });
});
