"use client";

import { useEffect, useRef, useState } from "react";

export interface CountUpProps {
  value: number;
  decimals?: number;
  durationMs?: number;
}

const prefersReduced = (): boolean =>
  typeof matchMedia === "undefined" || matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * Eased count-up to `value`. Renders the final value immediately where animation
 * is unavailable or reduced-motion is set (also the SSR/test path), so the number
 * is always correct.
 */
export function CountUp({ value, decimals = 1, durationMs = 900 }: CountUpProps) {
  const [display, setDisplay] = useState(value);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    if (prefersReduced() || typeof requestAnimationFrame === "undefined") {
      setDisplay(value);
      return;
    }
    const start = performance.now();
    setDisplay(0);
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(value * eased);
      if (t < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
    };
  }, [value, durationMs]);

  return (
    <span data-testid="countup" className="tabular-nums">
      {display.toFixed(decimals)}
    </span>
  );
}
