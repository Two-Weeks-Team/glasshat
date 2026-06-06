import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ProofReceipt } from "@/components/ProofReceipt";
import { SAMPLE_COHORT } from "@/lib/sample-cohort";

const record = SAMPLE_COHORT[0].record;

describe("ProofReceipt", () => {
  it("renders the run id from the record", () => {
    render(<ProofReceipt record={record} />);
    expect(screen.getByTestId("receipt-run-id")).toHaveTextContent(record.run_id);
  });

  it("shows live counts derived from the record", () => {
    render(<ProofReceipt record={record} />);
    const liveGroup = screen.getByTestId("receipt-group-live");
    expect(liveGroup).toHaveTextContent(String(record.audit_corrections.length));
    expect(liveGroup).toHaveTextContent(String(record.rubric.criteria.length));
  });

  it("labels deployment config statically with the live model", () => {
    render(<ProofReceipt record={record} />);
    const staticGroup = screen.getByTestId("receipt-group-static");
    expect(within(staticGroup).getByText("gemini-3.1-flash-lite")).toBeInTheDocument();
    expect(staticGroup).toHaveTextContent("phoenix-mcp");
  });

  it("has a copy control for the run id", () => {
    render(<ProofReceipt record={record} />);
    expect(screen.getByRole("button", { name: /copy/i })).toBeInTheDocument();
  });
});
