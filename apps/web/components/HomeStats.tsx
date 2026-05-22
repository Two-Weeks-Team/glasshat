"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/Badge";
import { listPresets, type PresetInfo } from "@/lib/api";

/** Live rubric-preset showcase on the landing page (proves multi-rubric support). */
export function HomeStats() {
  const [presets, setPresets] = useState<PresetInfo[] | null>(null);

  useEffect(() => {
    let alive = true;
    listPresets()
      .then((p) => alive && setPresets(p))
      .catch(() => alive && setPresets([]));
    return () => {
      alive = false;
    };
  }, []);

  if (presets === null) {
    return <p className="text-sm text-[var(--color-muted)]">Loading rubric presets…</p>;
  }
  if (presets.length === 0) {
    return (
      <p className="text-sm text-[var(--color-muted)]">
        Rubric presets load from the API at runtime.
      </p>
    );
  }

  return (
    <div data-testid="home-stats" className="flex flex-col gap-2">
      <span className="text-sm text-[var(--color-muted)]">
        {presets.length} rubric presets ready — the same engine scores any of them:
      </span>
      <div className="flex flex-wrap gap-2">
        {presets.map((p) => (
          <Badge key={p.id} tone="accent" title={`${p.criteria_count} criteria · ${p.final_scale}`}>
            {p.label}
          </Badge>
        ))}
      </div>
    </div>
  );
}
