"""Glasshat code grader: static facts about a repository.

Two paths, both read-only and non-executing:

* :func:`fetch_repo_facts` — the **deployed** path. Talks only to the fixed
  ``api.github.com`` host over GitHub's REST API (metadata only: repo summary,
  language byte-mix, README, and presence probes for ``tests`` / CI). It never
  clones and never follows redirects, so a hostile ``repo_url`` cannot redirect
  the client at an internal address (SSRF-safe by construction).
* :func:`grade_repo` / :func:`clone_and_grade` — the offline path over an
  already-present directory; kept for local/spike use, not used by the live
  deploy (the no-clone policy from the security review).

Both produce a :class:`~glasshat.agents.types.RepoFacts`. Never executes user
code.
"""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from glasshat.agents.types import Chunk, RepoFacts
from glasshat.shared.github_url import parse_github_url

SOURCE_EXTS = frozenset(
    {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".go",
        ".rs",
        ".java",
        ".rb",
        ".c",
        ".cpp",
        ".cc",
        ".h",
        ".hpp",
        ".cs",
        ".kt",
        ".swift",
        ".php",
        ".scala",
    }
)
_IGNORED_DIRS = frozenset({".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"})
_README_NAMES = ("README.md", "README.rst", "README.txt", "readme.md")


def _ignored(path: Path, root: Path) -> bool:
    return any(part in _IGNORED_DIRS for part in path.relative_to(root).parts)


def _count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))
    except OSError:  # pragma: no cover - unreadable file
        return 0


def grade_repo(path: str, *, url: str = "") -> RepoFacts:
    """Run static heuristics over an already-present repository directory."""
    root = Path(path)
    languages: dict[str, int] = {}
    loc = 0
    source_files = 0
    has_tests = False

    for file_path in root.rglob("*"):
        if not file_path.is_file() or _ignored(file_path, root):
            continue
        name = file_path.name.lower()
        if name.startswith("test_") or name.endswith(
            ("_test.py", ".test.ts", ".test.js", ".spec.ts")
        ):
            has_tests = True
        ext = file_path.suffix.lower()
        if ext in SOURCE_EXTS:
            languages[ext] = languages.get(ext, 0) + 1
            loc += _count_lines(file_path)
            source_files += 1

    has_tests = has_tests or any((root / d).is_dir() for d in ("tests", "test", "__tests__"))
    has_ci = (root / ".github" / "workflows").is_dir() or (root / ".gitlab-ci.yml").exists()

    readme_excerpt = ""
    for name in _README_NAMES:
        candidate = root / name
        if candidate.exists():
            readme_excerpt = candidate.read_text(encoding="utf-8", errors="ignore")[:500]
            break

    return RepoFacts(
        url=url,
        languages=languages,
        loc=loc,
        has_tests=has_tests,
        has_ci=has_ci,
        readme_excerpt=readme_excerpt,
        heuristics={"source_files": source_files},
    )


async def clone_and_grade(url: str) -> RepoFacts:  # pragma: no cover - requires git + network
    import asyncio

    with tempfile.TemporaryDirectory() as tmp:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            "--depth",
            "1",
            url,
            tmp + "/repo",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"git clone failed: {stderr.decode(errors='ignore')}")
        return grade_repo(tmp + "/repo", url=url)


# --- GitHub REST metadata-only path (the deployed grader) -------------------

# The canonical github.com URL shape + (owner, repo) parser is the single SSRF
# gate, shared with the API input boundary — see glasshat.shared.github_url
# (re-exported `parse_github_url` above). We extract (owner, repo) and then talk
# *exclusively* to the fixed api.github.com host; the user URL is never a target.
_GITHUB_API = "https://api.github.com"


