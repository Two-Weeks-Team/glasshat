import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Badge } from "@/components/Badge";

describe("Badge", () => {
  it("renders children and a title", () => {
    render(
      <Badge tone="good" title="ok">
        live
      </Badge>,
    );
    const el = screen.getByTestId("badge");
    expect(el).toHaveTextContent("live");
    expect(el).toHaveAttribute("title", "ok");
  });
});
