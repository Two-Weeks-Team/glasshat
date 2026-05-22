import { Badge } from "@/components/Badge";
import type { SynthesizedRubric } from "@/lib/api";

export interface RubricTableProps {
  rubric: SynthesizedRubric;
}

const pct = (w: number | null): string => (w == null ? "—" : `${Math.round(w * 100)}%`);

/** Renders a synthesized rubric: criteria with weights/scale/BMAD + the tie-break order. */
export function RubricTable({ rubric }: RubricTableProps) {
  const order = new Map(rubric.tie_breakers.map((t) => [t.criterion_id, t.order]));
  return (
    <div
      data-testid="rubric-table"
      className="overflow-hidden rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)]"
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--color-border)]/60 px-4 py-3 text-xs text-[var(--color-muted)]">
        <span>
          {rubric.source.type}: <span className="font-mono">{rubric.source.identifier}</span>
        </span>
        <span>
          {rubric.scoring_rule.aggregation} · scale {rubric.scoring_rule.final_scale}
        </span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs uppercase tracking-wide text-[var(--color-muted)]">
            <th className="px-4 py-2 font-medium">Criterion</th>
            <th className="px-4 py-2 font-medium">Weight</th>
            <th className="px-4 py-2 font-medium">Scale</th>
            <th className="px-4 py-2 font-medium">BMAD</th>
            <th className="px-4 py-2 font-medium">Tie-break</th>
          </tr>
        </thead>
        <tbody>
          {rubric.criteria.map((c) => (
            <tr key={c.id} className="border-t border-[var(--color-border)]/40 align-top">
              <td className="px-4 py-3">
                <div className="font-medium">{c.label}</div>
                {c.source_clause && (
                  <div className="mt-0.5 text-xs text-[var(--color-muted)]">{c.source_clause}</div>
                )}
              </td>
              <td className="px-4 py-3 font-mono tabular-nums">{pct(c.weight)}</td>
              <td className="px-4 py-3 font-mono tabular-nums">1–{c.scale}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {c.bmad_mapping.map((b) => (
                    <Badge key={b} tone="muted">
                      {b}
                    </Badge>
                  ))}
                </div>
              </td>
              <td className="px-4 py-3 font-mono tabular-nums">{order.get(c.id) ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
