"use client";

import { useEffect } from "react";

/**
 * Turns the landing into a scene-by-scene cinematic scroll: each full-height
 * beat gently snaps into place (proximity, not mandatory — never traps the
 * scroll). Scoped to the landing only (toggles a class on <html> while mounted)
 * so /judge and /participate keep normal scrolling. Disabled entirely for
 * `prefers-reduced-motion` users. Renders nothing.
 */
export default function CinematicScroll() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    const root = document.documentElement;
    root.classList.add("cine-snap");
    return () => root.classList.remove("cine-snap");
  }, []);
  return null;
}
