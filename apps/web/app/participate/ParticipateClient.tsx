"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

import { ScoreBar } from "@/components/ScoreBar";
import { getRun, streamEvaluate, type RunRecord } from "@/lib/api";
import { projectAll, type CriterionFeature, type Node3D } from "@/lib/projection";

const ConstellationGraph = dynamic(() => import("@/components/ConstellationGraph"), {
  ssr: false,
});

function toNodes(rec: RunRecord): Node3D[] {
  const features: CriterionFeature[] = rec.scores.map((s) => ({
    id: s.criterion_id,
    scoreFrac: s.score / 5,
    weight: 0.25,
    evidenceDepth: s.audit ? 0.3 : 0.7,
  }));
  return projectAll(features);
}

export function ParticipateClient() {
  const [record, setRecord] = useState<RunRecord | null>(null);
  const [status, setStatus] = useState<string>("idle");

  async function run() {
    setStatus("running");
    let runId = "";
    await streamEvaluate(
      {
        rubric_source: { preset_id: "rapid-agent" },
        deck_text: "We built a novel multi-agent evaluation system in Python with tests.",
        mode: "participant",
      },
      (e) => {
        setStatus(e.stage);
        if (e.stage === "queued" && typeof e.data.run_id === "string") {
          runId = e.data.run_id;
        }
      },
    );
    if (runId) setRecord(await getRun(runId));
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-3xl font-semibold">Participant</h1>
      <p className="mt-2 text-[var(--color-muted)]">
        Run your submission and watch the audit self-correct the over-confident axis.
      </p>
      <button
        onClick={run}
        className="mt-6 rounded-xl bg-[var(--color-accent)] px-5 py-2 font-medium text-white"
      >
        Run sample evaluation
      </button>
      <p className="mt-2 text-sm text-[var(--color-muted)]">Status: {status}</p>
      {record && (
        <section className="mt-8 flex flex-col gap-4">
          <div className="text-2xl font-semibold">Final: {record.final_score.toFixed(1)}</div>
          {record.scores.map((s) => (
            <ScoreBar
              key={s.criterion_id}
              label={s.criterion_id}
              score={s.score}
              max={5}
              corrected={s.audit != null}
            />
          ))}
          <ConstellationGraph nodes={toNodes(record)} />
        </section>
      )}
    </main>
  );
}
