"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import styles from "./ConstellationHero.module.css";

/* ------------------------------------------------------------------ *
 * Canvas color tokens.
 *
 * OKLCH can't be passed to 2D-canvas fill/stroke reliably across engines, so the
 * six-hat palette is resolved here to literal RGB strings. These mirror the
 * project's @theme tokens (globals.css): violet=--color-accent, cyan=
 * --color-accent-2, magenta=--color-accent-3, green=--color-good, amber=
 * --color-warn, ink=--color-ink, muted=--color-muted. The DOM (H1, CTAs,
 * legend, readout) still uses the live CSS vars — only the <canvas> uses these.
 *
 * Hat → token map:  White=ink · Red=magenta(accent-3) · Yellow=warn(amber) →
 * calibrated violet(accent) · Black=muted · Green=good · Blue=cyan(accent-2).
 * ------------------------------------------------------------------ */
const C = {
  violet: "rgb(166,128,246)",
  cyan: "rgb(122,206,230)",
  magenta: "rgb(232,150,212)",
  green: "rgb(118,212,158)",
  amber: "rgb(238,196,104)",
  ink: "rgb(244,244,250)",
  muted: "rgb(176,180,200)",
  star: "225,228,248",
} as const;

interface SceneNode {
  id: string;
  x: number;
  y: number;
  w: number;
  ev: number;
  col: string;
  score: number;
  /** Yellow only: over-confident origin + calibrated target. */
  ox?: number;
  oy?: number;
  colCal?: string;
  scoreCal?: number;
  special?: boolean;
}

/** Six hat-criterion stars placed by (score, weight, evidence depth). Fractions
 *  of the field (0..1). Yellow carries a second, over-confident origin (ox,oy)
 *  it is pulled back FROM toward its calibrated home (x,y). */
const NODES: readonly SceneNode[] = [
  { id: "white", x: 0.3, y: 0.24, w: 1.1, ev: 0.92, col: C.ink, score: 8.2 },
  { id: "red", x: 0.62, y: 0.18, w: 0.95, ev: 0.7, col: C.magenta, score: 7.4 },
  { id: "black", x: 0.74, y: 0.46, w: 1.15, ev: 0.85, col: C.muted, score: 8.6 },
  { id: "green", x: 0.48, y: 0.62, w: 1.0, ev: 0.8, col: C.green, score: 7.9 },
  { id: "blue", x: 0.24, y: 0.54, w: 1.05, ev: 0.88, col: C.cyan, score: 8.1 },
  {
    id: "yellow",
    x: 0.66,
    y: 0.74,
    w: 0.92,
    ev: 0.34,
    ox: 0.885,
    oy: 0.135,
    col: C.amber,
    colCal: C.violet,
    score: 9.0,
    scoreCal: 7.6,
    special: true,
  },
] as const;

/** Which stars draw lines to each other as the constellation resolves. */
const EDGES: ReadonlyArray<readonly [string, string]> = [
  ["white", "red"],
  ["white", "blue"],
  ["red", "black"],
  ["black", "green"],
  ["blue", "green"],
  ["green", "yellow"],
  ["black", "yellow"],
  ["white", "green"],
];

// Phase durations (ms) — autonomous arrival, never hover/click driven.
const T_SETTLE = 1400; // star field calms in
const T_DRAW = 1700; // constellation lines draw themselves
const T_HOLD = 700; // hold the over-confident shape
const T_PULL = 2200; // yellow recedes to its calibrated home

interface SceneStar {
  x: number;
  y: number;
  z: number;
  tw: number;
  tws: number;
}

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const easeInOut = (t: number) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
const clamp01 = (t: number) => (t < 0 ? 0 : t > 1 ? 1 : t);

function parseRGB(str: string): [number, number, number] {
  const m = str.match(/(\d+\.?\d*)/g);
  if (!m || m.length < 3) return [255, 255, 255];
  return [parseFloat(m[0]), parseFloat(m[1]), parseFloat(m[2])];
}
function blend(a: string, b: string, t: number): string {
  const ca = parseRGB(a);
  const cb = parseRGB(b);
  return `rgb(${Math.round(lerp(ca[0], cb[0], t))},${Math.round(lerp(ca[1], cb[1], t))},${Math.round(lerp(ca[2], cb[2], t))})`;
}
function withAlpha(rgb: string, a: number): string {
  const c = parseRGB(rgb);
  return `rgba(${c[0]},${c[1]},${c[2]},${clamp01(a).toFixed(3)})`;
}

