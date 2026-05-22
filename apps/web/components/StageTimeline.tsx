import { railIndexForStage, TIMELINE_STAGES, WOW_BEATS } from "@/lib/stages";

export interface BeatEntry {
  stage: string;
  detail?: string;
}

export interface StageTimelineProps {
  /** The most recent emitted stage name (rail position is derived from it). */
  current: string;
  /** The interleaved audit micro-events, in arrival order. */
  beats?: BeatEntry[];
  /** True once the run has finished (forces every rail node to "done"). */
  done?: boolean;
}

type NodeState = "done" | "active" | "pending";

/** Live pipeline monitor: a 7-stage rail plus the audit "wow-beat" ticker. */
export function StageTimeline({ current, beats = [], done = false }: StageTimelineProps) {
  const curIdx = done ? TIMELINE_STAGES.length : railIndexForStage(current);

  return (
    <div data-testid="stage-timeline" className="flex flex-col gap-4">
      <ol className="flex flex-wrap gap-2">
        {TIMELINE_STAGES.map((s, i) => {
          const state: NodeState = i < curIdx ? "done" : i === curIdx ? "active" : "pending";
          return (
            <li
              key={s.name}
              data-state={state}
              title={s.blurb}
              className={
                "flex items-center gap-2 rounded-xl border px-3 py-1.5 text-xs transition " +
                (state === "done"
                  ? "border-[var(--color-good)]/50 text-[var(--color-good)]"
                  : state === "active"
                    ? "animate-pulse-ring border-[var(--color-accent)] text-[var(--color-ink)]"
                    : "border-[var(--color-border)]/50 text-[var(--color-muted)]")
              }
            >
              <span className="font-mono tabular-nums opacity-60">{i + 1}</span>
              {s.label}
            </li>
          );
        })}
      </ol>

      {beats.length > 0 && (
        <ul data-testid="beat-log" className="flex flex-col gap-1 text-xs">
          {beats.map((b, i) => (
            <li key={`${b.stage}-${i}`} className="flex items-center gap-2 text-[var(--color-muted)]">
              <span className="text-[var(--color-accent-2)]" aria-hidden>
                ▸
              </span>
              <span className="text-[var(--color-ink)]">{WOW_BEATS[b.stage] ?? b.stage}</span>
              {b.detail && <span className="font-mono">{b.detail}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
