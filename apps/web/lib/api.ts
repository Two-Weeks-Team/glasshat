/** Typed client for the Glasshat API (mirrors apps/api FastAPI contract). */

import { streamPost, type SseEvent } from "@/lib/sse";

export const API_BASE: string = process.env.NEXT_PUBLIC_API_BASE ?? "";

export interface EvaluationInput {
  rubric_source: Record<string, string>;
  deck_text?: string;
  repo_url?: string;
  mode?: "judge" | "participant";
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
  final_score: number;
  scores: CriterionScore[];
  audit_corrections: AuditCorrection[];
  mode: string;
  created_at: string;
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

export const evaluate = (input: EvaluationInput): Promise<RunRecord> =>
  postJson<RunRecord>("/api/evaluate", input);

export const getRun = async (runId: string): Promise<RunRecord> => {
  const resp = await fetch(`${API_BASE}/api/runs/${runId}`);
  if (!resp.ok) throw new Error(`run ${runId} not found`);
  return (await resp.json()) as RunRecord;
};

export const streamEvaluate = (
  input: EvaluationInput,
  onEvent: (e: SseEvent) => void,
): Promise<void> => streamPost(`${API_BASE}/api/evaluate/stream`, input, onEvent);