function nodeById(id: string): SceneNode {
  const n = NODES.find((node) => node.id === id);
  // Edges only reference defined node ids; this fallback satisfies strict typing.
  return n ?? NODES[0];
}

/** Pixel position of a node given the global pull progress (yellow travels). */
function nodePos(n: SceneNode, pullT: number, w: number, h: number) {
  let fx = n.x;
  let fy = n.y;
  if (n.special && n.ox !== undefined && n.oy !== undefined) {
    const e = easeInOut(pullT);
    fx = lerp(n.ox, n.x, e);
    fy = lerp(n.oy, n.y, e);
  }
  return { x: fx * w, y: fy * h };
}

const YELLOW = nodeById("yellow");

type ReadoutPhase = "warn" | "pulling" | "cal";

export default function ConstellationHero() {
  const sectionRef = useRef<HTMLElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Readout state, driven by the rAF loop (React owns the DOM, not direct writes).
  const [phase, setPhase] = useState<ReadoutPhase>("warn");
  const [toScore, setToScore] = useState<number>(YELLOW.score);

  useEffect(() => {
    const canvas = canvasRef.current;
    const section = sectionRef.current;
    if (!canvas || !section) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduce =
      typeof window !== "undefined" &&
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const DPR = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    let W = 0;
    let H = 0;
    let stars: SceneStar[] = [];
    let raf = 0;
    let t0: number | null = null;
    let started = false;
    let finished = false;
    let lastPhase: ReadoutPhase = "warn";

    function resize() {
      if (!canvas || !ctx) return;
      W = section!.clientWidth;
      H = section!.clientHeight;
      canvas.width = Math.floor(W * DPR);
      canvas.height = Math.floor(H * DPR);
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    }

    function seedStars() {
      const n = Math.round(Math.min(180, Math.max(90, (W * H) / 11000)));
      stars = [];
      for (let i = 0; i < n; i++) {
        stars.push({
          x: Math.random(),
          y: Math.random(),
          z: 0.3 + Math.random() * 0.7,
          tw: Math.random() * Math.PI * 2,
          tws: 0.4 + Math.random() * 1.1,
        });
      }
    }

    function updateReadout(pullT: number) {
      const cur = lerp(YELLOW.score, YELLOW.scoreCal ?? YELLOW.score, easeInOut(pullT));
      setToScore(cur);
      const next: ReadoutPhase = pullT <= 0.02 ? "warn" : pullT >= 0.985 ? "cal" : "pulling";
      if (next !== lastPhase) {
        lastPhase = next;
        setPhase(next);
      }
    }

    function draw(now: number) {
      if (!ctx) return;
      if (t0 === null) t0 = now;
      const t = now - t0;
      ctx.clearRect(0, 0, W, H);

      const p1 = clamp01(t / T_SETTLE);
      const p2 = clamp01((t - T_SETTLE) / T_DRAW);
      const pullStart = T_SETTLE + T_DRAW + T_HOLD;
      const p3 = clamp01((t - pullStart) / T_PULL);

      // ── drifting, gently-twinkling background field ──
      for (const s of stars) {
        s.x += Math.sin(now * 0.00002 + s.tw) * 0.00006 * s.z;
        s.y += 0.00003 * s.z;
        if (s.y > 1.02) s.y = -0.02;
        s.tw += 0.016 * s.tws;
        const sx = s.x * W;
        const sy = s.y * H;
        const twAmt = 0.55 + 0.45 * Math.sin(s.tw);
        const appear = easeOut(clamp01(p1 * 1.3 - s.z * 0.2));
        const rad = (0.5 + s.z * 1.4) * (0.6 + 0.4 * twAmt);
        const alpha = (0.18 + 0.55 * s.z * twAmt) * appear;
        ctx.beginPath();
        ctx.arc(sx, sy, rad, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${C.star},${alpha.toFixed(3)})`;
        ctx.fill();
      }

      // ── constellation edges (each draws itself across a slice of p2) ──
      const nE = EDGES.length;
      for (let e = 0; e < nE; e++) {
        const seg = e / nE;
        const local = clamp01((p2 - seg) / ((1 / nE) * 1.6));
        if (local <= 0) continue;
        const a = nodeById(EDGES[e][0]);
        const b = nodeById(EDGES[e][1]);
        const pa = nodePos(a, p3, W, H);
        const pb = nodePos(b, p3, W, H);
        const ex = lerp(pa.x, pb.x, easeOut(local));
        const ey = lerp(pa.y, pb.y, easeOut(local));
        const ev = Math.min(a.ev, b.ev);
        const touchesYellow = a.special || b.special;
        const baseA = 0.1 + 0.3 * ev;
        const strain = touchesYellow ? lerp(0.55, 0.0, p3) : 0;
        ctx.beginPath();
        ctx.moveTo(pa.x, pa.y);
        ctx.lineTo(ex, ey);
        ctx.lineWidth = 1;
        if (strain > 0) {
          ctx.strokeStyle = `rgba(238,196,104,${(baseA + 0.25 * strain).toFixed(3)})`;
          ctx.shadowColor = "rgba(238,196,104,0.5)";
          ctx.shadowBlur = 8 * strain;
        } else {
          ctx.strokeStyle = `rgba(166,150,250,${baseA.toFixed(3)})`;
          ctx.shadowColor = "rgba(150,150,255,0.35)";
          ctx.shadowBlur = touchesYellow ? 4 : 2.5;
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
      }

      // ── ghost trail: where yellow used to over-score ──
      if (p3 > 0.02 && p3 < 0.999 && YELLOW.ox !== undefined && YELLOW.oy !== undefined) {
        const origin = { x: YELLOW.ox * W, y: YELLOW.oy * H };
        const home = nodePos(YELLOW, p3, W, H);
        ctx.beginPath();
        ctx.moveTo(origin.x, origin.y);
        ctx.lineTo(home.x, home.y);
        ctx.setLineDash([2, 6]);
        ctx.lineWidth = 1;
        ctx.strokeStyle = `rgba(238,196,104,${(0.3 * (1 - p3)).toFixed(3)})`;
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // ── nodes ──
      const nodeAppear = easeOut(clamp01((p2 - 0.05) * 1.4));
      for (const n of NODES) {
        const pos = nodePos(n, p3, W, H);
        let r = 3.4 + 3.0 * n.w;
        let col = n.col;
        let glowR = r * 3.4;
        let glowA = 0.28;

        if (n.special && n.colCal) {
          const e3 = easeInOut(p3);
          col = blend(n.col, n.colCal, e3);
          r = lerp(r * 1.6, r * 1.0, e3);
          glowR = lerp(r * 5.5, r * 3.2, e3);
          glowA = lerp(0.55, 0.3, e3);
        }

        const g = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, glowR);
        g.addColorStop(0, withAlpha(col, glowA * nodeAppear));
        g.addColorStop(1, withAlpha(col, 0));
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, glowR, 0, Math.PI * 2);
        ctx.fillStyle = g;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, r * nodeAppear, 0, Math.PI * 2);
        ctx.fillStyle = withAlpha(col, 0.96 * nodeAppear);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, Math.max(1, r * 0.4) * nodeAppear, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${(0.85 * nodeAppear).toFixed(3)})`;
        ctx.fill();
      }

      updateReadout(p3);

      if (p3 >= 1) finished = true;
      if (!finished) raf = requestAnimationFrame(draw);
    }

    /** Reduced-motion / completed-resize path: composite the final, already-
     *  corrected frame once (yellow at its violet calibrated home, no twinkle). */
    function drawStatic() {
      if (!ctx) return;
      ctx.clearRect(0, 0, W, H);
      for (const s of stars) {
        const sx = s.x * W;
        const sy = s.y * H;
        const rad = 0.5 + s.z * 1.4;
        ctx.beginPath();
        ctx.arc(sx, sy, rad, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${C.star},${(0.18 + 0.45 * s.z).toFixed(3)})`;
        ctx.fill();
      }
      for (let e = 0; e < EDGES.length; e++) {
        const a = nodeById(EDGES[e][0]);
        const b = nodeById(EDGES[e][1]);
        const pa = nodePos(a, 1, W, H);
        const pb = nodePos(b, 1, W, H);
        const ev = Math.min(a.ev, b.ev);
        ctx.beginPath();
        ctx.moveTo(pa.x, pa.y);
        ctx.lineTo(pb.x, pb.y);
        ctx.lineWidth = 1;
        ctx.strokeStyle = `rgba(166,150,250,${(0.1 + 0.3 * ev).toFixed(3)})`;
        ctx.stroke();
      }
      for (const n of NODES) {
        const pos = nodePos(n, 1, W, H);
        const r = 3.4 + 3.0 * n.w;
        const col = n.special && n.colCal ? n.colCal : n.col;
        const glowR = r * 3.2;
        const g = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, glowR);
        g.addColorStop(0, withAlpha(col, 0.3));
        g.addColorStop(1, withAlpha(col, 0));
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, glowR, 0, Math.PI * 2);
        ctx.fillStyle = g;
        ctx.fill();
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2);
        ctx.fillStyle = withAlpha(col, 0.96);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, Math.max(1, r * 0.4), 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255,0.85)";
        ctx.fill();
      }
      // Final calibrated readout state.
      setToScore(YELLOW.scoreCal ?? YELLOW.score);
      setPhase("cal");
    }

    function start() {
      if (started) return;
      started = true;
      if (reduce) {
        drawStatic();
        return;
      }
      t0 = null;
      raf = requestAnimationFrame(draw);
    }

    function onResize() {
      resize();
      seedStars();
      if (reduce && started) drawStatic();
      else if (finished) drawStatic();
    }

    // Initial layout.
    resize();
    seedStars();
    window.addEventListener("resize", onResize);

    // Autonomous arrival: animate ONLY when in view (never hover/click).
    let io: IntersectionObserver | null = null;
    let safety: ReturnType<typeof setTimeout> | null = null;
    if (reduce) {
      // Resolve to the corrected, static frame immediately once laid out.
      raf = requestAnimationFrame(() => {
        resize();
        seedStars();
        start();
      });
    } else if (typeof IntersectionObserver !== "undefined") {
      io = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (entry.isIntersecting) {
              start();
              io?.disconnect();
              break;
            }
          }
        },
        { threshold: 0.35 },
      );
      io.observe(section);
      // Fire even if already in view / observer never triggers.
      safety = setTimeout(start, 900);
    } else {
      safety = setTimeout(start, 700);
    }

    return () => {
      if (raf) cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      io?.disconnect();
      if (safety) clearTimeout(safety);
    };
  }, []);

  const readoutClass =
    phase === "cal"
      ? `${styles.readout} ${styles.readoutCal}`
      : `${styles.readout} ${styles.readoutWarn}`;
  const stateLabel =
    phase === "cal"
      ? "Yellow hat · calibrated"
      : phase === "pulling"
        ? "Yellow hat · pulling back…"
        : "Yellow hat · over-confident";

  return (
    <section
      ref={sectionRef}
      aria-label="Glasshat evaluation constellation: scored hat-criterion stars draw their own lines and resolve into a star map, then the over-confident Yellow node is pulled back from its amber over-scored position to the violet calibrated position."
      className="relative isolate min-h-[88svh] w-screen overflow-hidden"
    >
      {/* Decorative starfield + constellation (opaque to assistive tech). */}
      <div aria-hidden="true" className={styles.stage}>
        <canvas ref={canvasRef} className={styles.sky} />
      </div>

      {/* Overlay content — H1 + CTAs paint immediately (LCP); never gated. */}
      <div className="relative z-[3] mx-auto grid min-h-[88svh] max-w-[78rem] grid-rows-[auto_1fr_auto] gap-[clamp(1rem,3vh,2.25rem)] px-[clamp(1.25rem,4vw,2.75rem)] py-[clamp(1.25rem,4vw,2.75rem)]">
        {/* Eyebrow */}
        <div className="flex items-center gap-2 text-[0.78rem] uppercase tracking-[0.16em] text-[var(--color-accent-2)]">
          <span aria-hidden="true" className="h-px w-7 bg-gradient-to-r from-[var(--color-accent-2)] to-transparent" />
          Evaluation constellation
        </div>

        {/* Hero block — sits low-left so the constellation breathes. */}
        <div className="flex flex-col justify-end self-end pb-[2vh]">
          <h1 className="font-display max-w-[18ch] text-[clamp(2.3rem,6vw,4.6rem)] font-bold leading-[1.04] tracking-[-0.02em]">
            Glasshat doesn&apos;t just judge.{" "}
            <em className="font-serif-italic text-gradient font-medium">It audits the judge.</em>
          </h1>
          <p className="mt-5 max-w-[46ch] text-[clamp(1rem,1.7vw,1.18rem)] leading-[1.6] text-[var(--color-muted)]">
            Rubric-aware evaluation that mirrors the official rules, grounds every
            sub-score in retrieved evidence, then catches its own over-confidence
            and self-corrects &mdash; live. Not a chatbot.
          </p>

          {/* Primary CTAs */}
          <div className="mt-7 flex flex-wrap items-center gap-3">
            <Link
              href="/participate"
              className="hover-lift inline-flex items-center justify-center rounded-full bg-[var(--color-accent-strong)] px-6 py-3 text-[0.98rem] font-medium text-white shadow-[0_10px_30px_-12px_oklch(0.55_0.17_290/0.7)]"
            >
              Score a submission &rarr;
            </Link>
            <Link
              href="/judge"
              className="hover-lift inline-flex items-center justify-center rounded-full border border-[var(--color-border)] px-6 py-3 text-[0.98rem] font-medium text-[var(--color-ink)] hover:border-[var(--color-accent)]"
            >
              Judge a cohort
            </Link>
          </div>

          {/* Badge row */}
          <ul className="mt-6 flex flex-wrap gap-2 text-[0.74rem] text-[var(--color-muted)]">
            {["Arize track", "Gemini · Vertex AI", "Google ADK", "Phoenix + MCP"].map((b) => (
              <li
                key={b}
                className="rounded-full border border-[var(--color-border)] px-3 py-1 tracking-[0.02em]"
              >
                {b}
              </li>
            ))}
          </ul>

          {/* Corrected-score readout (aria-live surfaces the recovery to AT). */}
          <div className={`${readoutClass} mt-6 max-w-[36ch] px-[18px] py-4`} aria-live="polite">
            <div className="mb-2 flex items-center justify-between text-[0.74rem] uppercase tracking-[0.08em] text-[var(--color-muted)]">
              <span>{stateLabel}</span>
              <span aria-hidden="true" className={styles.dot} />
            </div>
            <div
              aria-hidden="true"
              className="flex items-baseline gap-3 [font-variant-numeric:tabular-nums]"
            >
              <span className={`${styles.from} text-[1.5rem] font-medium opacity-85`}>
                {YELLOW.score.toFixed(1)}
              </span>
              <span className="text-[1.1rem] text-[var(--color-muted)]">&rarr;</span>
              <span className={`${styles.to} text-[2.1rem] font-bold tracking-[-0.02em]`}>
                {toScore.toFixed(1)}
              </span>
            </div>
            <p className="font-serif-italic mt-3 text-[0.86rem] leading-[1.5] text-[var(--color-muted)]">
              <code className={styles.formulaCode}>
                clip(score &minus; 0.8&middot;mean_delta, p25, p75)
              </code>{" "}
              &middot; &plusmn;2.0 cap, from a prior recovered from held-out
              spike-D anchors.
            </p>
            <span className="mt-2 block text-[0.72rem] tracking-[0.03em] text-[var(--color-muted)] opacity-85">
              Illustrative.
            </span>
          </div>
        </div>

        {/* Constellation legend — the six hats and their tokens. */}
        <ul
          aria-label="Constellation legend"
          className="flex flex-wrap items-center gap-x-[14px] gap-y-2 border-t border-[var(--color-border)] pt-[18px] text-[0.74rem] tracking-[0.02em] text-[var(--color-muted)]"
        >
          {(
            [
              ["White", "var(--color-ink)"],
              ["Red", "var(--color-accent-3)"],
              ["Black", "var(--color-muted)"],
              ["Green", "var(--color-good)"],
              ["Blue", "var(--color-accent-2)"],
            ] as const
          ).map(([label, color]) => (
            <li key={label} className="inline-flex items-center gap-1.5">
              <span
                aria-hidden="true"
                className="h-[9px] w-[9px] rounded-full"
                style={{ background: color }}
              />
              {label}
            </li>
          ))}
          <li className="inline-flex items-center gap-1.5">
            <span
              aria-hidden="true"
              className="h-[9px] w-[9px] rounded-full"
              style={{ background: "var(--color-warn)" }}
            />
            Yellow &rarr;
            <span
              aria-hidden="true"
              className="h-[9px] w-[9px] rounded-full"
              style={{ background: "var(--color-accent)" }}
            />
            calibrated
          </li>
        </ul>
      </div>
    </section>
  );
}
