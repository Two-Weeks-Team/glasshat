"use client";

import { useEffect, useRef, useState } from "react";

import styles from "./KineticScore.module.css";

/**
 * KineticScore — the "D 시선" (attention hook), the first scroll section of the
 * cinematic landing.
 *
 * A colossal, over-confident score (9.0, amber) assembles out of flying
 * letterform shards, holds, then mechanically odometer-rolls down to the
 * calibrated 7.6 (violet) with a ±2.0 cap delta bar and a verdict caption. The
 * clip(...) correction math streams as fine micro-type behind the number.
 *
 * Rendering strategy — the markup defaults to the *resolved / calibrated*
 * state (7.6 violet, bar filled, verdict = calibrated). That makes SSR, no-JS,
 * and prefers-reduced-motion all correct with zero work and no flash of wrong
 * text. Only when motion is allowed AND the section scrolls into view does the
 * effect rewind to the raw 9.0 start and play the correction forward.
 *
 * Perf: the scene animates transform/opacity only; the streaming micro-type
 * drift runs solely while in view (the `running` class) and is removed on
 * exit/unmount. a11y: decorative layers are aria-hidden, the stage is
 * role="img" with a live aria-label, and an aria-live region announces the
 * corrected score.
 */

// Odometer reels (top → bottom). Each reel starts showing its first entry; the
// effect translates the reel up by `index * 1em` to reveal the target glyph.
const TENS_REEL = ["9", "8", "7"] as const; // 9 → 7
const ONES_REEL = ["0", "9", "8", "7", "6"] as const; // 0 → 6
const RAW_TENS_INDEX = 0; // "9"
const RAW_ONES_INDEX = 0; // "0"
const FINAL_TENS_INDEX = TENS_REEL.indexOf("7");
const FINAL_ONES_INDEX = ONES_REEL.indexOf("6");

// Fine micro-type: the correction math, set behind the number. Duplicated once
// for a seamless drift loop (the keyframe translates by -50%).
const FORMULA_BITS = [
  "clip( score − 0.8 · mean_delta , p25 , p75 )",
  "±2.0 cap",
  "spike-D anchors · evidence-bucketed",
  "YELLOW hat → optimism flagged",
  "Δ = 9.0 − 7.6 = 1.4",
  "p25 ≤ calibrated ≤ p75",
  "audit the judge — including itself",
];
const buildStream = (bits: readonly string[], reps: number): string => {
  const unit = `${bits.join("   ·   ")}   ·   `;
  const single = unit.repeat(reps);
  return single + single; // duplicate for the seamless -50% loop
};
const STREAM_1 = buildStream(FORMULA_BITS, 3);
const STREAM_2 = buildStream([...FORMULA_BITS].reverse(), 3);
const STREAM_3 = buildStream(
  ["evidence > assumption", "confident · fast · unaccountable → audited"],
  6,
);

const prefersReducedMotion = (): boolean =>
  typeof window === "undefined" ||
  typeof window.matchMedia === "undefined" ||
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

interface Shard {
  glyph: string;
  sx: string;
  sy: string;
  sr: string;
  sd: string;
  size: string;
}

const SHARD_GLYPHS = ["9", "/", "0", ".", "9", "\\", "0", "9", "|", "0"];

const makeShards = (): Shard[] => {
  const shards: Shard[] = [];
  for (let i = 0; i < 22; i += 1) {
    const ang = (i / 22) * Math.PI * 2 + Math.random();
    const dist = 38 + Math.random() * 46;
    shards.push({
      glyph: SHARD_GLYPHS[i % SHARD_GLYPHS.length],
      sx: `${(Math.cos(ang) * dist).toFixed(1)}vmin`,
      sy: `${(Math.sin(ang) * dist * 0.7).toFixed(1)}vmin`,
      sr: `${(Math.random() * 80 - 40).toFixed(0)}deg`,
      sd: `${(Math.random() * 280).toFixed(0)}ms`,
      size: `${(1.6 + Math.random() * 3.4).toFixed(1)}vmin`,
    });
  }
  return shards;
};

const RAW_VERDICT = "9.0 — over-confident, low-evidence (the optimism hat)";
const CALIBRATED_VERDICT = "7.6 — pulled to where the retrieved evidence holds";

