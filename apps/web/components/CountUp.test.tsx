import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CountUp } from "@/components/CountUp";

describe("CountUp", () => {
  it("renders the value at the requested precision (reduced-motion/jsdom path)", () => {
    // jsdom has no matchMedia → component renders the final value immediately.
    render(<CountUp value={58.27} decimals={1} />);
    expect(screen.getByTestId("countup")).toHaveTextContent("58.3");
  });

  it("honors decimals", () => {
    render(<CountUp value={100} decimals={0} />);
    expect(screen.getByTestId("countup")).toHaveTextContent("100");
  });
});
