"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/Badge";
import type { AuditCorrection } from "@/lib/api";

export interface SelfCorrectionCardProps {
  correction: AuditCorrection;
  /** Hat assessment scale (0–10). */
  scale?: number;
}

const clamp01 = (v: number): number => Math.max(0, Math.min(1, v));

/**
 * The hero "audit-the-auditor" moment, deliberately not hidden in expandable
 * text: which hat over-scored, the original score, the correction delta, the
 * corrected score, the calibration basis, and a bar that visibly slides from
 * the over-confident origin to the calibrated value. (Respects
 * prefers-reduced-motion via the .score-fill utility, which disables the
 * transition.)
 */
export function SelfCorrectionCard({ correction, scale = 10 }: SelfCorrectionCardProps) {
  const { hat, criterion_id, original, corrected, mean_delta, n, reason } = correction;
  const lowered = corrected < original;
  const delta = corrected - original;
  const origFrac = clamp01(original / scale);
  const corrFrac = clamp01(corrected / scale);

  // Render at the over-confident origin first, then ease to the calibrated value.
  const [frac, setFrac] = useState(origFrac);
  useEffect(() => {
    setFrac(origFrac);
    const id = setTimeout(() => setFrac(corrFrac), 90);
    return () => clearTimeout(id);
  }, [origFrac, corrFrac]);

  return (
    <div
      data-testid="self-correction-card"
      data-direction={lowered ? "lowered" : corrected > original ? "raised" : "held"}
      className="overflow-hidden rounded-2xl border border-[var(--color-warn)]/45 bg-[color-mix(in_oklch,var(--color-warn)_7%,var(--color-surface))] p-5"
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="warn">audit · self-correction</Badge>
        <span className="text-sm font-medium">
          <span className="uppercase">{hat}</span> hat over-scored{" "}
          <span className="font-mono">{criterion_id}</span>
        </span>
      </div>

      <div className="mt-4 flex items-end gap-4">
        <div className="flex flex-col">
          <span className="text-xs text-[var(--color-muted)]">original</span>
          <span className="font-mono text-2xl tabular-nums text-[var(--color-warn)] line-through decoration-[var(--color-warn)]/60">
            {original.toFixed(1)}
          </span>
        </div>
        <span aria-hidden className="pb-1 text-xl text-[var(--color-muted)]">
          →
        </span>
        <div className="flex flex-col">
          <span className="text-xs text-[var(--color-muted)]">corrected</span>
          <span className="text-gradient font-mono text-4xl font-semibold tabular-nums">
            {corrected.toFixed(1)}
          </span>
        </div>
        <div className="ml-auto flex flex-col items-end">
          <span className="text-xs text-[var(--color-muted)]">delta</span>
          <span
            className="font-mono text-lg tabular-nums"
            style={{ color: lowered ? "var(--color-warn)" : "var(--color-good)" }}
          >
            {delta > 0 ? "+" : ""}
            {delta.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Bar that slides from the over-confident origin to the calibrated value */}
      <div
        className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-[var(--color-surface-2)]"
        role="img"
        aria-label={`Score corrected from ${original.toFixed(1)} to ${corrected.toFixed(1)} out of ${scale}`}
      >
        <div
          data-testid="correction-bar"
          className="score-fill h-full rounded-full"
          style={{
            width: `${frac * 100}%`,
            background: lowered
              ? "linear-gradient(90deg, var(--color-accent), var(--color-good))"
              : "var(--color-good)",
          }}
        />
      </div>

      <p className="mt-3 text-sm text-[var(--color-muted)]">
        Basis:{" "}
        <span className="text-[var(--color-ink)]">calibrated prior</span> · {n} past evaluation
        {n === 1 ? "" : "s"} · mean over-confidence{" "}
        <span className="font-mono">{mean_delta.toFixed(2)}</span>
        <span className="italic"> · live-trace variant: Phoenix MCP path</span>
      </p>
      {reason && <p className="mt-1 text-xs italic text-[var(--color-muted)]">{reason}</p>}

      <p className="mt-4 border-t border-[var(--color-border)]/40 pt-3 text-sm font-medium text-[var(--color-ink)]">
        Glasshat catches its own over-confidence and corrects the score before the judge locks it.
      </p>
    </div>
  );
}
