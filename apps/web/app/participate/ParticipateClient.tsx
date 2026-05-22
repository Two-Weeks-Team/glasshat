"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { AuditCallout } from "@/components/AuditCallout";
import { Badge } from "@/components/Badge";
import { CountUp } from "@/components/CountUp";
import { EvidenceList } from "@/components/EvidenceList";
import { Reveal } from "@/components/Reveal";
import { RubricTable } from "@/components/RubricTable";
import { ScoreBar } from "@/components/ScoreBar";
import { StageTimeline } from "@/components/StageTimeline";
import { StatCard } from "@/components/StatCard";
import {
  getPlan,
  getRun,
  listPresets,
  streamEvaluate,
  type EvaluationInput,
  type PlanObject,
  type PresetInfo,
  type RunRecord,
} from "@/lib/api";
import {
  constellationNodes,
  initialRunState,
  reduceEvent,
  scoreRows,
  weakestAxis,
  type RunState,
} from "@/lib/participate-state";
import { SAMPLE_COHORT } from "@/lib/sample-cohort";

const ConstellationGraph = dynamic(() => import("@/components/ConstellationGraph"), { ssr: false });

// Real cached RunRecord (gemini-3.1-flash-lite) used for the first-paint sample
// preview so the score bars, audit callout, and 3D graph are visible before any run.
const SAMPLE_RESULT = SAMPLE_COHORT[0].record;

const SAMPLE_DECK =
  "We built Glasshat, a rubric-aware evaluation engine. It ingests a pitch deck, a " +
  "GitHub repo, and the official judging rules, synthesizes a per-evaluation rubric, runs a " +
  "six-perspective panel that grounds every sub-score in retrieved evidence, then audits and " +
  "self-corrects its own over-confident scores against past evaluations. Built on Gemini 3.1 + " +
  "Google ADK with Arize AX observability. Includes a full test suite and a live demo.";

type Phase = "form" | "planning" | "plan" | "running" | "done" | "error";

const scaleMax = (finalScale: string): string => finalScale.split("-").at(-1) ?? finalScale;

