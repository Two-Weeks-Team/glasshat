# Gemini 3 Devpost Crawl Dataset

This directory contains the full crawl of the **Gemini 3 Hackathon** on Devpost, plus a final slow GitHub repository recrawl.

- Source hackathon: <https://gemini3.devpost.com/>
- Rules page: <https://gemini3.devpost.com/rules>
- Project gallery: <https://gemini3.devpost.com/project-gallery>
- Full crawl finished: `2026-05-15T11:41:01Z`
- Submissions collected: `4,493`
- Project detail pages fetched: `4,493`
- Winner-labelled submissions in collected set: `13`
- GitHub recrawl finished: `2026-05-16T18:53:21Z`
- GitHub recrawl checked: `4,493 / 4,493`
- Projects with live GitHub repos: `2,380`
- Unique live GitHub repos: `2,505`
- GitHub recrawl errors: `3`
- WAF events: `0`

## Quick Start

The hit@13 **golden set** — used by `experiments/build_golden_set.py`, the Arize AX
experiment (`arize_experiment.py`), and the calibration tests — is the small, tracked pair:

```text
data/devpost-gemini3/submissions.json   # gallery submissions + is_winner flag
data/devpost-gemini3/winners.json       # the 13 Winner-badged entries
```

> **The raw scrape is gitignored.** `gemini3_dataset.json` (45 MB) and `projects.json`
> (42 MB) are the full Devpost-gallery scrape. They are **gitignored** (see `.gitignore`)
> to respect Devpost's terms on redistributing scraped submissions and to keep the repo
> lean — nothing in the codebase imports them (verified by `grep`). They were derived from
> the public gallery at the URLs above; **re-fetch from those pages** if you need the raw
> dump. The experiment and tests do **not** need them — they run on the tracked golden set.

## Files

| File | Purpose |
|---|---|
| `gemini3_dataset.json` | Full combined dataset: crawl metadata, hackathon metadata, overview, rules references, submissions, winners, projects |
| `projects.json` | Detailed data from each project page |
| `submissions.json` | Gallery-level submissions |
| `submissions.csv` | CSV version of gallery-level submissions |
| `winners.json` | Gallery entries marked with a Devpost `Winner` badge |
| `rules.txt` | Hackathon rules in plain text |
| `rules.html` | Raw HTML snapshot of the rules page |
| `summary_counts.json` | Aggregate counts for the full crawl |
| `github_existing_field_audit.json` | Audit of GitHub fields from the full crawl dataset |
| `github-recrawl-audit-2026-05-16.md` | Human-readable GitHub field audit |
| `github-recrawl-2026-05-16/` | Final slow live GitHub recrawl outputs |

## High-Level Counts

```json
{
  "submissions": 4493,
  "projects": 4493,
  "winners": 13,
  "github_recrawl_checked": 4493,
  "github_recrawl_remaining": 0,
  "projects_with_github_live": 2380,
  "unique_repos_live": 2505,
  "github_recrawl_errors": 3,
  "waf_events": 0
}
```

Notes:

- Not every Devpost project includes a GitHub link.
- Empty arrays/strings usually mean the public project page did not expose that field.
- The `github-recrawl-2026-05-16/` outputs are the final verified live GitHub-link pass.
