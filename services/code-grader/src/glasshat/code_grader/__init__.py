"""Glasshat code grader: static heuristics over a repository directory.

Clones (shallow, no network egress beyond the URL) and runs read-only static
heuristics — language mix, LOC, test presence, CI presence, README excerpt.
Never executes user code. Produces a :class:`~glasshat.agents.types.RepoFacts`.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from glasshat.agents.types import RepoFacts

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
