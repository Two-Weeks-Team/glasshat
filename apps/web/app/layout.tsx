import type { Metadata } from "next";
import { Newsreader, Space_Grotesk } from "next/font/google";

import { ApiStatus } from "@/components/ApiStatus";
import { SiteNav } from "@/components/SiteNav";

import "./globals.css";

// Display face for the headline + every big number (rank numerals, scores).
const display = Space_Grotesk({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});

// Italic serif for narrative asides ("audits the judge", pull-quotes).
const serif = Newsreader({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic"],
  variable: "--font-serif",
  display: "swap",
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
              Glasshat · Gemini (Vertex AI) + Google ADK + Arize Phoenix · Rapid Agent / Arize track
            </span>
            <ApiStatus />
          </div>
        </footer>
      </body>
    </html>
  );
}
