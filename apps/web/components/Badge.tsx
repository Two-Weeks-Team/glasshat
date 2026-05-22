import type { ReactNode } from "react";

export type Tone = "accent" | "good" | "warn" | "bad" | "muted";

const TONE_VAR: Record<Tone, string> = {
  accent: "var(--color-accent)",
  good: "var(--color-good)",
  warn: "var(--color-warn)",
  bad: "var(--color-bad)",
  muted: "var(--color-muted)",
};

export interface BadgeProps {
  children: ReactNode;
  tone?: Tone;
  title?: string;
}

/** A small pill that tints itself by tone (border + text in the tone color). */
export function Badge({ children, tone = "muted", title }: BadgeProps) {
  const color = TONE_VAR[tone];
  return (
    <span
      data-testid="badge"
      title={title}
      className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
      style={{ color, borderColor: color, background: `color-mix(in oklch, ${color} 12%, transparent)` }}
    >
      {children}
    </span>
  );
}
