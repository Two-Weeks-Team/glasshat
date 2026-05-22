// AUTO-GENERATED sample cohort, REAL RunRecords captured from the live API
// (POST /api/evaluate on gemini-3.1-flash-lite, rapid-agent rubric, 2026-05-22,
// spike-D calibration). Used as the /judge first-paint sample so the ranked
// result is visible before any round-trip; "Run cohort" re-evaluates live.
// Not fabricated, see README.
import type { RunRecord } from "@/lib/api";

export interface SampleEntry {
  label: string;
  record: RunRecord;
}

export const SAMPLE_COHORT: SampleEntry[] = (
[
  {
    "label": "Glasshat",
    "record": {
      "run_id": "53e2c03e-2f9a-4c2f-b5ff-e1221287a4f3",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "b4370943-0e9a-46dd-a036-d86cd9a4049b",
        "rubric_schema_hash": "64b4201a1e49cc52072ecf59965a02d07aa9d96c70c6fc66a9192555a304d763",
        "source": {
          "type": "preset",
          "identifier": "rapid-agent",
          "fetched_at": null,
          "source_text_excerpt": ""
        },
        "scoring_rule": {
          "aggregation": "weighted_sum",
          "final_scale": "0-100"
        },
        "criteria": [
          {
            "id": "tech-implementation",
            "label": "Technological Implementation",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "B1",
              "B2",
              "C1",
              "C2",
              "C3",
              "C4"
            ],
            "descriptor_levels": {
              "1": "Surface — basic wrapper, no novel engineering",
              "2": "Functional — working integration, some custom logic",
              "3": "Solid — non-trivial engineering, edge cases handled",
              "4": "Impressive — complex architecture, custom protocols",
              "5": "Exceptional — publication-worthy depth"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 1 of 4, weight 25%, tie-break first",
            "source_excerpt": "Technological Implementation"
          },
          {
            "id": "design",
            "label": "Design",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "D1",
              "D3",
              "A2"
            ],
            "descriptor_levels": {
              "1": "Confusing first run, no feedback",
              "2": "Works with friction, sparse polish",
              "3": "Smooth happy path, helpful errors",
              "4": "Thoughtful pacing, demo-able in 60s",
              "5": "Memorable, dinner-table-retellable UX"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 2 of 4, weight 25%, tie-break second",
            "source_excerpt": "Design"
          },
          {
            "id": "potential-impact",
            "label": "Potential Impact",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A4",
              "A1"
            ],
            "descriptor_levels": {
              "1": "Niche, unclear who benefits",
              "2": "Plausible benefit for a small group",
              "3": "Clear benefit for a defined audience",
              "4": "Broad impact across a real market",
              "5": "Category-defining, large addressable impact"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 3 of 4, weight 25%, tie-break third",
            "source_excerpt": "Potential Impact"
          },
          {
            "id": "quality-of-idea",
            "label": "Quality of the Idea",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A1",
              "A3"
            ],
            "descriptor_levels": {
              "1": "Recognizable wrapper pattern",
              "2": "Familiar pattern with one twist",
              "3": "Non-obvious, well-motivated concept",
              "4": "Pattern not seen in prior winners",
              "5": "Defines a genuinely new pattern"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 4 of 4, weight 25%, tie-break fourth",
            "source_excerpt": "Quality of the Idea"
          }
        ],
        "tie_breakers": [
          {
            "order": 1,
            "criterion_id": "tech-implementation"
          },
          {
            "order": 2,
            "criterion_id": "design"
          },
          {
            "order": 3,
            "criterion_id": "potential-impact"
          },
          {
            "order": 4,
            "criterion_id": "quality-of-idea"
          }
        ],
        "threshold_gates": [
          {
            "id": "phoenix-mcp-runtime",
            "condition": "Must call the Phoenix MCP server at runtime (Arize Stage-1)",
            "check": "automated"
          },
          {
            "id": "gemini-google-stack",
            "condition": "Uses Gemini + Google Cloud Agent Builder + a partner MCP server",
            "check": "manual"
          },
          {
            "id": "public-oss-repo",
            "condition": "Public repository with an OSI-approved license",
            "check": "manual"
          },
          {
            "id": "demo-video",
            "condition": "<=3 minute demo video on YouTube/Vimeo (English or EN subtitles)",
            "check": "manual"
          }
        ],
        "weights_vector": [
          0.25,
          0.25,
          0.25,
          0.25
        ],
        "confidence": 1.0,
        "warnings": []
      },
      "scores": [
        {
          "criterion_id": "tech-implementation",
          "score": 3.3893,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 9.0,
            "corrected": 7.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "design",
          "score": 2.1227,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 4.0,
            "corrected": 2.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 2.9227,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 9.0,
            "corrected": 7.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 3.1227,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 9.0,
            "corrected": 7.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
          }
        }
      ],
      "final_score": 57.79,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 9.0,
          "corrected": 7.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 4.0,
          "corrected": 2.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 9.0,
          "corrected": 7.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 9.0,
          "corrected": 7.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:46:08.377401+00:00"
    }
  },
  {
    "label": "MeshSight",
    "record": {
      "run_id": "8efe9da5-0f9a-4aad-a060-80b756699172",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "40d9bcfa-3c90-42d3-9182-8a8f854fec0b",
        "rubric_schema_hash": "64b4201a1e49cc52072ecf59965a02d07aa9d96c70c6fc66a9192555a304d763",
        "source": {
          "type": "preset",
          "identifier": "rapid-agent",
          "fetched_at": null,
          "source_text_excerpt": ""
        },
        "scoring_rule": {
          "aggregation": "weighted_sum",
          "final_scale": "0-100"
        },
        "criteria": [
          {
            "id": "tech-implementation",
            "label": "Technological Implementation",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "B1",
              "B2",
              "C1",
              "C2",
              "C3",
              "C4"
            ],
            "descriptor_levels": {
              "1": "Surface — basic wrapper, no novel engineering",
              "2": "Functional — working integration, some custom logic",
              "3": "Solid — non-trivial engineering, edge cases handled",
              "4": "Impressive — complex architecture, custom protocols",
              "5": "Exceptional — publication-worthy depth"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 1 of 4, weight 25%, tie-break first",
            "source_excerpt": "Technological Implementation"
          },
          {
            "id": "design",
            "label": "Design",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "D1",
              "D3",
              "A2"
            ],
            "descriptor_levels": {
              "1": "Confusing first run, no feedback",
              "2": "Works with friction, sparse polish",
              "3": "Smooth happy path, helpful errors",
              "4": "Thoughtful pacing, demo-able in 60s",
              "5": "Memorable, dinner-table-retellable UX"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 2 of 4, weight 25%, tie-break second",
            "source_excerpt": "Design"
          },
          {
            "id": "potential-impact",
            "label": "Potential Impact",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A4",
              "A1"
            ],
            "descriptor_levels": {
              "1": "Niche, unclear who benefits",
              "2": "Plausible benefit for a small group",
              "3": "Clear benefit for a defined audience",
              "4": "Broad impact across a real market",
              "5": "Category-defining, large addressable impact"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 3 of 4, weight 25%, tie-break third",
            "source_excerpt": "Potential Impact"
          },
          {
            "id": "quality-of-idea",
            "label": "Quality of the Idea",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A1",
              "A3"
            ],
            "descriptor_levels": {
              "1": "Recognizable wrapper pattern",
              "2": "Familiar pattern with one twist",
              "3": "Non-obvious, well-motivated concept",
              "4": "Pattern not seen in prior winners",
              "5": "Defines a genuinely new pattern"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 4 of 4, weight 25%, tie-break fourth",
            "source_excerpt": "Quality of the Idea"
          }
        ],
        "tie_breakers": [
          {
            "order": 1,
            "criterion_id": "tech-implementation"
          },
          {
            "order": 2,
            "criterion_id": "design"
          },
          {
            "order": 3,
            "criterion_id": "potential-impact"
          },
          {
            "order": 4,
            "criterion_id": "quality-of-idea"
          }
        ],
        "threshold_gates": [
          {
            "id": "phoenix-mcp-runtime",
            "condition": "Must call the Phoenix MCP server at runtime (Arize Stage-1)",
            "check": "automated"
          },
          {
            "id": "gemini-google-stack",
            "condition": "Uses Gemini + Google Cloud Agent Builder + a partner MCP server",
            "check": "manual"
          },
          {
            "id": "public-oss-repo",
            "condition": "Public repository with an OSI-approved license",
            "check": "manual"
          },
          {
            "id": "demo-video",
            "condition": "<=3 minute demo video on YouTube/Vimeo (English or EN subtitles)",
            "check": "manual"
          }
        ],
        "weights_vector": [
          0.25,
          0.25,
          0.25,
          0.25
        ],
        "confidence": 1.0,
        "warnings": []
      },
      "scores": [
        {
          "criterion_id": "tech-implementation",
          "score": 2.9227,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 8.0,
            "corrected": 6.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "design",
          "score": 2.1227,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 4.0,
            "corrected": 2.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 2.7893,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 8.0,
            "corrected": 6.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 2.5893,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 7.0,
            "corrected": 5.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
          }
        }
      ],
      "final_score": 52.12,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 8.0,
          "corrected": 6.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 4.0,
          "corrected": 2.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 8.0,
          "corrected": 6.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 7.0,
          "corrected": 5.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:46:19.630429+00:00"
    }
  },
  {
    "label": "QuickWrap",
    "record": {
      "run_id": "2ce721f8-0dd9-4051-a7c8-874b0a08d148",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "e80860a0-a183-48e2-a562-9b7b9ad8be7a",
        "rubric_schema_hash": "64b4201a1e49cc52072ecf59965a02d07aa9d96c70c6fc66a9192555a304d763",
        "source": {
          "type": "preset",
          "identifier": "rapid-agent",
          "fetched_at": null,
          "source_text_excerpt": ""
        },
        "scoring_rule": {
          "aggregation": "weighted_sum",
          "final_scale": "0-100"
        },
        "criteria": [
          {
            "id": "tech-implementation",
            "label": "Technological Implementation",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "B1",
              "B2",
              "C1",
              "C2",
              "C3",
              "C4"
            ],
            "descriptor_levels": {
              "1": "Surface — basic wrapper, no novel engineering",
              "2": "Functional — working integration, some custom logic",
              "3": "Solid — non-trivial engineering, edge cases handled",
              "4": "Impressive — complex architecture, custom protocols",
              "5": "Exceptional — publication-worthy depth"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 1 of 4, weight 25%, tie-break first",
            "source_excerpt": "Technological Implementation"
          },
          {
            "id": "design",
            "label": "Design",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "D1",
              "D3",
              "A2"
            ],
            "descriptor_levels": {
              "1": "Confusing first run, no feedback",
              "2": "Works with friction, sparse polish",
              "3": "Smooth happy path, helpful errors",
              "4": "Thoughtful pacing, demo-able in 60s",
              "5": "Memorable, dinner-table-retellable UX"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 2 of 4, weight 25%, tie-break second",
            "source_excerpt": "Design"
          },
          {
            "id": "potential-impact",
            "label": "Potential Impact",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A4",
              "A1"
            ],
            "descriptor_levels": {
              "1": "Niche, unclear who benefits",
              "2": "Plausible benefit for a small group",
              "3": "Clear benefit for a defined audience",
              "4": "Broad impact across a real market",
              "5": "Category-defining, large addressable impact"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 3 of 4, weight 25%, tie-break third",
            "source_excerpt": "Potential Impact"
          },
          {
            "id": "quality-of-idea",
            "label": "Quality of the Idea",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A1",
              "A3"
            ],
            "descriptor_levels": {
              "1": "Recognizable wrapper pattern",
              "2": "Familiar pattern with one twist",
              "3": "Non-obvious, well-motivated concept",
              "4": "Pattern not seen in prior winners",
              "5": "Defines a genuinely new pattern"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 4 of 4, weight 25%, tie-break fourth",
            "source_excerpt": "Quality of the Idea"
          }
        ],
        "tie_breakers": [
          {
            "order": 1,
            "criterion_id": "tech-implementation"
          },
          {
            "order": 2,
            "criterion_id": "design"
          },
          {
            "order": 3,
            "criterion_id": "potential-impact"
          },
          {
            "order": 4,
            "criterion_id": "quality-of-idea"
          }
        ],
        "threshold_gates": [
          {
            "id": "phoenix-mcp-runtime",
            "condition": "Must call the Phoenix MCP server at runtime (Arize Stage-1)",
            "check": "automated"
          },
          {
            "id": "gemini-google-stack",
            "condition": "Uses Gemini + Google Cloud Agent Builder + a partner MCP server",
            "check": "manual"
          },
          {
            "id": "public-oss-repo",
            "condition": "Public repository with an OSI-approved license",
            "check": "manual"
          },
          {
            "id": "demo-video",
            "condition": "<=3 minute demo video on YouTube/Vimeo (English or EN subtitles)",
            "check": "manual"
          }
        ],
        "weights_vector": [
          0.25,
          0.25,
          0.25,
          0.25
        ],
        "confidence": 1.0,
        "warnings": []
      },
      "scores": [
        {
          "criterion_id": "tech-implementation",
          "score": 1.3333,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 1.0,
            "corrected": 0.0,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "design",
          "score": 1.656,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 2.0,
            "corrected": 0.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 1.5893,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 2.0,
            "corrected": 0.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 1.4,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 1.0,
            "corrected": 0.0,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
          }
        }
      ],
      "final_score": 29.89,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 1.0,
          "corrected": 0.0,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 2.0,
          "corrected": 0.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 2.0,
          "corrected": 0.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 1.0,
          "corrected": 0.0,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:46:06.263115+00:00"
    }
  },
  {
    "label": "TodoZap",
    "record": {
      "run_id": "f2b50357-ee66-486c-967d-514ff4a842ed",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "98b2ea52-96f1-4398-bd83-fb3a7d0c3152",
        "rubric_schema_hash": "64b4201a1e49cc52072ecf59965a02d07aa9d96c70c6fc66a9192555a304d763",
        "source": {
          "type": "preset",
          "identifier": "rapid-agent",
          "fetched_at": null,
          "source_text_excerpt": ""
        },
        "scoring_rule": {
          "aggregation": "weighted_sum",
          "final_scale": "0-100"
        },
        "criteria": [
          {
            "id": "tech-implementation",
            "label": "Technological Implementation",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "B1",
              "B2",
              "C1",
              "C2",
              "C3",
              "C4"
            ],
            "descriptor_levels": {
              "1": "Surface — basic wrapper, no novel engineering",
              "2": "Functional — working integration, some custom logic",
              "3": "Solid — non-trivial engineering, edge cases handled",
              "4": "Impressive — complex architecture, custom protocols",
              "5": "Exceptional — publication-worthy depth"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 1 of 4, weight 25%, tie-break first",
            "source_excerpt": "Technological Implementation"
          },
          {
            "id": "design",
            "label": "Design",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "D1",
              "D3",
              "A2"
            ],
            "descriptor_levels": {
              "1": "Confusing first run, no feedback",
              "2": "Works with friction, sparse polish",
              "3": "Smooth happy path, helpful errors",
              "4": "Thoughtful pacing, demo-able in 60s",
              "5": "Memorable, dinner-table-retellable UX"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 2 of 4, weight 25%, tie-break second",
            "source_excerpt": "Design"
          },
          {
            "id": "potential-impact",
            "label": "Potential Impact",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A4",
              "A1"
            ],
            "descriptor_levels": {
              "1": "Niche, unclear who benefits",
              "2": "Plausible benefit for a small group",
              "3": "Clear benefit for a defined audience",
              "4": "Broad impact across a real market",
              "5": "Category-defining, large addressable impact"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 3 of 4, weight 25%, tie-break third",
            "source_excerpt": "Potential Impact"
          },
          {
            "id": "quality-of-idea",
            "label": "Quality of the Idea",
            "weight": 0.25,
            "scale": 5,
            "bmad_mapping": [
              "A1",
              "A3"
            ],
            "descriptor_levels": {
              "1": "Recognizable wrapper pattern",
              "2": "Familiar pattern with one twist",
              "3": "Non-obvious, well-motivated concept",
              "4": "Pattern not seen in prior winners",
              "5": "Defines a genuinely new pattern"
            },
            "evidence_required": true,
            "source_clause": "Judging criterion 4 of 4, weight 25%, tie-break fourth",
            "source_excerpt": "Quality of the Idea"
          }
        ],
        "tie_breakers": [
          {
            "order": 1,
            "criterion_id": "tech-implementation"
          },
          {
            "order": 2,
            "criterion_id": "design"
          },
          {
            "order": 3,
            "criterion_id": "potential-impact"
          },
          {
            "order": 4,
            "criterion_id": "quality-of-idea"
          }
        ],
        "threshold_gates": [
          {
            "id": "phoenix-mcp-runtime",
            "condition": "Must call the Phoenix MCP server at runtime (Arize Stage-1)",
            "check": "automated"
          },
          {
            "id": "gemini-google-stack",
            "condition": "Uses Gemini + Google Cloud Agent Builder + a partner MCP server",
            "check": "manual"
          },
          {
            "id": "public-oss-repo",
            "condition": "Public repository with an OSI-approved license",
            "check": "manual"
          },
          {
            "id": "demo-video",
            "condition": "<=3 minute demo video on YouTube/Vimeo (English or EN subtitles)",
            "check": "manual"
          }
        ],
        "weights_vector": [
          0.25,
          0.25,
          0.25,
          0.25
        ],
        "confidence": 1.0,
        "warnings": []
      },
      "scores": [
        {
          "criterion_id": "tech-implementation",
          "score": 1.3333,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 1.0,
            "corrected": 0.0,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "design",
          "score": 1.7893,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 2.0,
            "corrected": 0.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 1.456,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 2.0,
            "corrected": 0.84,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 1.3333,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 1.0,
            "corrected": 0.0,
            "mean_delta": 1.45,
            "n": 7,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
          }
        }
      ],
      "final_score": 29.56,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 1.0,
          "corrected": 0.0,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 2.0,
          "corrected": 0.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 2.0,
          "corrected": 0.84,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.45, n=7)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 1.0,
          "corrected": 0.0,
          "mean_delta": 1.45,
          "n": 7,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.45, n=7)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:46:04.600239+00:00"
    }
  }
]
) as unknown as SampleEntry[];
