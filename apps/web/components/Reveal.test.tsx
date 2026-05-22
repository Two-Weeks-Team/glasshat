import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Reveal } from "@/components/Reveal";

describe("Reveal", () => {
  it("renders children and the reveal class", () => {
    render(<Reveal>hello</Reveal>);
    const el = screen.getByTestId("reveal");
    expect(el).toHaveTextContent("hello");
    expect(el.className).toContain("reveal");
  });

  it("becomes visible when IntersectionObserver is unavailable (fallback)", () => {
    // jsdom has no IntersectionObserver → component falls back to visible.
    render(<Reveal>content</Reveal>);
    expect(screen.getByTestId("reveal").className).toContain("is-visible");
  });

  it("applies a stagger delay", () => {
    render(<Reveal delayMs={120}>x</Reveal>);
    expect(screen.getByTestId("reveal").style.transitionDelay).toBe("120ms");
  });
});
