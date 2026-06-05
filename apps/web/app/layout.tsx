import type { Metadata } from "next";
import { Newsreader, Space_Grotesk } from "next/font/google";

import { ApiStatus } from "@/components/ApiStatus";
import { SiteNav } from "@/components/SiteNav";

import "./globals.css";

// Display face for the headline + every big number (rank numerals, scores).
// Two weights (600/700) cover the H1 and numerals — fewer files = lighter
// critical path. Preloaded since it paints the headline/LCP on the landing hero.
const display = Space_Grotesk({
  subsets: ["latin"],
  weight: ["600", "700"],
  variable: "--font-display",
  // `optional`, not `swap`: the big display H1 is the LCP element, and a swap
  // re-paints it ~2s in (webfont arrival) → LCP ≈ 3.5s. `optional` keeps the
  // metric-adjusted fallback when the webfont isn't instant, so LCP ≈ FCP.
  display: "optional",
});

// Italic serif for narrative asides (the landing hero accent only). Not preloaded
// — it isn't on /judge or /participate, so preloading it there just contended
// with their critical resources and pushed LCP out.
const serif = Newsreader({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic"],
  variable: "--font-serif",
  display: "swap",
  preload: false,
});

export const metadata: Metadata = {
  title: "Glasshat — evaluation that audits its own scores",
  description:
    "Rubric-aware AI evaluation that mirrors the official rules, grounds every sub-score in retrieved evidence, and self-corrects its own over-confidence live.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${serif.variable}`}>
      <body className="flex min-h-screen flex-col">
        <SiteNav />
        <div className="flex-1">{children}</div>
        <footer className="border-t border-[var(--color-border)]/60">
          <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-6 py-4 text-xs text-[var(--color-muted)]">
            <span>
              Glasshat · Gemini on Gemini Enterprise Agent Platform + Google ADK + Arize AX · Rapid Agent / Arize track
            </span>
            <ApiStatus />
          </div>
        </footer>
      </body>
    </html>
  );
}
