export interface ScoreBarProps {
  label: string;
  score: number;
  max: number;
  weightPct?: number;
  corrected?: boolean;
}

export function ScoreBar({ label, score, max, weightPct, corrected }: ScoreBarProps) {
  const pct = Math.max(0, Math.min(100, (score / max) * 100));
  return (
    <div className="flex flex-col gap-1" data-testid="score-bar">
      <div className="flex items-baseline justify-between text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-[var(--color-muted)]">
          {score.toFixed(1)}/{max}
          {weightPct != null ? ` · ${weightPct}%` : ""}
          {corrected ? " · self-corrected" : ""}
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-[var(--color-muted)]/15">
        <div
          className="h-2 rounded-full bg-[var(--color-accent)]"
          style={{ width: `${pct}%` }}
          data-testid="score-bar-fill"
        />
      </div>
    </div>
  );
}