async def fetch_repo_facts(url: str, *, token: str = "", timeout: float = 15.0) -> RepoFacts:
    """Fetch repository facts from the GitHub REST API — metadata only, no clone.

    Raises :class:`ValueError` for a non-github.com URL (the caller treats that
    as "deck-only"). Network/HTTP errors propagate to the caller, which falls
    back to a deck-only run. ``token`` is an optional PAT to lift the 60 req/hr
    unauthenticated rate limit; public repos work without it.
    """
    import httpx

    parsed = parse_github_url(url)
    if parsed is None:
        raise ValueError("only https://github.com/<owner>/<repo> URLs are supported")
    owner, repo = parsed
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "glasshat-code-grader",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(
        base_url=_GITHUB_API, headers=headers, timeout=timeout, follow_redirects=False
    ) as client:
        repo_resp = await client.get(f"/repos/{owner}/{repo}")
        repo_resp.raise_for_status()
        meta = repo_resp.json()

        languages: dict[str, int] = {}
        lang_resp = await client.get(f"/repos/{owner}/{repo}/languages")
        if lang_resp.status_code == 200:
            languages = {
                k: int(v) for k, v in lang_resp.json().items() if isinstance(v, int | float)
            }

        readme_excerpt = ""
        readme_resp = await client.get(f"/repos/{owner}/{repo}/readme")
        if readme_resp.status_code == 200:
            payload = readme_resp.json()
            if payload.get("encoding") == "base64" and isinstance(payload.get("content"), str):
                try:
                    readme_excerpt = base64.b64decode(payload["content"]).decode(
                        "utf-8", errors="ignore"
                    )[:500]
                except (ValueError, TypeError):  # pragma: no cover - malformed base64
                    readme_excerpt = ""

        has_ci = await _path_exists(client, owner, repo, ".github/workflows")
        # Short-circuit: stop probing once a test directory is found (saves API
        # calls / rate budget rather than eagerly running all three).
        has_tests = False
        for test_dir in ("tests", "test", "__tests__"):
            if await _path_exists(client, owner, repo, test_dir):
                has_tests = True
                break

    return RepoFacts(
        url=url,
        languages=languages,
        loc=0,  # not derivable from metadata without a clone; left honest at 0
        has_tests=has_tests,
        has_ci=has_ci,
        readme_excerpt=readme_excerpt,
        heuristics={
            "size_kb": int(meta.get("size", 0) or 0),
            "stargazers": int(meta.get("stargazers_count", 0) or 0),
            "primary_language": meta.get("language") or "",
            "default_branch": meta.get("default_branch") or "",
            "description": (meta.get("description") or "")[:200],
            "source": "github-api-metadata",
        },
    )


async def _path_exists(client: object, owner: str, repo: str, path: str) -> bool:
    """True when ``GET /contents/{path}`` returns 200 (directory/file present)."""
    resp = await client.get(f"/repos/{owner}/{repo}/contents/{path}")  # type: ignore[attr-defined]
    return bool(resp.status_code == 200)


def repo_facts_to_chunks(facts: RepoFacts) -> list[Chunk]:
    """Project :class:`RepoFacts` into retrievable chunks with provenance ids.

    Ids are self-documenting (``repo:readme`` / ``repo:languages`` /
    ``repo:facts``) so the UI can show repo-sourced evidence distinctly from
    deck quotes. Each chunk carries ``source="repo"``. Empty facets are skipped
    so an empty README never produces a dangling reference.
    """
    chunks: list[Chunk] = []
    if facts.readme_excerpt.strip():
        chunks.append(
            Chunk(
                id="repo:readme",
                text=f"Repository README excerpt:\n{facts.readme_excerpt}",
                source="repo",
            )
        )
    if facts.languages:
        lang_line = ", ".join(
            f"{lang} ({count} bytes)"
            for lang, count in sorted(facts.languages.items(), key=lambda kv: kv[1], reverse=True)
        )
        chunks.append(
            Chunk(
                id="repo:languages",
                text=f"Repository languages by byte share: {lang_line}.",
                source="repo",
            )
        )
    facts_line = (
        f"Repository facts: tests present={facts.has_tests}; CI configured={facts.has_ci}; "
        f"primary language={facts.heuristics.get('primary_language', '')}; "
        f"size={facts.heuristics.get('size_kb', 0)} KB; "
        f"stars={facts.heuristics.get('stargazers', 0)}; "
        f"description={facts.heuristics.get('description', '')}"
    )
    chunks.append(Chunk(id="repo:facts", text=facts_line, source="repo"))
    return chunks


class GitHubApiRepoGrader:
    """Engine-facing adapter: ``repo_url`` -> retrievable repo chunks.

    Implements the engine's ``RepoGrader`` protocol. Wraps
    :func:`fetch_repo_facts` (metadata-only, SSRF-safe) and
    :func:`repo_facts_to_chunks`. Returns ``[]`` for a non-github.com URL so the
    engine simply runs deck-only; network errors propagate to the engine's
    bounded wrapper, which also falls back to deck-only.
    """

    def __init__(self, token: str = "", timeout: float = 15.0) -> None:
        self._token = token
        self._timeout = timeout

    async def chunks_for(self, url: str) -> list[Chunk]:
        try:
            facts = await fetch_repo_facts(url, token=self._token, timeout=self._timeout)
        except ValueError:
            # Not a supported github.com URL — deck-only, no network attempted.
            return []
        return repo_facts_to_chunks(facts)
