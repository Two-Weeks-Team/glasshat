import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatCard } from "@/components/StatCard";

describe("StatCard", () => {
  it("shows label, value, and optional sub", () => {
    render(<StatCard label="Final" value="54.0" sub="out of 100" />);
    expect(screen.getByText("Final")).toBeInTheDocument();
    expect(screen.getByText("54.0")).toBeInTheDocument();
    expect(screen.getByText("out of 100")).toBeInTheDocument();
  });

  it("omits sub when not provided", () => {
    render(<StatCard label="Runs" value={3} />);
    expect(screen.getByTestId("stat-card")).toHaveTextContent("Runs");
  });
});
