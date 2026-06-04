"use client";

/**
 * RankFlipStory — the "E narrative" landing beat: a lenticular, dual-state rank
 * board that auto-tilts in 3D and, once scrolled into view, DEPTH-FLIPS a 4-project
 * cohort from amber "raw consensus" (an over-confident, thin-evidence project at #1)
 * to violet "with Glasshat audit" (a better-evidenced project rises to #1). Nobody
 * touches it — the audit plays on its own, exactly once.
 *
 * Honesty: the cohort, scores, ranks and deltas are ILLUSTRATIVE — a depiction of
 * the re-ranking *mechanism*, not live results. No invented precision claims.
 *
 * Perf: every animated property is transform/opacity (composite-only). The lenticular
 * oscillation is low-amplitude and PAUSES when the section is offscreen; the depth-flip
 * fires once via IntersectionObserver and cleans up. Heading text paints immediately.
 *
 * a11y: decorative tilt layers are aria-hidden; the section has an aria-label; an
 * aria-live region announces the new #1 after the flip; the AUDITED (resolved) state
 * is the accessible source of truth, and under prefers-reduced-motion the board renders
 * already-flipped with no tilt/oscillation/strobe.
 */

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import styles from "./RankFlipStory.module.css";

type Evidence = "strong" | "mid" | "thin";

interface CohortProject {
  /** Stable key + accessible name. */
  name: string;
  /** Rank in the raw, un-audited consensus (1 = top). */
  rawRank: number;
  /** Rank after the Glasshat audit (1 = top). DOM order follows this. */
  audRank: number;
  rawScore: string;
  audScore: string;
  /** Short, illustrative calibration note shown once audited. */
  delta: string;
  chips: { label: string; evidence: Evidence }[];
}

/**
 * Illustrative cohort. DOM order == audited order so the resolved (accessible)
 * state reads top-to-bottom #1..#4 without relying on motion.
 */
const COHORT: CohortProject[] = [
  {
    name: "Halcyon · grid-balancing model",
    rawRank: 3,
    audRank: 1,
    rawScore: "7.9",
    audScore: "8.6",
    delta: "calibrated ↑ from 7.9",
    chips: [
      { label: "deep evidence", evidence: "strong" },
      { label: "repo + deck grounded", evidence: "strong" },
    ],
  },
  {
    name: "Nimbus · pitch-perfect demo",
    rawRank: 1,
    audRank: 2,
    rawScore: "9.4",
    audScore: "8.1",
    delta: "pulled back −1.3 · within ±2.0 cap",
    chips: [
      { label: "thin evidence", evidence: "thin" },
      { label: "over-confident yellow hat", evidence: "thin" },
    ],
  },
  {
    name: "Tessera · multi-agent router",
    rawRank: 2,
    audRank: 3,
    rawScore: "8.6",
    audScore: "7.8",
    delta: "calibrated −0.8",
    chips: [
      { label: "mixed evidence", evidence: "mid" },
      { label: "partial grounding", evidence: "mid" },
    ],
  },
  {
    name: "Quillwright · doc-search tool",
    rawRank: 4,
    audRank: 4,
    rawScore: "7.1",
    audScore: "6.9",
    delta: "calibrated −0.2",
    chips: [
      { label: "mid evidence", evidence: "mid" },
      { label: "sparse retrieval", evidence: "thin" },
    ],
  },
];

const CHIP_DOT: Record<Evidence, string> = {
  strong: styles.chipDotStrong,
  mid: styles.chipDotMid,
  thin: styles.chipDotThin,
};

