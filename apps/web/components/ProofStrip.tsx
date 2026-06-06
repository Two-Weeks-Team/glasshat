import { PROOF_CHIPS, PROOF_STATE_UI, type ProofChip } from "@/lib/deployment";

/**
 * First-screen Rapid Agent stack proof: five chips a judge can read in a single
 * video frame. All five pillars are live on every request — including the
 * Phoenix-MCP calibration loop (reads + writes the dataset over MCP per request,
 * verified against prod). No network calls — deterministic and stable for recording.
 */
export function ProofStrip({ className = "" }: { className?: string }) {
  return (
    <div
      data-testid="proof-strip"
      role="list"
      aria-label="Rapid Agent stack proof"
      className={"flex flex-wrap items-center gap-2 " + className}
    >
      {PROOF_CHIPS.map((chip) => (
        <ProofChipView key={chip.id} chip={chip} />
      ))}
    </div>
  );
}

function ProofChipView({ chip }: { chip: ProofChip }) {
  const ui = PROOF_STATE_UI[chip.state];
  return (
    <span
      role="listitem"
      data-testid={`proof-chip-${chip.id}`}
      data-state={chip.state}
      title={chip.title}
      aria-label={`${chip.label}: ${chip.detail} — ${ui.word}`}
      className="inline-flex items-center gap-2 rounded-full border bg-[var(--color-surface)]/70 px-3 py-1.5 text-xs"
      style={{ borderColor: `color-mix(in oklch, ${ui.color} 45%, transparent)` }}
    >
      <span
        aria-hidden
        className="inline-flex h-4 w-4 items-center justify-center rounded-full text-[10px] font-bold text-[var(--color-bg)]"
        style={{ background: ui.color }}
      >
        {ui.mark}
      </span>
      <span className="font-medium text-[var(--color-ink)]">{chip.label}</span>
      <span className="text-[var(--color-muted)]">{chip.detail}</span>
    </span>
  );
}
