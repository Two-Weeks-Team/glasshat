// AUTO-GENERATED sample cohort — REAL RunRecords captured from the live API
// (POST /api/evaluate on gemini-3.1-flash-lite, rapid-agent rubric, 2026-05-22).
// Used as the /judge first-paint sample so the ranked result is visible before
// any round-trip; "Run cohort" re-evaluates live. Not fabricated — see README.
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
      "run_id": "9b046a40-f085-447f-a25e-9794ffb51ccd",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "b893ba5a-0ca2-4437-bc55-b8f568ad0e02",
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
          "score": 2.7467,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 4.0,
            "corrected": 3.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "design",
          "score": 2.3467,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 4.0,
            "corrected": 3.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 3.08,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 9.0,
            "corrected": 8.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 3.08,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 9.0,
            "corrected": 8.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
          }
        }
      ],
      "final_score": 56.27,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 4.0,
          "corrected": 3.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 4.0,
          "corrected": 3.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 9.0,
          "corrected": 8.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 9.0,
          "corrected": 8.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:26:58.859021+00:00"
    }
  },
  {
    "label": "MeshSight",
    "record": {
      "run_id": "9b1b3737-b1d3-4bef-b1cb-edc3908c0cbb",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "528982a8-0d9c-456d-8da5-3c1e1415803b",
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
          "score": 2.88,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 7.0,
            "corrected": 6.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "design",
          "score": 2.4133,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 8.0,
            "corrected": 7.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 2.8133,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 8.0,
            "corrected": 7.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 2.8133,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 8.0,
            "corrected": 7.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
          }
        }
      ],
      "final_score": 54.6,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 7.0,
          "corrected": 6.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 8.0,
          "corrected": 7.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 8.0,
          "corrected": 7.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 8.0,
          "corrected": 7.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:27:04.948759+00:00"
    }
  },
  {
    "label": "QuickWrap",
    "record": {
      "run_id": "cad052e6-47de-4c70-aae5-74309abdd185",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "e72782c0-ad97-4658-b34e-af62e4735c06",
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
          "score": 1.3467,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 1.0,
            "corrected": 0.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "design",
          "score": 1.68,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 2.0,
            "corrected": 1.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 1.68,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 2.0,
            "corrected": 1.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 1.3467,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 1.0,
            "corrected": 0.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
          }
        }
      ],
      "final_score": 30.27,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 1.0,
          "corrected": 0.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 2.0,
          "corrected": 1.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 2.0,
          "corrected": 1.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 1.0,
          "corrected": 0.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:27:27.595740+00:00"
    }
  },
  {
    "label": "TodoZap",
    "record": {
      "run_id": "e1f64345-a241-482d-b875-3e487a66c12f",
      "rubric": {
        "schema_version": "1.0",
        "rubric_id": "22d8c116-2c95-4207-842d-d9ca2c4d6821",
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
          "score": 1.4133,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "tech-implementation",
            "original": 2.0,
            "corrected": 1.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "design",
          "score": 1.7467,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "design",
            "original": 2.0,
            "corrected": 1.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "potential-impact",
          "score": 1.48,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "potential-impact",
            "original": 2.0,
            "corrected": 1.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
          }
        },
        {
          "criterion_id": "quality-of-idea",
          "score": 1.4133,
          "evidence_refs": [
            "deck-0"
          ],
          "audit": {
            "hat": "yellow",
            "criterion_id": "quality-of-idea",
            "original": 2.0,
            "corrected": 1.2,
            "mean_delta": 1.0,
            "n": 14,
            "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
          }
        }
      ],
      "final_score": 30.27,
      "audit_corrections": [
        {
          "hat": "yellow",
          "criterion_id": "tech-implementation",
          "original": 2.0,
          "corrected": 1.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'tech-implementation' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "design",
          "original": 2.0,
          "corrected": 1.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'design' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "potential-impact",
          "original": 2.0,
          "corrected": 1.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'potential-impact' (evidence=low, mean_delta=+1.00, n=14)"
        },
        {
          "hat": "yellow",
          "criterion_id": "quality-of-idea",
          "original": 2.0,
          "corrected": 1.2,
          "mean_delta": 1.0,
          "n": 14,
          "reason": "yellow over/under-confident on 'quality-of-idea' (evidence=low, mean_delta=+1.00, n=14)"
        }
      ],
      "mode": "judge",
      "created_at": "2026-05-22T14:27:12.798991+00:00"
    }
  }
]
) as unknown as SampleEntry[];
