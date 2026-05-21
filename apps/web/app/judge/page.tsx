import Link from "next/link";

export default function JudgePage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-3xl font-semibold">Judge</h1>
      <p className="mt-2 text-[var(--color-muted)]">
        Batch-evaluate submissions against a synthesized rubric, rank them, and lock official
        scores. Top-K hit rate compares predicted ranking to known winners.
      </p>
      <ul className="mt-6 list-disc pl-5 text-[var(--color-muted)]">
        <li>Upload a CSV manifest or zip of submissions</li>
        <li>Live Kanban: queued → ingesting → planning → hats → auditing → scoring → complete</li>
        <li>Lock official scores (immutable, signed)</li>
      </ul>
      <Link href="/" className="mt-8 inline-block text-[var(--color-accent)]">
        ← back
      </Link>
    </main>
  );
}
