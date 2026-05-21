import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-8 px-6">
      <header>
        <h1 className="text-4xl font-semibold tracking-tight">Glasshat</h1>
        <p className="mt-2 text-lg text-[var(--color-muted)]">
          One engine, two viewports. Evaluation that mirrors the actual rubric — and audits its own
          scores in real time.
        </p>
      </header>
      <nav className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Link
          href="/judge"
          className="rounded-2xl border border-[var(--color-muted)]/30 p-6 transition hover:border-[var(--color-accent)]"
        >
          <h2 className="text-xl font-medium">I&apos;m a Judge</h2>
          <p className="mt-1 text-sm text-[var(--color-muted)]">
            Batch-rank submissions, lock official scores, see Top-K hit rate.
          </p>
        </Link>
        <Link
          href="/participate"
          className="rounded-2xl border border-[var(--color-muted)]/30 p-6 transition hover:border-[var(--color-accent)]"
        >
          <h2 className="text-xl font-medium">I&apos;m a Participant</h2>
          <p className="mt-1 text-sm text-[var(--color-muted)]">
            Score your submission, watch the audit self-correct, iterate on the weakest axis.
          </p>
        </Link>
      </nav>
    </main>
  );
}
