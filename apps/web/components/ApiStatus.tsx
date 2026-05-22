"use client";

import { useEffect, useState } from "react";

import { API_BASE, healthCheck } from "@/lib/api";

/** Live API liveness chip — polls /health on mount. */
export function ApiStatus() {
  const [up, setUp] = useState<boolean | null>(null);

  useEffect(() => {
    let alive = true;
    healthCheck().then((ok) => {
      if (alive) setUp(ok);
    });
    return () => {
      alive = false;
    };
  }, []);

  const tone =
    up === null ? "var(--color-muted)" : up ? "var(--color-good)" : "var(--color-bad)";
  const label = up === null ? "checking API…" : up ? "API live" : "API unreachable";
  const target = API_BASE || "same-origin";

  return (
    <span
      className="inline-flex items-center gap-2 text-xs text-[var(--color-muted)]"
      title={target}
      data-testid="api-status"
    >
      <span
        className="inline-block h-2 w-2 rounded-full"
        style={{ background: tone }}
        aria-hidden
      />
      {label}
    </span>
  );
}
