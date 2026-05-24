"use client";

import { useState } from "react";

import type { RunRecord } from "@/lib/api";
import { DEPLOYMENT_META } from "@/lib/deployment";

export interface ProofReceiptProps {
  record: RunRecord;
  /** True when the record is the cached sample rather than a fresh live run. */
  sample?: boolean;
}

interface Field {
  k: string;
  v: string;
  mono?: boolean;
}

/**
 * Post-run proof receipt. Honest by construction: "live" fields come from this
 * run's RunRecord (verifiable per run); "config" fields are the deployment's
 * static settings (infra/deploy.sh), surfaced via lib/deployment.ts. No API
 * change required. The run id is copyable for cross-checking against Arize AX.
 */
export function ProofReceipt({ record, sample = false }: ProofReceiptProps) {
  const [copied, setCopied] = useState(false);

  const copyRunId = async () => {
    try {
      await navigator.clipboard.writeText(record.run_id);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable — the id is still selectable on screen */
    }
  };

  const live: Field[] = [
    { k: "final score", v: record.final_score.toFixed(2) },
    { k: "corrections", v: String(record.audit_corrections.length) },
    { k: "criteria", v: String(record.rubric.criteria.length) },
    { k: "mode", v: record.mode },
    { k: "timestamp", v: record.created_at, mono: true },
  ];
  const config: Field[] = [
    { k: "model", v: DEPLOYMENT_META.modelFamily, mono: true },
    { k: "tracer", v: DEPLOYMENT_META.tracerBackend },
    { k: "deployment", v: DEPLOYMENT_META.deploymentTarget },
    { k: "consultant", v: DEPLOYMENT_META.consultantMode },
  ];

  return (
    <div data-testid="proof-receipt" className="elevate rounded-2xl p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-medium">Proof receipt</h2>
        <span className="text-xs text-[var(--color-muted)]">
          {sample ? "sample · cached real run" : "live run"}
        </span>
      </div>

      {/* run id + copy */}
      <div className="mt-3 flex flex-wrap items-center gap-2 rounded-xl border border-[var(--color-border)]/50 bg-[var(--color-surface-2)]/50 px-3 py-2">
        <span className="text-xs text-[var(--color-muted)]">run id</span>
        <code data-testid="receipt-run-id" className="font-mono text-sm text-[var(--color-ink)]">
          {record.run_id}
        </code>
        <button
          onClick={copyRunId}
          className="ml-auto rounded-lg border border-[var(--color-border)] px-2.5 py-1 text-xs transition hover:bg-[var(--color-surface-2)]"
        >
          {copied ? "copied ✓" : "copy"}
        </button>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <FieldGroup
          title="From this run"
          tag="live"
          tagColor="var(--color-good)"
          fields={live}
        />
        <FieldGroup
          title="Deployment config"
          tag="static"
          tagColor="var(--color-muted)"
          fields={config}
        />
      </div>

      <p className="mt-3 text-xs text-[var(--color-muted)]">
        <span style={{ color: "var(--color-good)" }}>live</span> fields are read from this run&apos;s
        RunRecord; <span>static</span> fields are the deployment&apos;s fixed config. The Phoenix
        MCP calibration path is E2E-verified; the deployed audit uses the table prior.
      </p>
    </div>
  );
}

function FieldGroup({
  title,
  tag,
  tagColor,
  fields,
}: {
  title: string;
  tag: string;
  tagColor: string;
  fields: Field[];
}) {
  return (
    <div data-testid={`receipt-group-${tag}`}>
      <div className="mb-2 flex items-center gap-2">
        <span className="text-sm font-medium">{title}</span>
        <span
          className="rounded-full px-2 py-0.5 text-[10px] font-medium"
          style={{
            color: tagColor,
            background: `color-mix(in oklch, ${tagColor} 16%, transparent)`,
          }}
        >
          {tag}
        </span>
      </div>
      <dl className="flex flex-col gap-1 text-sm">
        {fields.map((f) => (
          <div key={f.k} className="flex items-baseline justify-between gap-3">
            <dt className="text-[var(--color-muted)]">{f.k}</dt>
            <dd className={"text-right " + (f.mono ? "font-mono text-xs" : "")}>{f.v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
