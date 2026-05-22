import { Badge } from "@/components/Badge";
import type { AuditCorrection } from "@/lib/api";

export interface AuditCalloutProps {
  correction: AuditCorrection;
}

/** Explains one self-correction: which hat, the score delta, and the calibration basis. */
export function AuditCallout({ correction }: AuditCalloutProps) {
  const { hat, criterion_id, original, corrected, mean_delta, n, reason } = correction;
  const direction = corrected < original ? "lowered" : corrected > original ? "raised" : "held";
  const tone = direction === "lowered" ? "warn" : direction === "raised" ? "good" : "muted";

  return (
    <div
      data-testid="audit-callout"
      className="rounded-xl border border-[var(--color-warn)]/40 bg-[color-mix(in_oklch,var(--color-warn)_8%,transparent)] p-3 text-sm"
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="accent" title="Six Thinking Hats role">
          {hat} hat
        </Badge>
        <span className="font-medium">{criterion_id}</span>
        <Badge tone={tone}>self-corrected</Badge>
      </div>
      <p className="mt-2 text-[var(--color-muted)]">
        Score {direction} from{" "}
        <span className="font-mono text-[var(--color-ink)]">{original.toFixed(1)}</span> →{" "}
        <span className="font-mono text-[var(--color-ink)]">{corrected.toFixed(1)}</span> after
        consulting {n} past evaluation{n === 1 ? "" : "s"} (mean over-confidence{" "}
        <span className="font-mono">{mean_delta.toFixed(2)}</span>).
      </p>
      {reason && <p className="mt-1 text-xs italic text-[var(--color-muted)]">{reason}</p>}
    </div>
  );
}
