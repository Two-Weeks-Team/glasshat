/**
 * 3D projection for the self-correction constellation.
 *
 * Each criterion becomes a node in a centered cube from its (score, weight,
 * evidence) features. When a score self-corrects, re-projecting moves the node —
 * this is the live "graph reshape" driven by the pipeline's audit output.
 */

export interface CriterionFeature {
  id: string;
  scoreFrac: number; // 0..1 (score / scale)
  weight: number; // 0..1
  evidenceDepth: number; // 0..1
}

export interface Node3D {
  id: string;
  x: number;
  y: number;
  z: number;
}

const clamp01 = (v: number): number => Math.max(0, Math.min(1, v));

/** Map a criterion's features onto [-1, 1]^3. */
export function projectCriterion(c: CriterionFeature): Node3D {
  return {
    id: c.id,
    x: clamp01(c.scoreFrac) * 2 - 1,
    y: clamp01(c.weight) * 2 - 1,
    z: clamp01(c.evidenceDepth) * 2 - 1,
  };
}

export function projectAll(features: CriterionFeature[]): Node3D[] {
  return features.map(projectCriterion);
}

/** Re-project after a self-correction lowers a criterion's score fraction. */
export function reshapeOnCorrection(
  feature: CriterionFeature,
  correctedScoreFrac: number,
): Node3D {
  return projectCriterion({ ...feature, scoreFrac: correctedScoreFrac });
}
