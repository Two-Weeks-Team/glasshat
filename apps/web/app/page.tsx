import { HomeStats } from "@/components/HomeStats";
import ConstellationHero from "@/components/landing/ConstellationHero";
import KineticScore from "@/components/landing/KineticScore";
import RankFlipStory from "@/components/landing/RankFlipStory";
import SpotlightFinale from "@/components/landing/SpotlightFinale";
import { Reveal } from "@/components/Reveal";

// The six de Bono agent/hat spans the engine actually emits (engine.py: each
// agent + each hat opens its own glasshat.agent span). Honest names, not props.
const TRACE_SPANS: { name: string; tone: string; w: string }[] = [
  { name: "RubricSynthesizer", tone: "var(--color-accent-2)", w: "62%" },
  { name: "BluePlanner", tone: "var(--color-accent-2)", w: "44%" },
  { name: "SixHatPanel · White·Red·Yellow·Black·Green·Blue", tone: "var(--color-accent)", w: "100%" },
  { name: "Audit · self-correct (YELLOW pulled back)", tone: "var(--color-warn)", w: "70%" },
  { name: "BMADScorer", tone: "var(--color-good)", w: "38%" },
  { name: "ReportAssembler", tone: "var(--color-accent-3)", w: "30%" },
];

/** ARIZE emphasis — the Arize track is the whole point: the audit is *auditable*
 *  because every agent, every hat, and the self-correction is a trace span in
 *  Arize AX. Honest: AX tracing is live; the Phoenix-MCP calibration loop is wired
 *  (the credential-free demo runs the deterministic spike-D prior). */
function ArizeBand() {
  return (
    <Reveal>
      <section
        aria-label="Observability on Arize AX — every judgment is a trace span"
        className="mx-auto w-full max-w-5xl px-6 py-20"
      >
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[var(--color-accent-2)]">
          Built for the Arize track
        </p>
        <div className="mt-4 grid items-center gap-10 lg:grid-cols-[1.02fr_0.98fr]">
          <div className="flex flex-col gap-5">
            <h2 className="font-display text-[clamp(2rem,4.4vw,3.2rem)] font-bold leading-[1.06] tracking-[-0.02em]">
              The audit is <span className="text-gradient font-serif-italic font-medium">auditable</span>
              {" "}— on Arize&nbsp;AX.
            </h2>
            <p className="max-w-xl text-[0.98rem] leading-relaxed text-[var(--color-muted)]">
              Glasshat doesn&apos;t hide the judgment — it traces it. Every agent, every one of the
              six hats, and the self-correction itself opens its own{" "}
              <strong className="font-medium text-[var(--color-ink)]">trace span in Arize&nbsp;AX</strong>.
              You don&apos;t just get a score; you get the recorded trace of how it was judged — and
              audited.
            </p>
            <p className="max-w-xl text-[0.92rem] leading-relaxed text-[var(--color-muted)]">
              The calibration consultant reads a{" "}
              <strong className="font-medium text-[var(--color-ink)]">Phoenix dataset over MCP</strong>{" "}
              and writes each correction back — the learning loop is{" "}
              <span className="text-[var(--color-accent-2)]">wired</span>; the credential-free demo
              runs the deterministic spike-D prior, so the page never claims a live call it isn&apos;t
              making.
            </p>
            <div className="flex flex-wrap gap-2 pt-1">
              {["Arize AX · OpenInference/OTLP", "Phoenix · MCP (wired)", "every hat = a span"].map(
                (b) => (
                  <span
                    key={b}
                    className="rounded-full border border-[var(--color-accent-2)]/45 bg-[color-mix(in_oklch,var(--color-accent-2)_10%,transparent)] px-3 py-1 text-xs text-[var(--color-accent-2)]"
                  >
                    {b}
                  </span>
                ),
              )}
            </div>
          </div>

          {/* A faithful (illustrative) Arize-AX trace waterfall of the real spans. */}
          <div className="elevate rounded-2xl p-5" aria-hidden="true">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[var(--color-muted)]">
                glasshat · trace
              </span>
              <span className="font-mono text-[0.7rem] text-[var(--color-accent-2)]">Arize AX</span>
            </div>
            <ul className="mt-4 flex flex-col gap-2.5">
              {TRACE_SPANS.map((s) => (
                <li key={s.name} className="flex flex-col gap-1">
                  <span className="font-mono text-[0.68rem] text-[var(--color-muted)]">{s.name}</span>
                  <span className="h-2 rounded-full bg-[var(--color-surface-2)]">
                    <span
                      className="block h-2 rounded-full"
                      style={{
                        width: s.w,
                        background: `linear-gradient(90deg, ${s.tone}, color-mix(in oklch, ${s.tone} 45%, transparent))`,
                      }}
                    />
                  </span>
                </li>
              ))}
            </ul>
            <p className="mt-4 font-mono text-[0.64rem] leading-relaxed text-[var(--color-muted)]">
              Illustrative span waterfall · real span names from the live ADK runtime.
            </p>
          </div>
        </div>
      </section>
    </Reveal>
  );
}

export default function Home() {
  return (
    <main className="flex flex-col">
      {/* D · 시선 — the judge scores 9.0, then catches its own over-confidence */}
      <KineticScore />
      {/* F · 히어로 — the evaluation constellation + the H1 and primary CTAs */}
      <ConstellationHero />
      {/* E · 서사 — the audit changes who wins (rank-flip) */}
      <RankFlipStory />
      {/* ARIZE · the track's whole point — the audit is auditable on Arize AX */}
      <ArizeBand />
      {/* C · 마무리 와우 — the spotlight finale + closing CTA + honest live status */}
      <SpotlightFinale />
      {/* Quiet factual closer — live preset counts (real data) */}
      <section className="mx-auto w-full max-w-5xl px-6 pb-20">
        <Reveal>
          <div className="elevate rounded-3xl p-6">
            <HomeStats />
          </div>
        </Reveal>
      </section>
    </main>
  );
}
