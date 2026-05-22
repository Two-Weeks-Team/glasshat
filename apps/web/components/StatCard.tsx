import type { ReactNode } from "react";

export interface StatCardProps {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
}

/** A surface card showing one headline metric with an optional sub-line. */
export function StatCard({ label, value, sub }: StatCardProps) {
  return (
    <div
      data-testid="stat-card"
      className="hover-lift rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)] p-4"
    >
      <div className="text-xs uppercase tracking-wide text-[var(--color-muted)]">{label}</div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{value}</div>
      {sub != null && <div className="mt-1 text-xs text-[var(--color-muted)]">{sub}</div>}
    </div>
  );
}
