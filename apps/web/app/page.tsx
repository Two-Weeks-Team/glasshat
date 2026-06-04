import { HomeStats } from "@/components/HomeStats";
import CinematicScroll from "@/components/landing/CinematicScroll";
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

/** ARIZE emphasis (full-bleed) — the Arize track is the whole point: the audit is
 *  *auditable* because every agent, every hat, and the self-correction is a trace
 *  span in Arize AX. Honest: AX tracing is live; the Phoenix-MCP calibration loop
 *  is wired (the credential-free demo runs the deterministic spike-D prior). */
function ArizeBand() {
  return (
    <section
      aria-label="Observability on Arize AX — every judgment is a trace span"
      className="relative flex min-h-[100svh] w-full items-center justify-center overflow-hidden px-6 py-24"
    >
      {/* connective atmosphere so the beat bleeds between neighbours */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(60rem 40rem at 78% 30%, color-mix(in oklch, var(--color-accent-2) 16%, transparent), transparent 60%), linear-gradient(var(--color-bg), transparent 14%, transparent 86%, var(--color-bg))",
        }}
      />
      <Reveal className="mx-auto w-full max-w-6xl">
        <p className="font-mono text-sm uppercase tracking-[0.32em] text-[var(--color-accent-2)]">
          Built for the Arize track
        </p>
        <div className="mt-5 grid items-center gap-12 lg:grid-cols-[1fr_1.05fr]">
          <div className="flex flex-col gap-6">
            <h2 className="font-display text-[clamp(2.4rem,6vw,5rem)] font-bold leading-[1.02] tracking-[-0.03em]">
              The audit is{" "}
              <span className="text-gradient font-serif-italic font-medium">auditable</span>
              <br />— on Arize&nbsp;AX.
            </h2>
            <p className="max-w-xl text-[clamp(1.02rem,1.7vw,1.28rem)] leading-relaxed text-[var(--color-muted)]">
              Glasshat doesn&apos;t hide the judgment — it traces it. Every agent, every one of the
              six hats, and the self-correction itself opens its own{" "}
              <strong className="font-medium text-[var(--color-ink)]">trace span in Arize&nbsp;AX</strong>.
              You don&apos;t just get a score; you get the recorded trace of how it was judged — and
              audited.
            </p>
            <p className="max-w-xl text-[0.98rem] leading-relaxed text-[var(--color-muted)]">
              The calibration consultant reads a{" "}
              <strong className="font-medium text-[var(--color-ink)]">Phoenix dataset over MCP</strong>{" "}
              and writes each correction back — the learning loop is{" "}
              <span className="text-[var(--color-accent-2)]">wired</span>; the credential-free demo
              runs the deterministic spike-D prior, so the page never claims a live call it isn&apos;t
              making.
            </p>
            <div className="flex flex-wrap gap-2.5 pt-1">
              {["Arize AX · OpenInference/OTLP", "Phoenix · MCP (wired)", "every hat = a span"].map(
                (b) => (
                  <span
                    key={b}
                    className="rounded-full border border-[var(--color-accent-2)]/45 bg-[color-mix(in_oklch,var(--color-accent-2)_10%,transparent)] px-3.5 py-1.5 text-sm text-[var(--color-accent-2)]"
                  >
                    {b}
                  </span>
                ),
              )}
            </div>
          </div>

          {/* A faithful (illustrative) Arize-AX trace waterfall — the centerpiece. */}
          <div className="elevate rounded-3xl p-7 shadow-[0_30px_80px_-40px_oklch(0.72_0.17_290/0.5)]" aria-hidden="true">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs uppercase tracking-[0.2em] text-[var(--color-muted)]">
                glasshat · trace
              </span>
              <span className="font-mono text-xs font-semibold text-[var(--color-accent-2)]">
                Arize AX
              </span>
            </div>
            <ul className="mt-6 flex flex-col gap-4">
              {TRACE_SPANS.map((s) => (
                <li key={s.name} className="flex flex-col gap-1.5">
                  <span className="font-mono text-[0.78rem] text-[var(--color-muted)]">{s.name}</span>
                  <span className="h-3 rounded-full bg-[var(--color-surface-2)]">
                    <span
                      className="block h-3 rounded-full"
                      style={{
                        width: s.w,
                        background: `linear-gradient(90deg, ${s.tone}, color-mix(in oklch, ${s.tone} 45%, transparent))`,
                      }}
                    />
                  </span>
                </li>
              ))}
            </ul>
            <p className="mt-6 font-mono text-[0.72rem] leading-relaxed text-[var(--color-muted)]">
              Illustrative span waterfall · real span names from the live ADK runtime.
            </p>
          </div>
        </div>
      </Reveal>
    </section>
  );
}

export default function Home() {
  return (
    <main className="flex flex-col">
      <CinematicScroll />
      {/* D · 시선 — the judge scores 9.0, then catches its own over-confidence */}
      <div data-cine-scene>
        <KineticScore />
      </div>
      {/* F · 히어로 — the evaluation constellation + the H1 and primary CTAs */}
      <div data-cine-scene>
        <ConstellationHero />
      </div>
      {/* E · 서사 — the audit changes who wins (rank-flip) */}
      <div data-cine-scene>
        <RankFlipStory />
      </div>
      {/* ARIZE · the track's whole point — the audit is auditable on Arize AX */}
      <div data-cine-scene>
        <ArizeBand />
      </div>
      {/* C · 마무리 와우 — the spotlight finale + closing CTA + honest live status */}
      <div data-cine-scene>
        <SpotlightFinale />
      </div>
      {/* Quiet factual closer — live preset counts (real data) */}
      <section className="mx-auto w-full max-w-5xl px-6 pb-20 pt-8">
        <Reveal>
          <div className="elevate rounded-3xl p-6">
            <HomeStats />
          </div>
        </Reveal>
      </section>
    </main>
  );
}
