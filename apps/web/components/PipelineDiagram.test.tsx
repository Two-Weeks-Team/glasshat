import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PIPELINE, PipelineDiagram } from "@/components/PipelineDiagram";

describe("PipelineDiagram", () => {
  it("renders every default pipeline step in order", () => {
    render(<PipelineDiagram />);
    const el = screen.getByTestId("pipeline-diagram");
    for (const step of PIPELINE) {
      expect(el).toHaveTextContent(step.title);
    }
    expect(el).toHaveTextContent("01");
    expect(el).toHaveTextContent("05");
  });
});
