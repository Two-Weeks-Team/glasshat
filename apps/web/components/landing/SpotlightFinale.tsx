"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import styles from "./SpotlightFinale.module.css";

/* Honest illustrative numbers: an over-confident 9.0 pulled back to a
   calibrated 7.6 — the same correction the real engine applies on retrieved
   evidence. These are the ONLY numerals shown; no invented metrics. */
const OVER = 9.0;
const CAL = 7.6;

const HEALTH_URL = "https://glasshat-api-o366v7tl2q-uc.a.run.app/health";

const HATS = ["white", "red", "yellow", "black", "green", "blue"] as const;

const prefersReduced = (): boolean =>
  typeof window !== "undefined" &&
  typeof window.matchMedia === "function" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * SpotlightFinale — the closing WOW of the landing page.
 *
 * A near-black stage. A volumetric follow-spot sweeps in on its own
 * (IntersectionObserver, never hover/click) and catches a single submission
 * panel; the inflated amber score recedes to its calibrated violet value inside
 * a luminous ±2.0 cap bracket, while the de Bono YELLOW hat dims. Fires ONCE,
 * cleans up its timers/RAF, and renders the resolved static scene under
 * `prefers-reduced-motion`.
 */
export default function SpotlightFinale() {
  const stageRef = useRef<HTMLElement | null>(null);
  const scoreRef = useRef<HTMLSpanElement | null>(null);
  const played = useRef(false);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const raf = useRef<number | null>(null);

  // Scene state, all transform/opacity-driven through module classes.
  const [lit, setLit] = useState(false);
  const [capped, setCapped] = useState(false);
  const [calibrated, setCalibrated] = useState(false);
  const [corrected, setCorrected] = useState(false);
  const [score, setScore] = useState(OVER);
  const [tag, setTag] = useState("over-confident");
  const [phase, setPhase] = useState("scanning");
  const [phaseCopy, setPhaseCopy] = useState("following the beam onto the verdict");
  // Polite AT announcement of the corrected value.
  const [announce, setAnnounce] = useState("Spotlight finding the submission…");
  // The visible corrected-value line (paints after the recede resolves).
  const [resolvedLine, setResolvedLine] = useState(false);

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;

    const after = (ms: number, fn: () => void) => {
      timers.current.push(setTimeout(fn, ms));
    };

    // Per-frame value is written straight to the DOM (ref + textContent) so the
    // rAF loop avoids a React setState + reconciliation on every animation frame.
    // React state is committed only once at the end to persist the resolved value.
    const animateScore = (from: number, to: number, ms: number, done: () => void) => {
      let start: number | null = null;
      const frame = (t: number) => {
        if (start === null) start = t;
        const p = Math.min((t - start) / ms, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const node = scoreRef.current;
        if (node) node.textContent = (from + (to - from) * eased).toFixed(1);
        if (p < 1) {
          raf.current = requestAnimationFrame(frame);
        } else {
          const node2 = scoreRef.current;
          if (node2) node2.textContent = to.toFixed(1);
          setScore(to);
          done();
        }
      };
      raf.current = requestAnimationFrame(frame);
    };

    // Reduced motion: render the already-resolved scene at rest.
    const resolveStatic = () => {
      setLit(true);
      setScore(CAL);
      setCapped(true);
      setCalibrated(true);
      setCorrected(true);
      setTag("calibrated");
      setPhase("calibrated");
      setPhaseCopy("optimism pulled back into the ±2.0 cap");
      setResolvedLine(true);
      setAnnounce(
        "Calibrated to 7.6 of 10 (illustrative). Over-confident 9.0 pulled back via clip(score − 0.8·mean_delta) within the ±2.0 cap.",
      );
    };

    // The autonomous performance: spotlight sweeps in, then the score recedes.
    const perform = () => {
      if (played.current) return;
      played.current = true;

      if (prefersReduced()) {
        resolveStatic();
        return;
      }

      setLit(true);
      setScore(OVER);

      after(2200, () => {
        setPhase("caught");
        setPhaseCopy("YELLOW hat lit amber — optimism, thin evidence");
      });

      after(3000, () => {
        setCapped(true);
        setPhase("auditing");
        setPhaseCopy("recovering the spike-D calibration prior");
        setAnnounce(
          "Auditing the judge — recovering a calibration prior from held-out spike-D anchors.",
        );
      });

      after(3700, () => {
        setCalibrated(true);
        setTag("calibrated");
        setCorrected(true);
        animateScore(OVER, CAL, 1600, () => {
          setPhase("calibrated");
          setPhaseCopy("amber → violet · evidence-supported");
          setResolvedLine(true);
          setAnnounce(
            "Pulled back to 7.6 of 10 · clip(9.0 − 0.8·mean_delta) within ±2.0.",
          );
        });
      });
    };

    // Reduced motion still resolves immediately (no observer wait).
    if (prefersReduced()) {
      perform();
      return;
    }

    let observer: IntersectionObserver | null = null;
    if (typeof IntersectionObserver !== "undefined") {
      observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
              perform();
              observer?.disconnect();
              break;
            }
          }
        },
        { threshold: [0, 0.5, 1] },
      );
      observer.observe(stage);
    }
    // Safety net only when IntersectionObserver is unavailable, and only if the
    // stage is actually in view — never auto-play the one-shot finale off-screen.
    const fallback =
      observer === null
        ? setTimeout(() => {
            const rect = stage.getBoundingClientRect();
            const inView =
              rect.top < window.innerHeight * 0.9 &&
              rect.bottom > window.innerHeight * 0.1;
            if (inView) perform();
          }, 700)
        : null;

    return () => {
      observer?.disconnect();
      if (fallback !== null) clearTimeout(fallback);
      for (const id of timers.current) clearTimeout(id);
      timers.current = [];
      if (raf.current !== null) cancelAnimationFrame(raf.current);
    };
  }, []);

  const panelClass = [
    styles.panel,
    capped ? styles.capped : "",
    calibrated ? styles.calibrated : "",
  ]
    .filter(Boolean)
    .join(" ");

  const hatsClass = [styles.hats, corrected ? styles.corrected : ""]
    .filter(Boolean)
    .join(" ");

  return (
    <section
      ref={stageRef}
      aria-label="A theatrical stage where a follow-spot catches an AI evaluation and the over-confident score is corrected to its calibrated value"
      className={`${styles.stage}${lit ? ` ${styles.lit}` : ""}`}
    >
      {/* connective top-edge atmosphere: the finale emerges from the section above */}
      <div className={styles.topfade} aria-hidden="true" />

      {/* decorative volumetric light */}
      <div className={styles.cone} aria-hidden="true" />
      <div className={styles.catch} aria-hidden="true" />
      <div className={styles.floor} aria-hidden="true" />

      <div className={styles.wrap}>
        <div className={styles.lede}>
          <span className={styles.eyebrow}>
            <span className={styles.eyebrowDot} aria-hidden="true" />
            Glasshat &middot; it audits the judge
          </span>
          <h2 className={styles.headline}>
            The judge catches <em>its own</em> over-confidence &mdash; live.
          </h2>
          <p className={styles.sub}>
            A rubric-aware AI evaluator scores with a six-hat panel, grounds every
            sub-score in retrieved evidence, then pulls its own optimism back to
            where the evidence actually supports. Watch the spotlight find one
            verdict and correct it.
          </p>

          <div className={styles.links}>
            <Link
              href="/participate"
              className={`${styles.btn} ${styles.btnPrimary} bg-[var(--color-accent-strong)] text-white`}
            >
              Watch a single audit &rarr;
            </Link>
            <Link href="/judge" className={styles.btn}>
              See rank-flip &rarr;
            </Link>
          </div>

          <p className={styles.meta}>
            Live API health:{" "}
            <a href={HEALTH_URL} target="_blank" rel="noreferrer">
              <code>{'API /health → {"status":"ok"}'}</code>
            </a>
            <br />
            Gemini 3.1 Flash-Lite on Vertex AI &middot; Google ADK &middot; Arize AX
            + Phoenix-MCP calibration loop (wired) &middot; Apache-2.0
          </p>
        </div>

        {/* the caught subject: one submission being judged */}
        <div className={panelClass} role="group" aria-label="Live evaluation panel for one submission">
          <div className={styles.panelHead}>
            <span className={styles.panelTitle}>Submission &middot; YELLOW hat (optimism)</span>
            <span className={styles.panelTag}>{tag}</span>
          </div>

          <div className={styles.scorewrap}>
            <span className={`${styles.bracket} ${styles.bracketL}`} aria-hidden="true" />
            <span className={styles.score} aria-hidden="true">
              <span ref={scoreRef}>{score.toFixed(1)}</span>
              <span className={styles.scoreout}> /10</span>
            </span>
            <span className={`${styles.bracket} ${styles.bracketR}`} aria-hidden="true" />
            <span className={styles.caplabel} aria-hidden="true">
              &plusmn;2.0 correction cap
            </span>
          </div>
          <p className={styles.illus}>illustrative score &middot; the math runs on real evidence</p>

          {/* surfaced corrected value, announced politely to AT. The visible
             text doubles as the live-region content, so there is exactly one
             announcement per state change (no duplicate sr-only mirror). */}
          <p className={styles.delta} aria-live="polite">
            {resolvedLine ? (
              <span>
                Pulled back to <b>7.6</b> of 10 &middot;{" "}
                <span className={styles.math}>clip(9.0 &minus; 0.8&middot;mean_delta) within &plusmn;2.0</span>{" "}
                &middot; illustrative score &middot; the math runs on real evidence
              </span>
            ) : (
              <span>{announce}</span>
            )}
          </p>

          <div className={styles.status}>
            <span className={styles.now}>{phase}</span> &mdash; {phaseCopy}
          </div>
        </div>
      </div>

      {/* faint six-hat panel at the stage edge */}
      <div className={hatsClass} aria-hidden="true">
        {HATS.map((hat) => (
          <span
            key={hat}
            className={`${styles.hat}${hat === "yellow" ? ` ${styles.hatYellow}` : ""}`}
          />
        ))}
      </div>
    </section>
  );
}
