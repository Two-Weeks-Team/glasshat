export interface EvidenceListProps {
  refs: string[];
}

/** A `repo:*` ref is evidence pulled from the GitHub repository (metadata-only:
 *  README / language mix / facts). Everything else (e.g. `deck-0`) is a deck
 *  quote. Provenance is labelled honestly — metadata-only grading has no
 *  file:line, so we surface the repo facet, not a fabricated line number. */
function provenance(ref: string): { kind: "repo" | "deck"; label: string } {
  if (ref.startsWith("repo:")) {
    return { kind: "repo", label: ref.slice("repo:".length) };
  }
  return { kind: "deck", label: ref };
}

/** Render retrieved evidence references as monospace chips (empty → a hint).
 *  Repo-sourced evidence is tinted + tagged so judges can tell at a glance
 *  whether a hat leaned on the deck or on the actual repository. */
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
      {refs.map((r) => {
        const { kind, label } = provenance(r);
        const isRepo = kind === "repo";
        return (
          <li
            key={r}
            data-testid="evidence-ref"
            data-kind={kind}
            className={
              "flex items-center gap-1 rounded-md border px-1.5 py-0.5 font-mono text-[11px] " +
              (isRepo
                ? "border-[var(--color-accent)]/50 bg-[color-mix(in_oklch,var(--color-accent)_14%,transparent)] text-[var(--color-accent)]"
                : "border-[var(--color-border)]/60 bg-[var(--color-surface-2)] text-[var(--color-muted)]")
            }
          >
            <span className="text-[9px] uppercase tracking-wide opacity-70">
              {isRepo ? "repo" : "deck"}
            </span>
            {label}
          </li>
        );
      })}
    </ul>
  );
}
