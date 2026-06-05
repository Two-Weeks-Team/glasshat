import calibration from "@/lib/calibration-result.json";

import { StatCard } from "@/components/StatCard";

/**
 * Offline "does the audit improve the ranking?" evidence on the /judge page.
 *
 * hit@k = how many of the evaluator's top-k ranked submissions were actual Devpost
 * winners, before vs after the audit. The source labels are BINARY (winner / not) —
 * there is no rank in them — so this is hit@k, never a rank curve. The figure is
 * generated offline by experiments/run_calibration_experiment.py; the caveat states
 * the backend honestly (mock = illustrative; vertex = live).
 */
export function CalibrationBand({ className = "" }: { className?: string }) {
  const pre = Math.round(calibration.hit_at_k_pre_audit * 100);
  const post = Math.round(calibration.hit_at_k_post_audit * 100);
  const deltaPts = Math.round(calibration.delta * 100);
  const noChange = deltaPts === 0;
  // Don't dress up a zero as a win: a flat result reads "±0 pts / no change",
  // never an ambiguous "+0 pts" that glances as positive.
  const deltaLabel = noChange ? "±0 pts" : `${deltaPts > 0 ? "+" : "−"}${Math.abs(deltaPts)} pts`;
  const deltaSub = noChange
    ? "no change in top-13 hit rate on this run"
    : deltaPts > 0
      ? "winners ranked higher after audit"
      : "winners ranked lower after audit";

  return (
    <section
      aria-label="Offline calibration: audit effect on ranking"
      className={`elevate rounded-2xl p-5 ${className}`}
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--color-muted)]">
          Calibration · hit@{calibration.k} (does the audit improve the ranking?)
        </h2>
        <span className="font-mono text-xs text-[var(--color-muted)]">
          n={calibration.n} · {calibration.n_winners} winners · backend={calibration.backend}
        </span>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <StatCard label="hit@13 before audit" value={`${pre}%`} sub="pre-calibration ranking" />
        <StatCard label="hit@13 after audit" value={`${post}%`} sub="post-calibration ranking" />
        <StatCard label="Audit effect" value={deltaLabel} sub={deltaSub} />
      </div>

      <p className="mt-3 text-xs leading-relaxed text-[var(--color-muted)]">{calibration.caveat}</p>
    </section>
  );
}
