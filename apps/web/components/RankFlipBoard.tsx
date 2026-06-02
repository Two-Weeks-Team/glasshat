/**
 * RankFlipBoard — two-column "without audit / with Glasshat audit" leaderboard.
 *
 * Left column is the cohort ordered by the raw six-hat consensus (no
 * calibration); right column is the same cohort ordered by Glasshat's audited
 * final. Rows whose rank moved across the two views get a soft glow + a
 * `↑n / ↓n` indicator so the judging-relevant claim — "the audit changes who
 * wins" — is visible on the first paint of /judge. The visual is the whole
 * point: a single number going from 9.0 to 7.84 is forgettable; a different
 * project sitting at #1 because of the audit is not.
 */

import { Badge } from "@/components/Badge";
import {
  type EvalItem,
  type RankedItem,
  rankSubmissions,
  rankSubmissionsPreAudit,
} from "@/lib/ranking";

export interface RankFlipBoardProps {
  items: EvalItem[];
  /** Visible heading above the board. */
  title?: string;
  className?: string;
}

interface FlipRow extends RankedItem {
  /** Rank on the *other* axis (right column = pre-audit rank, etc.). */
  otherRank: number;
  /** Positive when the audit *promoted* this row vs the pre-audit view. */
  delta: number;
}

function annotate(
  side: RankedItem[],
  otherRankByLabel: Map<string, number>,
  invert: boolean,
): FlipRow[] {
  return side.map((r) => {
    const otherRank = otherRankByLabel.get(r.label) ?? r.rank;
    const raw = otherRank - r.rank;
    // From the right column's perspective: rank went *down numerically* means
    // the audit *promoted* this row (good = green). From the left column's
    // perspective the sign flips: a row that *will* be promoted by the audit
    // should already read as "about to move up" in the raw view.
    const delta = invert ? -raw : raw;
    return { ...r, otherRank, delta };
  });
}

export function RankFlipBoard({
  items,
  title = "Same cohort. Two ranks.",
  className,
}: RankFlipBoardProps) {
  if (items.length < 2) {
    // The board only tells a story with a cohort — single submissions belong
    // on /participate. Rendering nothing is intentional, not an empty state.
    return null;
  }

  const audited = rankSubmissions(items);
  const preAudited = rankSubmissionsPreAudit(items);
  const auditedRankByLabel = new Map(audited.map((r) => [r.label, r.rank]));
  const preAuditedRankByLabel = new Map(preAudited.map((r) => [r.label, r.rank]));

  const leftRows = annotate(preAudited, auditedRankByLabel, /* invert */ true);
  const rightRows = annotate(audited, preAuditedRankByLabel, /* invert */ false);

  const flipCount = audited.reduce(
    (acc, r) => (auditedRankByLabel.get(r.label) !== preAuditedRankByLabel.get(r.label) ? acc + 1 : acc),
    0,
  );

  return (
    <section
      data-testid="rank-flip-board"
      className={"elevate rounded-3xl p-5 sm:p-6 " + (className ?? "")}
    >
      <header className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
          <p className="mt-0.5 text-xs text-[var(--color-muted)]">
            Six-hat raw consensus on the left; Glasshat&apos;s audited rank on the right.
          </p>
        </div>
        <Badge tone={flipCount > 0 ? "accent" : "muted"}>
          {flipCount > 0
            ? `audit moved ${flipCount} of ${items.length} position${flipCount === 1 ? "" : "s"}`
            : "no rank change in this cohort"}
        </Badge>
      </header>
      <div className="grid gap-4 sm:grid-cols-2">
        <Column
          subtitle="Without Glasshat audit"
          subtitleHint="raw six-hat consensus"
          rows={leftRows}
          dimmer
        />
        <Column
          subtitle="With Glasshat audit"
          subtitleHint="calibration applied"
          rows={rightRows}
        />
      </div>
    </section>
  );
}

interface ColumnProps {
  subtitle: string;
  subtitleHint: string;
  rows: FlipRow[];
  /** Renders the raw column slightly de-emphasised so the audited side is the hero. */
  dimmer?: boolean;
}

function Column({ subtitle, subtitleHint, rows, dimmer = false }: ColumnProps) {
  return (
    <div className="flex flex-col gap-2.5">
      <div
        className={
          "flex items-baseline justify-between text-xs uppercase tracking-wide " +
          (dimmer ? "text-[var(--color-muted)]" : "text-[var(--color-accent)]")
        }
      >
        <span className="font-medium">{subtitle}</span>
        <span className="text-[var(--color-muted)] normal-case">{subtitleHint}</span>
      </div>
      <ol className="flex flex-col gap-2">
        {rows.map((r) => (
          <FlipRowCard key={`${subtitle}-${r.label}`} row={r} dimmer={dimmer} />
        ))}
      </ol>
    </div>
  );
}

function FlipRowCard({ row, dimmer }: { row: FlipRow; dimmer: boolean }) {
  const direction = row.delta > 0 ? "up" : row.delta < 0 ? "down" : "flat";
  const glowClass =
    direction === "up" ? "flip-row flip-row-up" : direction === "down" ? "flip-row flip-row-down" : "";
  const indicator = direction === "flat" ? "" : direction === "up" ? `↑${row.delta}` : `↓${Math.abs(row.delta)}`;

  return (
    <li
      data-testid="rank-flip-row"
      data-direction={direction}
      data-label={row.label}
      className={
        "flex items-center justify-between gap-3 rounded-2xl border border-[var(--color-border)]/40 bg-[var(--color-surface-2)]/60 px-3.5 py-2.5 " +
        glowClass
      }
    >
      <div className="flex min-w-0 items-center gap-3">
        <span
          className={
            "font-mono tabular-nums " +
            (dimmer ? "text-xl text-[var(--color-muted)]" : "text-2xl text-gradient")
          }
        >
          {row.rank}
        </span>
        <span className="truncate font-medium">{row.label}</span>
      </div>
      <div className="flex shrink-0 items-baseline gap-2">
        {indicator && (
          <span
            data-testid="rank-flip-indicator"
            className={
              "rounded-md px-1.5 py-0.5 font-mono text-[11px] tabular-nums " +
              (direction === "up"
                ? "bg-[color-mix(in_oklch,var(--color-good)_22%,transparent)] text-[var(--color-good)]"
                : "bg-[color-mix(in_oklch,var(--color-warn)_22%,transparent)] text-[var(--color-warn)]")
            }
          >
            {indicator}
          </span>
        )}
        <span
          className={
            "font-mono tabular-nums " +
            (dimmer ? "text-sm text-[var(--color-muted)]" : "text-base font-semibold")
          }
        >
          {row.effectiveFinal.toFixed(1)}
        </span>
      </div>
    </li>
  );
}
