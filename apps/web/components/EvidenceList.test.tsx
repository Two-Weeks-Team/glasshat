import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EvidenceList } from "@/components/EvidenceList";

describe("EvidenceList", () => {
  it("lists each evidence ref", () => {
    render(<EvidenceList refs={["deck-2", "repo:readme"]} />);
    const list = screen.getByTestId("evidence-list");
    expect(list).toHaveTextContent("deck-2");
    expect(list).toHaveTextContent("readme");
  });

  it("shows a hint when empty", () => {
    render(<EvidenceList refs={[]} />);
    expect(screen.getByTestId("evidence-empty")).toBeInTheDocument();
  });

  it("tags repo-sourced refs distinctly from deck quotes", () => {
    render(<EvidenceList refs={["deck-0", "repo:languages", "repo:facts"]} />);
    const refs = screen.getAllByTestId("evidence-ref");
    const kinds = refs.map((el) => el.getAttribute("data-kind"));
    expect(kinds).toEqual(["deck", "repo", "repo"]);
    // Repo chips strip the `repo:` prefix and show the facet label.
    const repoChip = refs.find((el) => el.getAttribute("data-kind") === "repo");
    expect(repoChip).toBeTruthy();
    expect(within(repoChip!).getByText("languages")).toBeInTheDocument();
    expect(within(repoChip!).getByText("repo")).toBeInTheDocument();
  });
});
