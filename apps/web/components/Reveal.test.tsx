import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Reveal } from "@/components/Reveal";

describe("Reveal", () => {
  it("renders children inside a .reveal wrapper", () => {
    render(<Reveal>hello</Reveal>);
    const el = screen.getByTestId("reveal");
    expect(el).toHaveTextContent("hello");
    expect(el.className).toContain("reveal");
  });

  it("applies a stagger delay via animation-delay", () => {
    render(<Reveal delayMs={120}>x</Reveal>);
    expect(screen.getByTestId("reveal").style.animationDelay).toBe("120ms");
  });

  it("omits the delay style when zero", () => {
    render(<Reveal>x</Reveal>);
    expect(screen.getByTestId("reveal").style.animationDelay).toBe("");
  });
});