/** The project that holds #1 after the audit — announced + used as the resolved leader. */
const AUDITED_WINNER = COHORT.find((p) => p.audRank === 1)?.name.split(" · ")[0] ?? "the audited leader";

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export default function RankFlipStory() {
  const boardRef = useRef<HTMLDivElement>(null);
  const rowRefs = useRef<(HTMLLIElement | null)[]>([]);
  const regionRef = useRef<HTMLDivElement>(null);

  // `audited` is the resolved state of the board. It starts already-true under
  // reduced motion / SSR-safe default is false (raw) for the animated path.
  const [audited, setAudited] = useState(false);
  const [announce, setAnnounce] = useState("");

  useEffect(() => {
    const reduce = prefersReducedMotion();

    // Lay the rows out for a given state by translating each row from its DOM
    // (audited) slot to its target slot. Pure transform — no layout.
    const layout = (state: "raw" | "aud", rowStep: number) => {
      COHORT.forEach((p, domIndex) => {
        const el = rowRefs.current[domIndex];
        if (!el) return;
        const targetRank = state === "raw" ? p.rawRank : p.audRank;
        const dy = (targetRank - 1 - domIndex) * rowStep;
        el.style.transform = `translateY(${dy}px)`;
      });
    };

    // Measure the natural row pitch from layout geometry. getBoundingClientRect()
    // includes any active translateY(), so clear row transforms for the read and
    // restore them after — otherwise a resize while shifted yields a wrong step.
    const measureStep = (): number => {
      const a = rowRefs.current[0];
      const b = rowRefs.current[1];
      if (!a || !b) return 0;
      const ta = a.style.transform;
      const tb = b.style.transform;
      a.style.transform = "";
      b.style.transform = "";
      const step = b.getBoundingClientRect().top - a.getBoundingClientRect().top;
      a.style.transform = ta;
      b.style.transform = tb;
      return step;
    };

    // ── Reduced motion: resolve to AUDITED, static, no tilt/oscillation ──
    if (reduce) {
      setAudited(true);
      layout("aud", measureStep());
      setAnnounce(
        `Audit complete. ${AUDITED_WINNER} is ranked number one on calibrated, evidence-weighted scores.`,
      );
      const onResize = () => layout("aud", measureStep());
      window.addEventListener("resize", onResize);
      return () => window.removeEventListener("resize", onResize);
    }

    const board = boardRef.current;
    const region = regionRef.current;
    if (!board) return;

    // Track the resolved state across the rAF closure without re-subscribing.
    let isAudited = false;
    let rowStep = measureStep();
    layout("raw", rowStep);

    // ── 1) Lenticular auto-tilt: low-amplitude 3D sway, pausable offscreen ──
    // The rAF loop is fully torn down when the section leaves the viewport (no
    // idle per-frame callbacks) and restarted when it returns.
    let raf = 0; // 0 == loop not scheduled
    let scrollTilt = 0; // transient nudge during the flip "snap"

    const tick = (t: number) => {
      const rotY = Math.sin(t / 2600) * 5.5 + scrollTilt; // low amplitude
      const rotX = Math.cos(t / 3400) * 1.8;
      board.style.transform = `rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg)`;
      raf = requestAnimationFrame(tick);
    };
    const startLoop = () => {
      if (!raf) raf = requestAnimationFrame(tick);
    };
    const stopLoop = () => {
      if (raf) {
        cancelAnimationFrame(raf);
        raf = 0;
      }
    };
    startLoop();

    const onResize = () => {
      rowStep = measureStep();
      layout(isAudited ? "aud" : "raw", rowStep);
    };
    window.addEventListener("resize", onResize, { passive: true });

    // ── 3) Depth-flip orchestration: plays once on first reveal ──
    let played = false;
    let holdTimer: ReturnType<typeof setTimeout> | undefined;
    let snapTimer: ReturnType<typeof setInterval> | undefined;

    const playFlip = () => {
      if (played) return;
      played = true;
      holdTimer = setTimeout(() => {
        // Brief lenticular "snap" — a few small transient nudges — then resolve.
        let snaps = 0;
        snapTimer = setInterval(() => {
          snaps += 1;
          scrollTilt = snaps % 2 ? 4.5 : -4.5;
          if (snaps >= 3) {
            if (snapTimer) clearInterval(snapTimer);
            scrollTilt = 0;
            isAudited = true;
            setAudited(true);
            layout("aud", rowStep);
            setAnnounce(
              `Audit applied. The new number one is ${AUDITED_WINNER} — the better-evidenced project — after calibration pulled an over-confident score back within the cap.`,
            );
          }
        }, 180);
      }, 1100);
    };

    // ── 2) Visibility: drive the one-shot flip + pause oscillation offscreen ──
    let io: IntersectionObserver | undefined;
    if ("IntersectionObserver" in window) {
      io = new IntersectionObserver(
        (entries) => {
          for (const e of entries) {
            if (e.isIntersecting) startLoop();
            else stopLoop();
            region?.classList.toggle(styles.paused, !e.isIntersecting);
            if (e.isIntersecting && e.intersectionRatio > 0.45) playFlip();
          }
        },
        { threshold: [0, 0.45, 0.8] },
      );
      io.observe(board);
    } else {
      // No IO: still unbidden, just timer-driven.
      holdTimer = setTimeout(playFlip, 1400);
    }

    return () => {
      stopLoop();
      window.removeEventListener("resize", onResize);
      if (holdTimer) clearTimeout(holdTimer);
      if (snapTimer) clearInterval(snapTimer);
      io?.disconnect();
    };
  }, []);

  return (
    <section
      ref={regionRef}
      aria-label="The audit changes who wins: a cohort leaderboard re-ranks from raw consensus to evidence-calibrated scores. Illustrative."
      className={`relative flex min-h-[100svh] w-full flex-col justify-center overflow-hidden py-[clamp(4rem,12vh,8rem)] ${
        audited ? styles.audited : ""
      }`}
    >
      {/* decorative lenticular ridges sweeping the section */}
      <div className={styles.ridges} aria-hidden="true" />
      {/* connective gradient atmosphere: fade to --color-bg at top & bottom so the
          beat flows into its neighbours */}
      <div className={styles.edgeFadeTop} aria-hidden="true" />
      <div className={styles.edgeFadeBottom} aria-hidden="true" />

      <div className="relative mx-auto w-full max-w-[1320px] px-[clamp(1rem,4vw,3rem)]">
        <span className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)]/60 px-3 py-1.5 text-[clamp(0.68rem,1.4vw,0.78rem)] uppercase tracking-[0.22em] text-[var(--color-muted)] backdrop-blur-sm">
          <span
            className="h-2 w-2 rounded-full bg-[var(--color-warn)] animate-pulse-ring"
            aria-hidden="true"
          />
          Glasshat &middot; it audits the judge
        </span>

        {/* Heading paints immediately (no entrance animation gating text). */}
        <h2 className="font-display mt-5 max-w-[20ch] text-[clamp(2.4rem,6vw,5rem)] font-bold leading-[1.02] tracking-[-0.03em]">
          Same cohort.{" "}
          <em className="font-serif-italic text-[1.08em] font-medium text-gradient">Two truths.</em>{" "}
          The audit decides who wins.
        </h2>
        <p className="mt-5 max-w-[56ch] text-[clamp(1.05rem,2.1vw,1.32rem)] leading-relaxed text-[var(--color-muted)]">
          A raw AI panel hands the loudest, least-evidenced project the crown. Watch the board{" "}
          <b className="font-semibold text-[var(--color-ink)]">tilt</b> &mdash; and once
          calibration lands on retrieved evidence, a{" "}
          <b className="font-semibold text-[var(--color-ink)]">
            better-evidenced project rises to #1
          </b>
          . No one touches it; the audit happens on its own.
        </p>

        {/* ── the lenticular board ── */}
        <div className={`mt-[clamp(1.5rem,4.5vh,3rem)] ${styles.boardRegion}`}>
          {/* legend (decorative) */}
          <div
            className="mb-4 flex flex-wrap items-center gap-x-[clamp(0.6rem,2.5vw,1.6rem)] gap-y-2"
            aria-hidden="true"
          >
            <span className="flex items-center gap-2 text-[0.82rem] text-[var(--color-muted)]">
              <span className={`h-[0.85rem] w-[0.85rem] flex-none rounded-[3px] ${styles.swatchRaw}`} />
              Raw consensus
            </span>
            <span className="font-semibold text-[var(--color-muted)]">&rarr;</span>
            <span className="flex items-center gap-2 text-[0.82rem] text-[var(--color-muted)]">
              <span className={`h-[0.85rem] w-[0.85rem] flex-none rounded-[3px] ${styles.swatchAud}`} />
              With Glasshat audit
            </span>
            <span className="ml-auto flex items-center gap-2 text-[0.72rem] uppercase tracking-[0.16em] text-[var(--color-muted)]">
              <span className={`h-2 w-2 rounded-full ${styles.led}`} />
              auditing live
            </span>
          </div>

          <div
            ref={boardRef}
            className={`${styles.board} p-[clamp(1rem,2.6vw,1.75rem)]`}
          >
            <div className="mb-3 flex items-baseline justify-between gap-4 border-b border-[var(--color-border)] px-1.5 pb-5 pt-1.5">
              <div className="text-[clamp(1.15rem,2.4vw,1.5rem)] font-bold tracking-tight">
                Cohort ranking &middot;{" "}
                <span className={styles.ttlState}>
                  {audited ? "with Glasshat audit" : "raw consensus"}
                </span>
              </div>
              <div className="text-[0.74rem] tracking-wide text-[var(--color-muted)]">
                {audited
                  ? "evidence-calibrated · over-confidence pulled back"
                  : "over-confident · evidence not yet applied"}
              </div>
            </div>

            <ol className="flex list-none flex-col gap-2.5">
              {COHORT.map((p, i) => {
                const rank = audited ? p.audRank : p.rawRank;
                const score = audited ? p.audScore : p.rawScore;
                const isLeader = rank === 1;
                return (
                  <li
                    key={p.name}
                    ref={(el) => {
                      rowRefs.current[i] = el;
                    }}
                    data-label={p.name}
                    className={`grid grid-cols-[3rem_1fr_auto] items-center gap-x-[clamp(0.75rem,1.8vw,1.4rem)] rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface-2)]/70 px-[clamp(0.85rem,2vw,1.5rem)] py-[clamp(0.7rem,1.6vw,1.1rem)] ${styles.row} ${isLeader ? styles.leader : ""}`}
                  >
                    <span
                      className={`text-center text-[clamp(1.7rem,3.8vw,2.4rem)] font-medium ${styles.rank}`}
                    >
                      {rank}
                    </span>
                    <div className="min-w-0">
                      <div className="truncate text-[clamp(1rem,2.1vw,1.2rem)] font-semibold tracking-tight">
                        {p.name}
                      </div>
                      <div className="mt-1.5 flex flex-wrap gap-1.5">
                        {p.chips.map((c) => (
                          <span
                            key={c.label}
                            className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border border-[var(--color-border)] bg-[var(--color-surface)]/60 px-2 py-0.5 text-[0.66rem] text-[var(--color-muted)]"
                          >
                            <span
                              className={`h-[0.46rem] w-[0.46rem] flex-none rounded-full ${CHIP_DOT[c.evidence]}`}
                            />
                            {c.label}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="min-w-[6.4rem] justify-self-end text-right">
                      <span
                        className={`text-[clamp(1.5rem,3.4vw,2rem)] font-bold ${styles.scoreVal}`}
                      >
                        {score}
                      </span>
                      <span className="mt-0.5 block text-[0.6rem] uppercase tracking-[0.18em] text-[var(--color-muted)]">
                        score / 10
                      </span>
                      <span className={`mt-0.5 block text-[0.64rem] ${styles.delta}`}>{p.delta}</span>
                    </div>
                  </li>
                );
              })}
            </ol>

            <div
              className={`mt-4 flex items-center gap-3 rounded-xl px-4 py-3 text-[0.86rem] leading-snug text-[var(--color-ink)] ${styles.verdict}`}
            >
              <span
                className={`grid h-7 w-7 flex-none place-items-center rounded-lg font-bold text-[var(--color-ink)] ${styles.verdictMark}`}
                aria-hidden="true"
              >
                &#10003;
              </span>
              <span>
                <b className={`font-semibold ${styles.verdictName}`}>{AUDITED_WINNER}</b> rises to #1
                once evidence is weighed.{" "}
                <span className={styles.verdictMath}>
                  clip(score &minus; 0.8&middot;mean_delta, p25, p75)
                </span>
                , &plusmn;2.0 cap &mdash; a calibration prior recovered from held-out anchors.
              </span>
            </div>

            <p className="mt-3.5 flex items-start gap-1.5 text-[0.68rem] leading-snug text-[var(--color-muted)]">
              <svg width="13" height="13" viewBox="0 0 16 16" aria-hidden="true" className="mt-0.5 flex-none">
                <circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" strokeWidth="1.4" />
                <path d="M8 4.4v.2M8 7v4.6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
              <span>
                Projects, scores, ranks and deltas are{" "}
                <b className="font-semibold text-[var(--color-muted)]">illustrative</b> &mdash; a
                depiction of the re-ranking mechanism, not live results.
              </span>
            </p>
          </div>

          {/* aria-live announcer: states the resolved winner after the flip */}
          <p className="sr-only" role="status" aria-live="polite">
            {announce}
          </p>
        </div>

        <div className="mt-[clamp(1.75rem,5vh,3.5rem)]">
          <Link
            href="/judge"
            className="inline-flex items-center gap-2 rounded-xl bg-[var(--color-accent-strong)] px-5 py-3 text-[0.92rem] font-semibold text-[var(--color-ink)] shadow-[0_14px_34px_-16px_oklch(0.55_0.17_290/0.9)] transition-transform hover:-translate-y-0.5"
          >
            See the rank-flip on /judge <span aria-hidden="true">&rarr;</span>
          </Link>
        </div>
      </div>
    </section>
  );
}
