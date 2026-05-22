# services/code-grader (`glasshat.code_grader`)

Static repo heuristics — languages, LOC, tests/CI presence, README excerpt — that
produce a `RepoFacts` object. Implemented and tested as a standalone module. It is
**not wired into the default deck-only evaluation path** (the live pipeline indexes
`deck_text`); wiring `repo_url` → grader → retrieval is a documented next step.
No Qdrant — facts flow into the in-code retrieval index.
