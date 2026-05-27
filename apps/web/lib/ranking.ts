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

/**
 * Standard six-hat panel size — used to back-derive a pre-audit per-criterion
 * score for legacy RunRecords cached before `pre_audit_final_score` was added
 * to the contract. New RunRecords carry the field directly; this is a
 * compatibility shim for the sample cohort.
 */
const HATS_PER_CRITERION = 6;

function nativeFromInternal(internal: number, scale: number): number {
  return 1 + (internal / 10) * (scale - 1);
}

function internalFromNative(native: number, scale: number): number {
  return ((native - 1) * 10) / (scale - 1);
}

/**
 * Reconstruct each criterion's pre-audit native score from an audited
 * RunRecord by adding back the per-hat shift that the audit applied.
 *
 * `audited_internal = sum(hat_scores) / N`
 * `pre_audit_internal = audited_internal + (sum of (original − corrected)) / N`
 *
 * Falls back to the audited score when no corrections touched that criterion.
 */
export function preAuditScoreMap(record: RunRecord): Record<string, number> {
  const map: Record<string, number> = {};
  for (const cs of record.scores) {
    const criterion = record.rubric.criteria.find((c) => c.id === cs.criterion_id);
    if (!criterion) {
      map[cs.criterion_id] = cs.score;
      continue;
    }
    const deltaSum = record.audit_corrections
      .filter((c) => c.criterion_id === cs.criterion_id)
      .reduce((acc, c) => acc + (c.original - c.corrected), 0);
    if (deltaSum === 0) {
      map[cs.criterion_id] = cs.score;
      continue;
    }
    const auditedInternal = internalFromNative(cs.score, criterion.scale);
    const preInternal = auditedInternal + deltaSum / HATS_PER_CRITERION;
    map[cs.criterion_id] = nativeFromInternal(preInternal, criterion.scale);
  }
  return map;
}

/**
 * Pre-audit final score: read from the RunRecord when the engine provided it
 * (post-PR-A); reconstruct from corrections + criterion scores for cached
 * legacy records. Two-decimal rounded to match `finalScoreFrom`.
 */
export function preAuditFinalScore(record: RunRecord): number {
  if (typeof record.pre_audit_final_score === "number" && record.pre_audit_final_score > 0) {
    return record.pre_audit_final_score;
  }
  return finalScoreFrom(record.rubric, preAuditScoreMap(record));
}

function _rankBy(
  items: EvalItem[],
  scoreOf: (item: EvalItem) => { final: number; scores: Record<string, number> },
): RankedItem[] {
  const enriched: RankedItem[] = items.map((it) => {
    const { final, scores } = scoreOf(it);
    return { ...it, effectiveScores: scores, effectiveFinal: final, rank: 0 };
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

/** Rank by audited final (desc), breaking ties by the rubric's ordered tie-break chain. */
export function rankSubmissions(items: EvalItem[]): RankedItem[] {
  return _rankBy(items, (it) => {
    const scores = effectiveScoreMap(it);
    return { final: finalScoreFrom(it.record.rubric, scores), scores };
  });
}

/**
 * Rank by *pre-audit* final — the order the cohort would have had without
 * Glasshat's calibration. Drives the left column of the rank-flip board.
 * Overrides (gate-2) are ignored on this axis: pre-audit is the agent's
 * raw consensus, not the human-amended verdict.
 */
export function rankSubmissionsPreAudit(items: EvalItem[]): RankedItem[] {
  return _rankBy(items, (it) => {
    const scores = preAuditScoreMap(it.record);
    return { final: finalScoreFrom(it.record.rubric, scores), scores };
  });
}

/** Hit rate of the predicted top-K against the judge's marked winners (0–1). */
export function topKHitRate(ranked: RankedItem[], winners: Set<string>, k: number): number {
  if (winners.size === 0 || k <= 0) return 0;
  const top = ranked.slice(0, k).map((r) => r.label);
  const hits = top.filter((l) => winners.has(l)).length;
  return hits / Math.min(k, winners.size);
}
