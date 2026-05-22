/**
 * Judge-side ranking logic, kept pure for unit testing.
 *
 * `finalScoreFrom` mirrors `agents/report.final_score` exactly so a gate-2
 * override (a manual criterion score) re-ranks the cohort faithfully — the same
 * weighted-sum / average over score fractions, projected onto the display scale.
 */

import type { RunRecord, SynthesizedRubric } from "@/lib/api";

const EPS = 1e-6;

const scaleTop = (finalScale: string): number => {
  const top = Number(finalScale.trim().split("-").at(-1));
  return Number.isFinite(top) ? top : 100;
};

/** Final score on the rubric's display scale, from an explicit criterion→score map. */
export function finalScoreFrom(
  rubric: SynthesizedRubric,
  scoreById: Record<string, number>,
): number {
  const fracs = rubric.criteria.map((c) => ({
    weight: c.weight ?? 0,
    frac: (scoreById[c.id] ?? 0) / c.scale,
  }));
  const agg =
    rubric.scoring_rule.aggregation === "weighted_sum"
      ? fracs.reduce((s, f) => s + f.weight * f.frac, 0)
      : fracs.reduce((s, f) => s + f.frac, 0) / (fracs.length || 1);
  return Math.round(agg * scaleTop(rubric.scoring_rule.final_scale) * 100) / 100;
}

export interface EvalItem {
  label: string;
  record: RunRecord;
  /** Gate-2 manual overrides: criterion_id → native score. */
  overrides?: Record<string, number>;
}

export interface RankedItem extends EvalItem {
  rank: number;
  effectiveFinal: number;
  effectiveScores: Record<string, number>;
}

function effectiveScoreMap(item: EvalItem): Record<string, number> {
  const map: Record<string, number> = {};
  for (const s of item.record.scores) map[s.criterion_id] = s.score;
  if (item.overrides) Object.assign(map, item.overrides);
  return map;
}

/** Rank by effective final (desc), breaking ties by the rubric's ordered tie-break chain. */
export function rankSubmissions(items: EvalItem[]): RankedItem[] {
  const enriched: RankedItem[] = items.map((it) => {
    const effectiveScores = effectiveScoreMap(it);
    return {
      ...it,
      effectiveScores,
      effectiveFinal: finalScoreFrom(it.record.rubric, effectiveScores),
      rank: 0,
    };
  });

  enriched.sort((a, b) => {
    if (Math.abs(a.effectiveFinal - b.effectiveFinal) > EPS) {
      return b.effectiveFinal - a.effectiveFinal;
    }
    const tbs = [...a.record.rubric.tie_breakers].sort((x, y) => x.order - y.order);
    for (const tb of tbs) {
      const av = a.effectiveScores[tb.criterion_id] ?? 0;
      const bv = b.effectiveScores[tb.criterion_id] ?? 0;
      if (Math.abs(av - bv) > EPS) return bv - av;
    }
    return a.label.localeCompare(b.label);
  });

  enriched.forEach((e, i) => (e.rank = i + 1));
  return enriched;
}

/** Hit rate of the predicted top-K against the judge's marked winners (0–1). */
export function topKHitRate(ranked: RankedItem[], winners: Set<string>, k: number): number {
  if (winners.size === 0 || k <= 0) return 0;
  const top = ranked.slice(0, k).map((r) => r.label);
  const hits = top.filter((l) => winners.has(l)).length;
  return hits / Math.min(k, winners.size);
}
