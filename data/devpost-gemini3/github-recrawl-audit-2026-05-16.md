# Gemini 3 Devpost GitHub Repo Recrawl/Audit — 2026-05-16

## Request
Re-run the full crawl and check whether GitHub repository collection missed projects.

## Existing dataset
- Path: `docs/generated/devpost-gemini3-full/gemini3_dataset.json`
- Projects: 4,493
- Original direct valid GitHub-repo projects: 2,380
- Original direct unique valid repos: 2,505

## Existing-field robust audit
A robust scan over all already-captured project fields found GitHub repo candidates that were present somewhere in the captured record but missing from `github_repos`.

- Robust GitHub-repo projects: 2,383
- Robust unique repos: 2,508
- Confirmed missed projects from existing fields: 3

### Confirmed missed candidates
| Project | Devpost URL | Missing repo |
|---|---|---|
| Foru AI: Skin & Health Agent | https://devpost.com/software/foru-ai-skin-health-agent | PeixunWu/foryou |
| goStuddy | https://devpost.com/software/gostuddy | abdushakurob/getstuddy |
| Slipstream Control Plane | https://devpost.com/software/slipstream-control-plane | anthony-maio/slipcore |

## Full live recrawl attempt
Started a new full crawler output at:
`docs/generated/devpost-gemini3-full-recrawl-2026-05-16/`

Observed:
- Gallery crawl reached 188 pages / 4,492 submissions in the new live run.
- Detail recrawl began, but after roughly project 174 the HTTP responses changed into AWS WAF/challenge pages. The parser then began emitting project titles as raw URLs, a signature that it was parsing WAF/challenge HTML rather than project pages.
- A browser check to `https://devpost.com/software/landingpageroasterai` also returned `403 Forbidden` with the managed OpenClaw browser.

Conclusion: the fast live recrawl became WAF-blocked and is not valid as a replacement dataset. It was stopped to avoid writing polluted results.

## Current conclusion
- Confirmed collection bug/miss from existing dataset: +3 repo-projects / +3 unique repos.
- Corrected counts from existing data:
  - GitHub repo projects: 2,383 / 4,493 (about 53.0%)
  - Unique GitHub repos: 2,508
- Further live recrawl requires slower crawl/backoff or a browser/session path that can pass Devpost WAF.
