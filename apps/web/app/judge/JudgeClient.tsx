"use client";

import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/Badge";
import { ScoreBar } from "@/components/ScoreBar";
import { StatCard } from "@/components/StatCard";
import {
  evaluate,
  listPresets,
  override,
  type PresetInfo,
  type RunRecord,
} from "@/lib/api";
import { rankSubmissions, topKHitRate, type EvalItem } from "@/lib/ranking";

type RowStatus = "idle" | "running" | "done" | "error";

interface Row {
  label: string;
  deck: string;
  status: RowStatus;
  record?: RunRecord;
  error?: string;
  overrides: Record<string, number>;
}

const SEED: { label: string; deck: string }[] = [
  {
    label: "Glasshat",
    deck:
      "Glasshat is a rubric-aware evaluation engine that ingests the official judging rules, " +
      "synthesizes a per-evaluation rubric, runs a six-hat panel grounded in retrieved evidence, " +
      "and audits and self-corrects its own over-confident scores against past evaluations. " +
      "Built on Gemini + Google ADK with Arize Phoenix observability and the Phoenix MCP server. " +
      "Full test suite, CI, and a live Cloud Run deployment.",
  },
  {
    label: "MeshSight",
    deck:
      "MeshSight is multi-agent observability for Google ADK pipelines. It traces every tool " +
      "call, attributes token cost per agent, and flags drift between runs. Working OpenInference " +
      "integration, a dashboard, and an integration test suite.",
  },
  {
    label: "QuickWrap",
    deck:
      "QuickWrap is a thin wrapper around a single LLM call that drafts marketing emails from a " +
      "short prompt. No custom orchestration, no retrieval, and no tests yet — a familiar wrapper " +
      "pattern shipped fast.",
  },
  {
    label: "TodoZap",
    deck:
      "TodoZap is a to-do list app with an AI button that suggests tasks. Standard CRUD plus one " +
      "prompt; minimal evidence of novel engineering or broad impact.",
  },
];

const newRow = (s: { label: string; deck: string }): Row => ({
  ...s,
  status: "idle",
  overrides: {},
});

