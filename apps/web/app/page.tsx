import Link from "next/link";

import { Badge } from "@/components/Badge";
import { HeroGraphic } from "@/components/HeroGraphic";
import { HomeStats } from "@/components/HomeStats";
import { PipelineDiagram } from "@/components/PipelineDiagram";
import { Reveal } from "@/components/Reveal";

export default function Home() {
  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-20 px-6 py-16">
      {/* ── Hero ── */}
      <section className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="flex flex-col gap-5">
          <div className="flex flex-wrap gap-2">
            <Badge tone="accent">Arize track</Badge>
            <Badge tone="muted">Gemini · Vertex AI</Badge>
            <Badge tone="muted">Google ADK</Badge>
            <Badge tone="muted">Phoenix + MCP</Badge>
          </div>
          <h1 className="text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
            Glasshat doesn&apos;t just judge projects.{" "}
            <span className="text-gradient">It audits the judge.</span>
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-[var(--color-muted)]">
            An artifact-ingesting evaluation pipeline that synthesizes a rubric from the official
            rules, grounds every sub-score in retrieved evidence, then catches its own
            over-confidence and self-corrects — live. Not a chatbot.
          </p>
          <div className="flex flex-wrap gap-3 pt-1">
            <Link
              href="/participate"
              className="hover-lift rounded-xl bg-[var(--color-accent)] px-6 py-2.5 font-medium text-white"
            >
              Score a submission →
            </Link>
            <Link
              href="/judge"
              className="hover-lift rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-6 py-2.5 font-medium"
            >
              Judge a cohort
            </Link>
          </div>
        </div>
        <Reveal className="relative">
          <div className="elevate rounded-3xl p-5">
            <HeroGraphic />
            <p className="mt-2 text-center text-xs text-[var(--color-muted)]">
              A low-evidence, over-confident score is pulled back to the calibrated value — in real time.
            </p>
          </div>
        </Reveal>
      </section>

      {/* ── How it works ── */}
      <Reveal>
        <section className="flex flex-col gap-4">
          <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--color-muted)]">
            How it works
          </h2>
          <PipelineDiagram />
        </section>
      </Reveal>

      {/* ── Bento features ── */}
      <section className="flex flex-col gap-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--color-muted)]">
          Why it&apos;s different
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Reveal className="sm:col-span-2">
            <article className="elevate hover-lift flex h-full flex-col justify-between rounded-3xl p-6">
              <div>
                <Badge tone="warn">the flagship</Badge>
                <h3 className="mt-3 text-2xl font-semibold">It audits its own scores</h3>
                <p className="mt-2 max-w-xl text-sm leading-relaxed text-[var(--color-muted)]">
                  An over-confident, low-evidence assessment is pulled back toward calibrated past
                  evaluations — validated math, not theatre — with the 3D evaluation graph reshaping
                  as it happens.
                </p>
              </div>
              <code className="mt-4 inline-block w-fit rounded-lg bg-[var(--color-surface-2)] px-3 py-1.5 font-mono text-xs text-[var(--color-muted)]">
                clip(score − 0.8·mean_delta, p25, p75)
              </code>
            </article>
          </Reveal>
          <Reveal delayMs={80}>
            <article className="hover-lift h-full rounded-3xl border border-[var(--color-accent)]/40 bg-[color-mix(in_oklch,var(--color-accent)_7%,var(--color-surface))] p-6">
              <h3 className="font-medium">No vector database</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--color-muted)]">
                Retrieval is in-code — Vertex embeddings + cosine + BM25 + RRF over an in-memory
                index. No Qdrant.
              </p>
            </article>
          </Reveal>
          <Reveal delayMs={40}>
            <article className="elevate hover-lift h-full rounded-3xl p-6">
              <h3 className="font-medium">Rubric-aware, not one-size-fits-all</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--color-muted)]">
                Each criterion maps onto a shared BMAD vocabulary, so scores stay comparable across
                rubrics — and the official 4×25% + ordered tie-break is honored exactly.
              </p>
            </article>
          </Reveal>
          <Reveal delayMs={80}>
            <article className="elevate hover-lift h-full rounded-3xl p-6">
              <h3 className="font-medium">Every score is grounded</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--color-muted)]">
                Six perspectives each retrieve evidence and cite it — every step is a Phoenix span
                you can inspect.
              </p>
            </article>
          </Reveal>
          <Reveal delayMs={120}>
            <article className="elevate hover-lift h-full rounded-3xl p-6">
              <h3 className="font-medium">Built for the Arize track</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--color-muted)]">
                Gemini (Vertex AI) + Google ADK, with Arize Phoenix observability and the Phoenix MCP
                server consulted at runtime.
              </p>
            </article>
          </Reveal>
        </div>
      </section>

      {/* ── Two viewports ── */}
      <Reveal>
        <section className="flex flex-col gap-4">
          <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--color-muted)]">
            One engine, two viewports
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Link
              href="/judge"
              className="elevate hover-lift rounded-3xl p-6 transition"
            >
              <h3 className="text-xl font-medium">I&apos;m a Judge</h3>
              <p className="mt-2 text-sm text-[var(--color-muted)]">
                Batch-rank a cohort with the ordered tie-break, override a score at the human gate,
                and lock the official result.
              </p>
              <span className="mt-3 inline-block text-sm text-[var(--color-accent)]">Open /judge →</span>
            </Link>
            <Link
              href="/participate"
              className="elevate hover-lift rounded-3xl p-6 transition"
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
      </Reveal>

      {/* ── Live presets ── */}
      <Reveal>
        <section className="elevate rounded-3xl p-6">
          <HomeStats />
        </section>
      </Reveal>
    </main>
  );
}
