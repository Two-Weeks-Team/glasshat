"""Canonical GitHub repo-URL validation — the single SSRF gate.

Both the API input boundary (``EvaluationInput.repo_url`` in ``glasshat.agents``)
and the code grader (``glasshat.code_grader``) must accept *exactly* the same URL
shape, otherwise the Pydantic layer can wave through a URL the grader later
rejects (or, worse, a looser ``startswith`` check passes a traversal-ish URL the
strict grader would have caught). Keeping the regex here, used by both, removes
that mismatch.

Only the public ``https://github.com/<owner>/<repo>`` web URL shape is accepted.
Callers extract ``(owner, repo)`` and then talk *exclusively* to the fixed
``api.github.com`` host — the user URL is never used as a request target.
"""

from __future__ import annotations

import re

# `(?:\.git)?/?` tolerates the `.git` suffix and a single trailing slash; the
# `+?` on repo is non-greedy so `.git` is stripped rather than captured.
GITHUB_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)


def parse_github_url(url: str) -> tuple[str, str] | None:
    """Return ``(owner, repo)`` for a ``https://github.com/<owner>/<repo>`` URL.

    Returns ``None`` for anything else (other hosts, ssh URLs, gists, paths with
    extra segments). This is the SSRF gate: a URL that does not parse here never
    triggers a network call.
    """
    match = GITHUB_URL_RE.match(url.strip())
    if match is None:
        return None
    owner, repo = match.group("owner"), match.group("repo")
    # Reject path-traversal-ish or reserved segments defensively.
    if owner in {".", ".."} or repo in {".", ".."}:
        return None
    return owner, repo
