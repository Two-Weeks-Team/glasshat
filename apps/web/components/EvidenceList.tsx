export interface EvidenceListProps {
  refs: string[];
}

/** Render retrieved evidence references as monospace chips (empty → a hint). */
export function EvidenceList({ refs }: EvidenceListProps) {
  if (refs.length === 0) {
    return (
      <span data-testid="evidence-empty" className="text-xs italic text-[var(--color-muted)]">
        no evidence retrieved
      </span>
    );
  }
  return (
    <ul data-testid="evidence-list" className="flex flex-wrap gap-1.5">
      {refs.map((r) => (
        <li
          key={r}
          className="rounded-md border border-[var(--color-border)]/60 bg-[var(--color-surface-2)] px-1.5 py-0.5 font-mono text-[11px] text-[var(--color-muted)]"
        >
          {r}
        </li>
      ))}
    </ul>
  );
}