export default function KineticScore() {
  const sectionRef = useRef<HTMLElement | null>(null);
  const tensReelRef = useRef<HTMLSpanElement | null>(null);
  const onesReelRef = useRef<HTMLSpanElement | null>(null);
  const scoreRef = useRef<HTMLDivElement | null>(null);

  // State drives the React-owned bits (verdict text/tag, shard list, classes).
  // Default = resolved/calibrated so SSR + no-JS + reduced-motion are correct.
  const [running, setRunning] = useState(false); // micro-type drift active
  const [phase, setPhase] = useState<"raw" | "calibrated">("calibrated");
  const [shards, setShards] = useState<Shard[]>([]);
  const [assembling, setAssembling] = useState(false);
  const [barPending, setBarPending] = useState(false);
  const [liveScore, setLiveScore] = useState<string>(CALIBRATED_VERDICT);

  // Translate a reel to a given glyph index. `animate` toggles the CSS
  // transition (we snap to the start with it off, then roll with it on).
  const setReel = (
    reel: HTMLSpanElement | null,
    index: number,
    animate: boolean,
  ): void => {
    if (!reel) return;
    if (animate) {
      reel.classList.add(styles.animate);
    } else {
      reel.classList.remove(styles.animate);
      // force reflow so a later re-enabled transition applies cleanly
      void reel.offsetHeight;
    }
    reel.style.transform = `translateY(-${index}em)`;
  };

  useEffect(() => {
    const section = sectionRef.current;
    const scoreEl = scoreRef.current;
    if (!section || !scoreEl) return;

    // Reduced motion / no animation support: keep the resolved default. Nothing
    // to wire up — the markup already renders 7.6 violet, bar filled, verdict
    // calibrated. (No reels to move; their CSS rest state shows 9/0 top, but we
    // want 7/6 — so still position them statically.)
    if (prefersReducedMotion()) {
      setReel(tensReelRef.current, FINAL_TENS_INDEX, false);
      setReel(onesReelRef.current, FINAL_ONES_INDEX, false);
      return;
    }

    // Pre-position the reels at the resolved value before any scene runs, so a
    // late/never-firing observer still shows the correct number.
    setReel(tensReelRef.current, FINAL_TENS_INDEX, false);
    setReel(onesReelRef.current, FINAL_ONES_INDEX, false);

    let hasRun = false;
    const timers: ReturnType<typeof setTimeout>[] = [];

    const runScene = (): void => {
      if (hasRun) return;
      hasRun = true;

      // Rewind to the raw, over-confident start: 9.0, amber, bar empty.
      setReel(tensReelRef.current, RAW_TENS_INDEX, false);
      setReel(onesReelRef.current, RAW_ONES_INDEX, false);
      setPhase("raw");
      setBarPending(true);
      setLiveScore(RAW_VERDICT);

      // 1) shards fly in and assemble into the raw 9.0
      setShards(makeShards());
      setAssembling(true);

      // 2) HOLD on 9.0, then the AUDIT FIRES: odometer rolls 9.0 → 7.6.
      timers.push(
        setTimeout(() => {
          setAssembling(false);
          setShards([]);

          setReel(tensReelRef.current, FINAL_TENS_INDEX, true);
          setReel(onesReelRef.current, FINAL_ONES_INDEX, true);

          // delta bar streams in
          setBarPending(false);

          // color/weight shift to calibrated violet mid-roll (the "pull")
          timers.push(setTimeout(() => setPhase("calibrated"), 350));

          // 3) settle: verdict + aria-live announce the corrected value
          timers.push(
            setTimeout(() => {
              setLiveScore(CALIBRATED_VERDICT);
              scoreEl.setAttribute(
                "aria-label",
                "Calibrated score 7.6, corrected from 9.0",
              );
            }, 1300),
          );
        }, 2400),
      );
    };

    let started = false;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setRunning(true); // start the in-view micro-type drift
            if (!started) {
              started = true;
              timers.push(setTimeout(runScene, 500));
            }
          } else {
            setRunning(false); // pause drift when scrolled away (Speed Index)
          }
        }
      },
      { threshold: 0.5 },
    );
    observer.observe(section);

    // Safety: if the observer never reports intersection, play once anyway.
    const safety = setTimeout(() => {
      if (!started) {
        started = true;
        setRunning(true);
        runScene();
      }
    }, 1600);
    timers.push(safety);

    return () => {
      observer.disconnect();
      for (const t of timers) clearTimeout(t);
    };
  }, []);

  const scoreClass = `${styles.score} ${phase === "raw" ? styles.raw : ""} ${
    assembling ? styles.assembling : ""
  }`.trim();
  const verdictClass = `${styles.verdict} ${
    phase === "calibrated" ? styles.calibrated : ""
  }`.trim();
  const deltabarClass = `${styles.deltabar} ${
    barPending ? styles.pending : ""
  }`.trim();
  const microClass = `${styles.microtype} ${running ? styles.running : ""}`.trim();
  // The static-resolved tag/text the markup ships with; the live label
  // announces transitions for assistive tech.
  const isCalibrated = phase === "calibrated";

  return (
    <section
      ref={sectionRef}
      className={`${styles.section} hero-mesh`}
      aria-labelledby="kinetic-score-kicker"
    >
      <div className={styles.field} aria-hidden="true" />

      <div className={microClass} aria-hidden="true">
        <div className={`${styles.stream} ${styles.s1}`}>{STREAM_1}</div>
        <div className={`${styles.stream} ${styles.s2}`}>{STREAM_2}</div>
        <div className={`${styles.stream} ${styles.s3}`}>{STREAM_3}</div>
      </div>

      <div className={styles.stage}>
        <p className={styles.kicker} id="kinetic-score-kicker">
          the judge scores <b>9.0</b> · then catches its own over-confidence
        </p>

        {/* The colossal numeral. Odometer reels per digit. */}
        <div
          ref={scoreRef}
          className={scoreClass}
          role="img"
          aria-label="Calibrated score 7.6, corrected down from an over-confident 9.0"
        >
          <span className={styles.digit}>
            <span ref={tensReelRef} className={styles.reel}>
              {TENS_REEL.map((d) => (
                <span key={d}>{d}</span>
              ))}
            </span>
          </span>
          <span className={styles.dotSep}>.</span>
          <span className={styles.digit}>
            <span ref={onesReelRef} className={styles.reel}>
              {ONES_REEL.map((d) => (
                <span key={d}>{d}</span>
              ))}
            </span>
          </span>
          <span className={styles.shardwrap} aria-hidden="true">
            {shards.map((s, i) => (
              <span
                key={i}
                className={styles.shard}
                style={
                  {
                    "--sx": s.sx,
                    "--sy": s.sy,
                    "--sr": s.sr,
                    "--sd": s.sd,
                    fontSize: s.size,
                  } as React.CSSProperties
                }
              >
                {s.glyph}
              </span>
            ))}
          </span>
        </div>

        {/* ±2.0 cap delta bar */}
        <div className={deltabarClass} aria-hidden="true">
          <div className={styles.track}>
            <span className={`${styles.cap} ${styles.capL}`} />
            <span className={`${styles.cap} ${styles.capR}`} />
            <span className={styles.fill} />
          </div>
          <div className={styles.labels}>
            <span>&minus;2.0 cap</span>
            <span className={styles.mid}>pulled &minus;1.4 toward the evidence</span>
            <span>+2.0 cap</span>
          </div>
        </div>

        <p className={verdictClass}>
          <span className={styles.tag}>{isCalibrated ? "calibrated" : "raw"}</span>
          <span>
            <strong>{isCalibrated ? "7.6" : "9.0"}</strong>
            {isCalibrated
              ? " — pulled to where the retrieved evidence holds"
              : " — over-confident, low-evidence (the optimism hat)"}
          </span>
        </p>

        {/* aria-live announcer for the correction (text is the source of truth
            for assistive tech; the visual numeral above is role="img"). */}
        <p className="sr-only" aria-live="polite">
          {liveScore}
        </p>

        <p className={styles.illus}>
          Illustrative correction ·{" "}
          <span className={styles.formula}>
            clip(score &minus; 0.8·mean_delta, p25, p75)
          </span>
          , ±2.0 cap · prior recovered from held-out spike-D anchors.
        </p>
      </div>
    </section>
  );
}
