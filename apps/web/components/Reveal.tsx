import type { ReactNode } from "react";

export interface RevealProps {
  children: ReactNode;
  /** Stagger delay in ms (sequenced reveals). */
  delayMs?: number;
  className?: string;
}

/**
 * A staggered fade-up entrance. CSS-only (`.reveal` runs a `both` fill-mode
 * animation), so content always ends visible — never stuck hidden, works without
 * JS, and is disabled under reduced-motion via CSS.
 */
export function Reveal({ children, delayMs = 0, className = "" }: RevealProps) {
  return (
    <div
      data-testid="reveal"
      className={`reveal ${className}`.trim()}
      style={delayMs ? { animationDelay: `${delayMs}ms` } : undefined}
    >
      {children}
    </div>
  );
}
