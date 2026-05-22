import Link from "next/link";

/** Global brand bar + viewport links, rendered in the root layout. */
export function SiteNav() {
  return (
    <header className="sticky top-0 z-10 border-b border-[var(--color-border)]/60 bg-[var(--color-bg)]/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span
            className="inline-block h-3 w-3 rotate-45 rounded-[2px] bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-accent-2)]"
            aria-hidden
          />
          Glasshat
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          <Link
            href="/judge"
            className="rounded-lg px-3 py-1.5 text-[var(--color-muted)] transition hover:bg-[var(--color-surface)] hover:text-[var(--color-ink)]"
          >
            Judge
          </Link>
          <Link
            href="/participate"
            className="rounded-lg px-3 py-1.5 text-[var(--color-muted)] transition hover:bg-[var(--color-surface)] hover:text-[var(--color-ink)]"
          >
            Participant
          </Link>
        </nav>
      </div>
    </header>
  );
}
