export interface PipelineStep {
  title: string;
  blurb: string;
}

export const PIPELINE: PipelineStep[] = [
  { title: "Ingest", blurb: "Deck + repo + the official rules, chunked and embedded" },
  { title: "Synthesize rubric", blurb: "Per-evaluation rubric that mirrors the actual rules" },
  { title: "6-Hat panel", blurb: "Each perspective grounds its score in retrieved evidence" },
  { title: "Audit & self-correct", blurb: "Over-confident axes pulled back against past evaluations" },
  { title: "Score & rank", blurb: "Final score on the rubric's native scale" },
];

export interface PipelineDiagramProps {
  steps?: PipelineStep[];
}

/** The conceptual engine flow, shown on the landing page. */
export function PipelineDiagram({ steps = PIPELINE }: PipelineDiagramProps) {
  return (
    <ol
      data-testid="pipeline-diagram"
      className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5"
    >
      {steps.map((s, i) => (
        <li
          key={s.title}
          className="relative rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)] p-4"
        >
          <div className="font-mono text-xs text-[var(--color-accent)]">
            {String(i + 1).padStart(2, "0")}
          </div>
          <div className="mt-1 font-medium">{s.title}</div>
          <p className="mt-1 text-xs leading-relaxed text-[var(--color-muted)]">{s.blurb}</p>
        </li>
      ))}
    </ol>
  );
}