export function JudgeClient() {
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [presetId, setPresetId] = useState("rapid-agent");
  const [rows, setRows] = useState<Row[]>(SEED.map(newRow));
  const [winners, setWinners] = useState<Set<string>>(new Set());
  const [locked, setLocked] = useState<Set<string>>(new Set());
  const [running, setRunning] = useState(false);
  const [k, setK] = useState(2);
  const [newLabel, setNewLabel] = useState("");
  const [newDeck, setNewDeck] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    listPresets()
      .then(setPresets)
      .catch(() => setPresets([]));
  }, []);

  const patch = (label: string, p: Partial<Row>) =>
    setRows((rs) => rs.map((r) => (r.label === label ? { ...r, ...p } : r)));

  async function runCohort() {
    setRunning(true);
    setExpanded(null);
    setRows((rs) => rs.map((r) => ({ ...r, status: "running", record: undefined, error: undefined })));
    await Promise.all(
      rows.map(async (r) => {
        try {
          const rec = await evaluate({
            rubric_source: { preset_id: presetId },
            deck_text: r.deck,
            mode: "judge",
          });
          patch(r.label, { status: "done", record: rec });
        } catch (e) {
          patch(r.label, { status: "error", error: String(e) });
        }
      }),
    );
    setRunning(false);
  }

  const items: EvalItem[] = useMemo(
    () =>
      rows
        .filter((r): r is Row & { record: RunRecord } => r.record != null)
        .map((r) => ({ label: r.label, record: r.record, overrides: r.overrides })),
    [rows],
  );
  const ranked = useMemo(() => rankSubmissions(items), [items]);
  const hitRate = topKHitRate(ranked, winners, k);
  const allDone = rows.length > 0 && rows.every((r) => r.status === "done");

  const toggle = (set: Set<string>, label: string): Set<string> => {
    const next = new Set(set);
    if (next.has(label)) next.delete(label);
    else next.add(label);
    return next;
  };

  async function applyOverride(label: string, criterionId: string, score: number, reason: string) {
    const row = rows.find((r) => r.label === label);
    if (!row?.record) return;
    await override(row.record.run_id, { criterion_id: criterionId, score, reason });
    patch(label, { overrides: { ...row.overrides, [criterionId]: score } });
    setExpanded(null);
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Judge</h1>
        <p className="mt-1 max-w-2xl text-[var(--color-muted)]">
          Batch-evaluate a cohort against one synthesized rubric, rank with the rubric&apos;s
          ordered tie-break, override a score at the human gate, and lock the official result.
        </p>
      </header>

      {/* Controls */}
      <section className="rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)] p-5">
        <div className="flex flex-wrap items-end gap-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--color-muted)]">Rubric</span>
            <select
              value={presetId}
              onChange={(e) => setPresetId(e.target.value)}
              disabled={running}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] px-3 py-2"
            >
              {presets.length === 0 && <option value="rapid-agent">rapid-agent</option>}
              {presets.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} · {p.criteria_count} criteria
                </option>
              ))}
            </select>
          </label>
          <button
            onClick={runCohort}
            disabled={running || rows.length === 0}
            className="rounded-xl bg-[var(--color-accent)] px-5 py-2 font-medium text-white transition disabled:opacity-40"
          >
            {running ? `Evaluating ${rows.length}…` : `Run cohort (${rows.length})`}
          </button>
          <label className="flex items-center gap-2 text-sm text-[var(--color-muted)]">
            Top-K
            <input
              type="number"
              min={1}
              max={rows.length}
              value={k}
              onChange={(e) => setK(Math.max(1, Number(e.target.value)))}
              className="w-16 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] px-2 py-1 text-center"
            />
          </label>
        </div>

        {/* Add submission */}
        <div className="mt-4 flex flex-wrap items-end gap-2 border-t border-[var(--color-border)]/40 pt-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--color-muted)]">Add submission</span>
            <input
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
              placeholder="name"
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] px-3 py-2"
            />
          </label>
          <input
            value={newDeck}
            onChange={(e) => setNewDeck(e.target.value)}
            placeholder="pitch / deck text"
            className="min-w-[16rem] flex-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] px-3 py-2 text-sm"
          />
          <button
            onClick={() => {
              if (newLabel.trim() && newDeck.trim()) {
                setRows((rs) => [...rs, newRow({ label: newLabel.trim(), deck: newDeck.trim() })]);
                setNewLabel("");
                setNewDeck("");
              }
            }}
            disabled={running || !newLabel.trim() || !newDeck.trim()}
            className="rounded-xl border border-[var(--color-border)] px-4 py-2 text-sm font-medium transition hover:bg-[var(--color-surface-2)] disabled:opacity-40"
          >
            + Add
          </button>
        </div>
      </section>

      {/* Top-K summary */}
      {allDone && winners.size > 0 && (
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <StatCard
            label={`Top-${k} hit rate`}
            value={`${Math.round(hitRate * 100)}%`}
            sub={`vs ${winners.size} marked winner${winners.size === 1 ? "" : "s"}`}
          />
          <StatCard label="Submissions" value={rows.length} sub="in this cohort" />
          <StatCard
            label="Locked"
            value={locked.size}
            sub="official results frozen"
          />
        </div>
      )}

      {/* Ranking / cohort table */}
      <section className="mt-6 overflow-hidden rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)]">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-[var(--color-muted)]">
              <th className="px-4 py-3 font-medium">#</th>
              <th className="px-4 py-3 font-medium">Submission</th>
              <th className="px-4 py-3 font-medium">Final</th>
              <th className="px-4 py-3 font-medium">Per-criterion</th>
              <th className="px-4 py-3 font-medium">Winner</th>
              <th className="px-4 py-3 font-medium">Official</th>
            </tr>
          </thead>
          <tbody>
            {ranked.map((r) => {
              const row = rows.find((x) => x.label === r.label)!;
              const isLocked = locked.has(r.label);
              const overridden = Object.keys(row.overrides).length > 0;
              return (
                <RankedRow
                  key={r.label}
                  rank={r.rank}
                  label={r.label}
                  effectiveFinal={r.effectiveFinal}
                  record={r.record}
                  effectiveScores={r.effectiveScores}
                  scaleLabel={r.record.rubric.scoring_rule.final_scale}
                  isWinner={winners.has(r.label)}
                  isLocked={isLocked}
                  overridden={overridden}
                  expanded={expanded === r.label}
                  onToggleWinner={() => !isLocked && setWinners((w) => toggle(w, r.label))}
                  onToggleLock={() => setLocked((l) => toggle(l, r.label))}
                  onExpand={() => setExpanded((e) => (e === r.label ? null : r.label))}
                  onOverride={(cid, sc, reason) => applyOverride(r.label, cid, sc, reason)}
                />
              );
            })}
            {/* rows not yet scored */}
            {rows
              .filter((r) => r.record == null)
              .map((r) => (
                <tr key={r.label} className="border-t border-[var(--color-border)]/40">
                  <td className="px-4 py-3 text-[var(--color-muted)]">–</td>
                  <td className="px-4 py-3 font-medium">{r.label}</td>
                  <td className="px-4 py-3" colSpan={4}>
                    {r.status === "running" && (
                      <span className="text-[var(--color-muted)]">evaluating…</span>
                    )}
                    {r.status === "error" && (
                      <span className="text-[var(--color-bad)]">{r.error}</span>
                    )}
                    {r.status === "idle" && (
                      <span className="text-[var(--color-muted)]">not yet evaluated</span>
                    )}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </section>
      {ranked.length > 0 && (
        <p className="mt-2 text-xs text-[var(--color-muted)]">
          Ties break by the rubric&apos;s ordered chain (Tech → Design → Impact → Idea). Override a
          score to re-rank; lock to freeze the official result.
        </p>
      )}
    </main>
  );
}

interface RankedRowProps {
  rank: number;
  label: string;
  effectiveFinal: number;
  record: RunRecord;
  effectiveScores: Record<string, number>;
  scaleLabel: string;
  isWinner: boolean;
  isLocked: boolean;
  overridden: boolean;
  expanded: boolean;
  onToggleWinner: () => void;
  onToggleLock: () => void;
  onExpand: () => void;
  onOverride: (criterionId: string, score: number, reason: string) => void;
}

function RankedRow(props: RankedRowProps) {
  const {
    rank,
    label,
    effectiveFinal,
    record,
    effectiveScores,
    isWinner,
    isLocked,
    overridden,
    expanded,
    onToggleWinner,
    onToggleLock,
    onExpand,
    onOverride,
  } = props;
  const corrections = record.audit_corrections.length;

  return (
    <>
      <tr className="border-t border-[var(--color-border)]/40 align-top">
        <td className="px-4 py-3 font-mono text-lg tabular-nums">{rank}</td>
        <td className="px-4 py-3">
          <div className="font-medium">{label}</div>
          <div className="mt-1 flex flex-wrap gap-1">
            {corrections > 0 && (
              <Badge tone="warn">
                {corrections} self-correction{corrections === 1 ? "" : "s"}
              </Badge>
            )}
            {overridden && <Badge tone="accent">overridden</Badge>}
          </div>
        </td>
        <td className="px-4 py-3">
          <div className="font-mono text-xl tabular-nums">{effectiveFinal.toFixed(1)}</div>
        </td>
        <td className="px-4 py-3" style={{ minWidth: "14rem" }}>
          <div className="flex flex-col gap-1.5">
            {record.rubric.criteria.map((c) => (
              <ScoreBar
                key={c.id}
                label={c.label}
                score={effectiveScores[c.id] ?? 0}
                max={c.scale}
                weightPct={Math.round((c.weight ?? 0) * 100)}
              />
            ))}
          </div>
        </td>
        <td className="px-4 py-3">
          <button
            onClick={onToggleWinner}
            disabled={isLocked}
            className={
              "rounded-lg border px-2 py-1 text-xs transition disabled:opacity-40 " +
              (isWinner
                ? "border-[var(--color-good)] text-[var(--color-good)]"
                : "border-[var(--color-border)] text-[var(--color-muted)] hover:bg-[var(--color-surface-2)]")
            }
          >
            {isWinner ? "★ winner" : "mark winner"}
          </button>
        </td>
        <td className="px-4 py-3">
          <div className="flex flex-col gap-1">
            <button
              onClick={onToggleLock}
              className={
                "rounded-lg border px-2 py-1 text-xs transition " +
                (isLocked
                  ? "border-[var(--color-accent)] text-[var(--color-accent)]"
                  : "border-[var(--color-border)] text-[var(--color-muted)] hover:bg-[var(--color-surface-2)]")
              }
            >
              {isLocked ? "🔒 locked" : "lock"}
            </button>
            {!isLocked && (
              <button
                onClick={onExpand}
                className="text-xs text-[var(--color-muted)] underline-offset-2 hover:underline"
              >
                {expanded ? "close" : "override…"}
              </button>
            )}
          </div>
        </td>
      </tr>
      {expanded && !isLocked && (
        <tr className="border-t border-[var(--color-border)]/20 bg-[var(--color-surface-2)]/40">
          <td />
          <td colSpan={5} className="px-4 py-3">
            <OverrideForm record={record} effectiveScores={effectiveScores} onSubmit={onOverride} />
          </td>
        </tr>
      )}
    </>
  );
}

function OverrideForm({
  record,
  effectiveScores,
  onSubmit,
}: {
  record: RunRecord;
  effectiveScores: Record<string, number>;
  onSubmit: (criterionId: string, score: number, reason: string) => void;
}) {
  const [cid, setCid] = useState(record.rubric.criteria[0]?.id ?? "");
  const criterion = record.rubric.criteria.find((c) => c.id === cid);
  const [score, setScore] = useState(effectiveScores[cid] ?? 3);
  const [reason, setReason] = useState("");

  return (
    <div className="flex flex-wrap items-end gap-2 text-sm">
      <label className="flex flex-col gap-1">
        <span className="text-xs text-[var(--color-muted)]">Criterion</span>
        <select
          value={cid}
          onChange={(e) => {
            setCid(e.target.value);
            setScore(effectiveScores[e.target.value] ?? 3);
          }}
          className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-2 py-1.5"
        >
          {record.rubric.criteria.map((c) => (
            <option key={c.id} value={c.id}>
              {c.label}
            </option>
          ))}
        </select>
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-xs text-[var(--color-muted)]">Score (1–{criterion?.scale ?? 5})</span>
        <input
          type="number"
          min={1}
          max={criterion?.scale ?? 5}
          step={0.5}
          value={score}
          onChange={(e) => setScore(Number(e.target.value))}
          className="w-24 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-2 py-1.5"
        />
      </label>
      <label className="flex flex-1 flex-col gap-1">
        <span className="text-xs text-[var(--color-muted)]">Reason (gate 2)</span>
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="why the manual override"
          className="min-w-[10rem] rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-2 py-1.5"
        />
      </label>
      <button
        onClick={() => onSubmit(cid, score, reason)}
        className="rounded-lg bg-[var(--color-accent)] px-4 py-1.5 font-medium text-white"
      >
        Apply override
      </button>
    </div>
  );
}
