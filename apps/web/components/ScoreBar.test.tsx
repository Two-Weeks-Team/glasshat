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
});
