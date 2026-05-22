"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

export interface RevealProps {
  children: ReactNode;
  /** Stagger delay in ms (for sequenced reveals). */
  delayMs?: number;
  className?: string;
}

/**
 * Scroll-triggered fade-up. Adds `is-visible` when the element enters the
 * viewport (IntersectionObserver). Degrades to immediately-visible where the
 * observer is unavailable (SSR/tests) and is disabled under reduced-motion via CSS.
 */
export function Reveal({ children, delayMs = 0, className = "" }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setVisible(true);
          io.disconnect();
        }
      },
      { threshold: 0.12 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      data-testid="reveal"
      className={`reveal ${visible ? "is-visible" : ""} ${className}`.trim()}
      style={delayMs ? { transitionDelay: `${delayMs}ms` } : undefined}
    >
      {children}
    </div>
  );
}