export function ParticipateClient() {
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [presetId, setPresetId] = useState("rapid-agent");
  const [deckText, setDeckText] = useState(SAMPLE_DECK);
  const [repoUrl, setRepoUrl] = useState("");

  const [phase, setPhase] = useState<Phase>("form");
  const [plan, setPlan] = useState<PlanObject | null>(null);
  const [run, setRun] = useState<RunState>(initialRunState);
  const [record, setRecord] = useState<RunRecord | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listPresets()
      .then(setPresets)
      .catch(() => setPresets([]));
  }, []);

  const buildInput = (): EvaluationInput => ({
    rubric_source: { preset_id: presetId },
    deck_text: deckText.trim(),
    repo_url: repoUrl.trim() || undefined,
    mode: "participant",
  });

  async function preview() {
    setPhase("planning");
    setError("");
    try {
      setPlan(await getPlan(buildInput()));
      setPhase("plan");
    } catch (e) {
      setError(String(e));
      setPhase("error");
    }
  }

  async function execute() {
    setPhase("running");
    setRecord(null);
    let st = initialRunState;
    setRun(st);
    try {
      await streamEvaluate(buildInput(), (e) => {
        st = reduceEvent(st, e);
        setRun({ ...st });
      });
      if (st.runId) setRecord(await getRun(st.runId));
      setPhase("done");
    } catch (e) {
      setError(String(e));
      setPhase("error");
    }
  }

  const busy = phase === "planning" || phase === "running";

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <header className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Participant</h1>
        <p className="mt-1 max-w-2xl text-[var(--color-muted)]">
          Score your submission against the official rubric, watch the audit catch its own
          over-confidence live, then iterate on your weakest axis.
        </p>
      </header>

      {/* ── Input form ── */}
      <section className="elevate rounded-2xl p-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--color-muted)]">Rubric</span>
            <select
              value={presetId}
              onChange={(e) => setPresetId(e.target.value)}
              disabled={busy}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] px-3 py-2"
            >
              {presets.length === 0 && <option value="rapid-agent">rapid-agent</option>}
              {presets.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label} · {p.criteria_count} criteria · {p.final_scale}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--color-muted)]">Repo URL (optional)</span>
            <input
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              disabled={busy}
              placeholder="https://github.com/you/project"
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] px-3 py-2"
            />
          </label>
        </div>
        <label className="mt-4 flex flex-col gap-1 text-sm">
          <span className="text-[var(--color-muted)]">Pitch / deck text</span>
          <textarea
            value={deckText}
            onChange={(e) => setDeckText(e.target.value)}
            disabled={busy}
            rows={5}
            className="resize-y rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] px-3 py-2 leading-relaxed"
          />
        </label>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            onClick={preview}
            disabled={busy || deckText.trim().length === 0}
            className="rounded-xl bg-[var(--color-accent)] px-5 py-2 font-medium text-white transition disabled:opacity-40"
          >
            {phase === "planning" ? "Synthesizing rubric…" : "Preview plan"}
          </button>
          <button
            onClick={execute}
            disabled={busy || deckText.trim().length === 0}
            className="rounded-xl border border-[var(--color-border)] px-5 py-2 font-medium transition hover:bg-[var(--color-surface-2)] disabled:opacity-40"
          >
            Skip to evaluate
          </button>
        </div>
      </section>

      {error && (
        <p className="mt-4 rounded-xl border border-[var(--color-bad)]/50 bg-[color-mix(in_oklch,var(--color-bad)_10%,transparent)] p-3 text-sm">
          {error}
        </p>
      )}

      {/* ── Gate 1: plan preview ── */}
      {plan && (phase === "plan" || phase === "running" || phase === "done") && (
        <section className="elevate mt-6 rounded-2xl p-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg font-medium">Plan (human gate 1)</h2>
            {phase === "plan" && (
              <button
                onClick={execute}
                className="rounded-xl bg-[var(--color-accent)] px-4 py-1.5 text-sm font-medium text-white"
              >
                Approve &amp; run →
              </button>
            )}
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {plan.hats_enabled.map((h) => (
              <Badge key={h} tone="accent">
                {h}
              </Badge>
            ))}
          </div>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {plan.criteria_in_scope.map((c) => (
              <div
                key={c}
                className="flex items-center justify-between rounded-lg border border-[var(--color-border)]/50 px-3 py-1.5 text-sm"
              >
                <span>{c}</span>
                <span className="font-mono tabular-nums text-[var(--color-muted)]">
                  {Math.round((plan.weights[c] ?? 0) * 100)}%
                </span>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-[var(--color-muted)]">
            Retrieval budget: {plan.retrieval_budget.pitch_chunks ?? 0} pitch ·{" "}
            {plan.retrieval_budget.repo_chunks ?? 0} repo · {plan.retrieval_budget.past_evals ?? 0}{" "}
            past evals · code grader: {plan.code_grader_depth}
          </p>
        </section>
      )}

      {/* ── Live monitor ── */}
      {(phase === "running" || phase === "done") && (
        <section className="elevate mt-6 rounded-2xl p-5">
          <h2 className="mb-4 text-lg font-medium">Live pipeline</h2>
          <StageTimeline current={run.current} beats={run.beats} done={run.done} />
        </section>
      )}

      {/* ── Results (live) ── */}
      {phase === "done" && record && (
        <ResultsView record={record} onIterate={() => setPhase("form")} />
      )}

      {/* ── Sample result preview on first paint (before any run) ── */}
      {phase === "form" && !record && <ResultsView record={SAMPLE_RESULT} sample />}
    </main>
  );
}

function ResultsView({
  record,
  sample = false,
  onIterate,
}: {
  record: RunRecord;
  sample?: boolean;
  onIterate?: () => void;
}) {
  const rows = scoreRows(record);
  const weakest = weakestAxis(rows);
  return (
    <section className="mt-6 flex flex-col gap-6">
      {sample && (
        <p className="rounded-xl border border-[var(--color-accent)]/35 bg-[color-mix(in_oklch,var(--color-accent)_8%,transparent)] px-4 py-2.5 text-sm text-[var(--color-muted)]">
          <span className="font-medium text-[var(--color-ink)]">Sample result</span> — a cached{" "}
          <span className="font-mono">gemini-3.1-flash-lite</span> evaluation so you can see the
          output shape. Submit your own above to run it live.
        </p>
      )}
      <Reveal className="grid gap-3 sm:grid-cols-3">
        <StatCard
          label="Final score"
          value={<CountUp value={record.final_score} />}
          sub={`out of ${scaleMax(record.rubric.scoring_rule.final_scale)}`}
        />
        <StatCard
          label="Self-corrections"
          value={record.audit_corrections.length}
          sub="over-confident axes pulled back"
        />
        <StatCard
          label="Rubric"
          value={record.rubric.source.identifier}
          sub={`${record.rubric.criteria.length} criteria · ${record.rubric.scoring_rule.aggregation}`}
        />
      </Reveal>

      <Reveal>
        <h2 className="mb-3 text-lg font-medium">Per-criterion scores</h2>
        <div className="flex flex-col gap-5">
          {rows.map((r) => (
            <div key={r.id} className="flex flex-col gap-2">
              <ScoreBar
                label={r.label}
                score={r.score}
                max={r.scale}
                weightPct={r.weightPct}
                corrected={r.audit != null}
              />
              <EvidenceList refs={r.evidenceRefs} />
              {r.audit && <AuditCallout correction={r.audit} />}
            </div>
          ))}
        </div>
      </Reveal>

      <Reveal>
        <h2 className="mb-3 text-lg font-medium">Self-correction graph</h2>
        <ConstellationGraph nodes={constellationNodes(record)} />
        <p className="mt-2 text-xs text-[var(--color-muted)]">
          Axes: score · weight · evidence depth. <span className="text-[#f0b429]">Amber</span>{" "}
          nodes were self-corrected and reshape from their over-confident origin.
        </p>
      </Reveal>

      {weakest && !sample && (
        <div className="rounded-2xl border border-[var(--color-accent)]/40 bg-[color-mix(in_oklch,var(--color-accent)_8%,transparent)] p-4">
          <div className="text-sm font-medium">Weakest axis: {weakest.label}</div>
          <p className="mt-1 text-sm text-[var(--color-muted)]">
            Scored {weakest.score.toFixed(1)}/{weakest.scale}. Strengthen the evidence for this
            criterion and re-run to see the score move.
          </p>
          <button
            onClick={onIterate}
            className="mt-3 rounded-lg border border-[var(--color-border)] px-4 py-1.5 text-sm font-medium transition hover:bg-[var(--color-surface-2)]"
          >
            ← Iterate on my submission
          </button>
        </div>
      )}

      <Reveal>
        <h2 className="mb-3 text-lg font-medium">Synthesized rubric</h2>
        <RubricTable rubric={record.rubric} />
      </Reveal>
    </section>
  );
}
