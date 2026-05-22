import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EvidenceList } from "@/components/EvidenceList";

describe("EvidenceList", () => {
  it("lists each evidence ref", () => {
    render(<EvidenceList refs={["deck#2", "repo#7"]} />);
    const list = screen.getByTestId("evidence-list");
    expect(list).toHaveTextContent("deck#2");
    expect(list).toHaveTextContent("repo#7");
  });

  it("shows a hint when empty", () => {
    render(<EvidenceList refs={[]} />);
    expect(screen.getByTestId("evidence-empty")).toBeInTheDocument();
  });
});
