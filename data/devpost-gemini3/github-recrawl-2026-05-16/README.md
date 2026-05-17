# GitHub Repo Recrawl — 2026-05-16

Slow, WAF-aware live recrawl of all Gemini 3 Devpost project pages to verify GitHub repository links.

## Summary

- Finished: `2026-05-16T18:53:21Z`
- Total projects: `4,493`
- Checked: `4,493`
- Remaining: `0`
- Projects with GitHub repos: `2,380`
- Unique repos: `2,505`
- Errors: `3`
- WAF events: `0`

## Files

- `summary.json` — aggregate crawl status and counts
- `results.jsonl` — one JSON record per checked Devpost project

## Known Exceptions

- `Menu Assistant` — transient network error: `No route to host`
- `NEURIX` — transient network error: `No route to host`
- `Welcome to Aether` — `404` / non-project-page response
