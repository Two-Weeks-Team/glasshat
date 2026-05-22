/** Typed client for the Glasshat API (mirrors apps/api FastAPI contract). */

import { streamPost, type SseEvent } from "@/lib/sse";

export const API_BASE: string = process.env.NEXT_PUBLIC_API_BASE ?? "";

export type Hat = "blue" | "white" | "red" | "yellow" | "black" | "green";
export type RunMode = "judge" | "participant";

export interface PresetInfo {
  id: string;
  label: string;
  criteria_count: number;
  final_scale: string;
  source_type: string;
}

export interface EvaluationInput {
  rubric_source: Record<string, string>;
  deck_text?: string;
  repo_url?: string;
  mode?: RunMode;
}

export interface PlanObject {
  hats_enabled: Hat[];
  criteria_in_scope: string[];
  retrieval_budget: Record<string, number>;
  weights: Record<string, number>;
  code_grader_depth: string;
}

export interface Criterion {
  id: string;
  label: string;
  weight: number | null;
  scale: number;
  bmad_mapping: string[];
  descriptor_levels: Record<string, string>;
  evidence_required: boolean;
  source_clause: string;
  source_excerpt: string;
}

export interface TieBreaker {
  order: number;
  criterion_id: string;
}

export interface RubricSource {
  type: string;
  identifier: string;
  fetched_at: string | null;
  source_text_excerpt: string;
}

export interface ScoringRule {
  aggregation: string;
  final_scale: string;
}

export interface SynthesizedRubric {
  schema_version: string;
  rubric_id: string;
  rubric_schema_hash: string;
  source: RubricSource;
  scoring_rule: ScoringRule;
  criteria: Criterion[];
  tie_breakers: TieBreaker[];
  weights_vector: number[];
  confidence: number;
  warnings: string[];
}

export interface AuditCorrection {
  hat: string;
  criterion_id: string;
  original: number;
  corrected: number;
  mean_delta: number;
  n: number;
  reason: string;
}

export interface CriterionScore {
  criterion_id: string;
  score: number;
  evidence_refs: string[];
  audit: AuditCorrection | null;
}

export interface RunRecord {
  run_id: string;
  rubric: SynthesizedRubric;
  final_score: number;
  scores: CriterionScore[];
  audit_corrections: AuditCorrection[];
  mode: string;
  created_at: string;
}

export interface OverrideRequest {
  criterion_id: string;
  score: number;
  reason: string;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`${path} failed: ${resp.status}`);
  return (await resp.json()) as T;
}

async function getJson<T>(path: string): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`);
  if (!resp.ok) throw new Error(`${path} failed: ${resp.status}`);
  return (await resp.json()) as T;
}

/** Liveness probe; resolves false instead of throwing so callers can render a chip. */
export const healthCheck = async (): Promise<boolean> => {
  try {
    const resp = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    return resp.ok;
  } catch {
    return false;
  }
};

export const listPresets = (): Promise<PresetInfo[]> => getJson<PresetInfo[]>("/api/presets");

export const getPlan = (input: EvaluationInput): Promise<PlanObject> =>
  postJson<PlanObject>("/api/plan", input);

export const evaluate = (input: EvaluationInput): Promise<RunRecord> =>
  postJson<RunRecord>("/api/evaluate", input);

export const getRun = (runId: string): Promise<RunRecord> =>
  getJson<RunRecord>(`/api/runs/${runId}`);

export const override = (runId: string, body: OverrideRequest): Promise<RunRecord> =>
  postJson<RunRecord>(`/api/runs/${runId}/override`, body);

export const streamEvaluate = (
  input: EvaluationInput,
  onEvent: (e: SseEvent) => void,
): Promise<void> => streamPost(`${API_BASE}/api/evaluate/stream`, input, onEvent);
