import type { Metadata } from "next";

import { ApiStatus } from "@/components/ApiStatus";
import { SiteNav } from "@/components/SiteNav";

import "./globals.css";

export const metadata: Metadata = {
  title: "Glasshat — evaluation that audits its own scores",
  description:
    "Rubric-aware AI evaluation that mirrors the official rules, grounds every sub-score in retrieved evidence, and self-corrects its own over-confidence live.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
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
