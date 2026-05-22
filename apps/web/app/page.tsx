import Link from "next/link";

import { Badge } from "@/components/Badge";
import { HomeStats } from "@/components/HomeStats";
import { PipelineDiagram } from "@/components/PipelineDiagram";

const FEATURES: { title: string; body: string }[] = [
  {
    title: "Rubric-aware, not one-size-fits-all",
    body: "Each criterion maps onto a shared BMAD vocabulary so scores stay comparable across different rubrics — and the official Rapid Agent rule (4 × 25%, ordered tie-break) is honored exactly.",
  },
  {
    title: "Every score is grounded",
    body: "Six perspectives each retrieve evidence via in-code hybrid search (dense cosine + BM25 + RRF). No vector database — Vertex embeddings over an in-memory index.",
  },
  {
    title: "It audits its own scores",
    body: "An over-confident, low-evidence assessment is pulled back toward calibrated past evaluations — live, on screen, with the 3D graph reshaping as it happens.",
  },
  {
    title: "Built for the Arize track",
    body: "Gemini (Vertex AI) + Google ADK, with Arize Phoenix observability and the Phoenix MCP server consulted at runtime for the self-improvement loop.",
  },
];

export default function Home() {
  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-14 px-6 py-14">
      {/* Hero */}
      <section className="flex flex-col gap-5">
        <div className="flex flex-wrap gap-2">
          <Badge tone="accent">Arize track</Badge>
          <Badge tone="muted">Gemini · Vertex AI</Badge>
          <Badge tone="muted">Google ADK</Badge>
          <Badge tone="muted">Arize Phoenix + MCP</Badge>
        </div>
        <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          Glasshat doesn&apos;t just judge projects.{" "}
          <span className="bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-2)] bg-clip-text text-transparent">
            It audits the judge.
          </span>
        </h1>
        <p className="max-w-2xl text-lg text-[var(--color-muted)]">
          Glasshat ingests a pitch deck, a repo, and the evaluator&apos;s official rules, synthesizes
          a rubric that mirrors those rules, grounds every sub-score in retrieved evidence, then
          catches its own over-confidence and self-corrects the score in real time. An
          artifact-ingesting evaluation pipeline and a transparent fairness monitor — not a chatbot.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/participate"
            className="rounded-xl bg-[var(--color-accent)] px-6 py-2.5 font-medium text-white transition hover:opacity-90"
          >
            Score a submission →
          </Link>
          <Link
            href="/judge"
            className="rounded-xl border border-[var(--color-border)] px-6 py-2.5 font-medium transition hover:bg-[var(--color-surface)]"
          >
            Judge a cohort
          </Link>
        </div>
      </section>

      {/* Pipeline */}
      <section className="flex flex-col gap-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--color-muted)]">
          How it works
        </h2>
        <PipelineDiagram />
      </section>

      {/* Features */}
      <section className="grid gap-4 sm:grid-cols-2">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)] p-5"
          >
            <h3 className="font-medium">{f.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-[var(--color-muted)]">{f.body}</p>
          </div>
        ))}
      </section>

      {/* Two viewports */}
      <section className="flex flex-col gap-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--color-muted)]">
          One engine, two viewports
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link
            href="/judge"
            className="group rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)] p-6 transition hover:border-[var(--color-accent)]"
          >
            <h3 className="text-xl font-medium">I&apos;m a Judge</h3>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              Batch-rank a cohort against one synthesized rubric with the ordered tie-break, override
              a score at the human gate, and lock the official result.
            </p>
            <span className="mt-3 inline-block text-sm text-[var(--color-accent)]">Open /judge →</span>
          </Link>
          <Link
            href="/participate"
            className="group rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)] p-6 transition hover:border-[var(--color-accent)]"
          >
            <h3 className="text-xl font-medium">I&apos;m a Participant</h3>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              Score your submission, watch the audit self-correct its over-confident axis live, and
              iterate on your weakest criterion.
            </p>
            <span className="mt-3 inline-block text-sm text-[var(--color-accent)]">
              Open /participate →
            </span>
          </Link>
        </div>
        <p className="text-sm text-[var(--color-muted)]">
          Same engine. Different viewer. Different fairness.
        </p>
      </section>

      {/* Live presets */}
      <section className="rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)] p-5">
        <HomeStats />
      </section>
    </main>
  );
}
