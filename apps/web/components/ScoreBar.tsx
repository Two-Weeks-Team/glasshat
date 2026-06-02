export interface ScoreBarProps {
  label: string;
  score: number;
  max: number;
  weightPct?: number;
  corrected?: boolean;
  /** Pre-audit (over-confident) score on the same scale. When it is higher than
   *  the audited `score`, a faint "ghost" bar marks where the score *was*, so the
   *  audited fill visibly recedes from the over-confident origin. */
  originScore?: number;
}

export function ScoreBar({
  label,
  score,
  max,
  weightPct,
  corrected,
  originScore,
}: ScoreBarProps) {
  const pct = Math.max(0, Math.min(100, (score / max) * 100));
  const originPct =
    originScore != null ? Math.max(0, Math.min(100, (originScore / max) * 100)) : pct;
  // Only draw the ghost when the audit actually pulled the score DOWN.
  const showGhost = originScore != null && originPct > pct + 0.5;
  // Ramp the fill so weak axes read red, mid amber, strong the brand accent.
  const fill =
    pct < 40 ? "var(--color-bad)" : pct < 70 ? "var(--color-warn)" : "var(--color-accent)";
  return (
    <div className="flex flex-col gap-1" data-testid="score-bar">
      <div className="flex items-baseline justify-between text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-[var(--color-muted)]">
          {showGhost && (
            <span className="numeral mr-1 text-[var(--color-warn)]/70 line-through">
              {originScore!.toFixed(1)}
            </span>
          )}
          <span className="numeral">{score.toFixed(1)}</span>/{max}
          {weightPct != null ? ` · ${weightPct}%` : ""}
          {corrected ? " · self-corrected" : ""}
        </span>
      </div>
      <div className="relative h-2 w-full rounded-full bg-[var(--color-muted)]/15">
        {showGhost && (
          // The receded segment: from the audited width to the over-confident origin.
          <div
            className="absolute inset-y-0 left-0 rounded-full border border-dashed border-[var(--color-warn)]/50 bg-[color-mix(in_oklch,var(--color-warn)_14%,transparent)]"
            style={{ width: `${originPct}%` }}
            data-testid="score-bar-ghost"
            aria-hidden
          />
        )}
        <div
          className="score-fill absolute inset-y-0 left-0 rounded-full"
          style={{ width: `${pct}%`, background: fill }}
          data-testid="score-bar-fill"
        />
      </div>
    </div>
  );
}
