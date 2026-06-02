import asyncio
import base64
from pathlib import Path

import httpx
import pytest
from glasshat.agents.types import RepoFacts
from glasshat.code_grader import (
    GitHubApiRepoGrader,
    fetch_repo_facts,
    grade_repo,
    parse_github_url,
    repo_facts_to_chunks,
)


def test_grade_repo_detects_languages_tests_ci_readme(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('hi')\nprint('bye')\n")
    (tmp_path / "app.js").write_text("console.log(1)\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")
    (tmp_path / "README.md").write_text("# My Project\nGreat stuff here.\n")

    facts = grade_repo(str(tmp_path), url="https://github.com/x/y")
    assert facts.url == "https://github.com/x/y"
    assert facts.languages[".py"] == 2  # main.py + tests/test_x.py
    assert facts.languages[".js"] == 1
    assert facts.has_tests is True
    assert facts.has_ci is True
    assert "My Project" in facts.readme_excerpt
    assert facts.loc > 0
    assert facts.heuristics["source_files"] == 3


def test_grade_empty_repo(tmp_path: Path) -> None:
    facts = grade_repo(str(tmp_path), url="u")
    assert facts.has_tests is False
    assert facts.has_ci is False
    assert facts.languages == {}
    assert facts.loc == 0


def test_grade_repo_ignores_vendor_dirs(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dep.js").write_text("x\n")
    (tmp_path / "real.py").write_text("y\n")
    facts = grade_repo(str(tmp_path), url="u")
    assert ".js" not in facts.languages  # node_modules ignored
    assert facts.languages[".py"] == 1


# --- GitHub REST metadata-only path (SSRF gate) -----------------------------


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://github.com/acme/widget", ("acme", "widget")),
        ("https://github.com/acme/widget.git", ("acme", "widget")),
        ("https://github.com/acme/widget/", ("acme", "widget")),
        ("https://github.com/A_b-c.d/Repo_1", ("A_b-c.d", "Repo_1")),
    ],
)
def test_parse_github_url_accepts_canonical(url: str, expected: tuple[str, str]) -> None:
    assert parse_github_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/acme/widget",  # not https
        "https://gitlab.com/acme/widget",  # wrong host
        "https://example.com/acme/widget",  # arbitrary host (SSRF attempt)
        "https://github.com/acme",  # no repo segment
        "https://github.com/acme/widget/tree/main",  # extra path
        "git@github.com:acme/widget.git",  # ssh
        "https://raw.githubusercontent.com/acme/widget/main/x",  # other github host
        "",
    ],
)
def test_parse_github_url_rejects_non_canonical(url: str) -> None:
    assert parse_github_url(url) is None


def test_repo_facts_to_chunks_emits_provenance_ids() -> None:
    facts = RepoFacts(
        url="https://github.com/acme/widget",
        languages={"Python": 90000, "TypeScript": 10000},
        loc=0,
        has_tests=True,
        has_ci=True,
        readme_excerpt="A multi-agent evaluator.",
        heuristics={
            "primary_language": "Python",
            "size_kb": 42,
            "stargazers": 7,
            "description": "x",
        },
    )
    chunks = repo_facts_to_chunks(facts)
    ids = {c.id for c in chunks}
    assert ids == {"repo:readme", "repo:languages", "repo:facts"}
    assert all(c.source == "repo" for c in chunks)
    langs = next(c for c in chunks if c.id == "repo:languages")
    assert "Python (90000 bytes)" in langs.text  # sorted by byte share desc


def test_repo_facts_to_chunks_skips_empty_readme() -> None:
    facts = RepoFacts(url="u", languages={}, readme_excerpt="   ")
    ids = {c.id for c in repo_facts_to_chunks(facts)}
    assert "repo:readme" not in ids
    assert "repo:languages" not in ids  # empty languages skipped too
    assert ids == {"repo:facts"}  # facts chunk always present


def _mock_github(handler_routes: dict[str, httpx.Response]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return handler_routes.get(request.url.path, httpx.Response(404, json={}))

    return httpx.MockTransport(handler)


def test_fetch_repo_facts_parses_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    readme_b64 = base64.b64encode(b"# Widget\nA fast multi-agent tool.").decode()
    routes = {
        "/repos/acme/widget": httpx.Response(
            200,
            json={
                "size": 128,
                "stargazers_count": 9,
                "language": "Python",
                "default_branch": "main",
                "description": "a tool",
            },
        ),
        "/repos/acme/widget/languages": httpx.Response(
            200, json={"Python": 90000, "TypeScript": 10000}
        ),
        "/repos/acme/widget/readme": httpx.Response(
            200, json={"encoding": "base64", "content": readme_b64}
        ),
        "/repos/acme/widget/contents/.github/workflows": httpx.Response(
            200, json=[{"name": "ci.yml"}]
        ),
        "/repos/acme/widget/contents/tests": httpx.Response(200, json=[{"name": "test_x.py"}]),
    }
    transport = _mock_github(routes)
    orig = httpx.AsyncClient

    def patched(*args: object, **kwargs: object) -> httpx.AsyncClient:
        kwargs["transport"] = transport
        return orig(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(httpx, "AsyncClient", patched)

    facts = asyncio.run(fetch_repo_facts("https://github.com/acme/widget"))
    assert facts.url == "https://github.com/acme/widget"
    assert facts.languages == {"Python": 90000, "TypeScript": 10000}
    assert facts.has_ci is True
    assert facts.has_tests is True
    assert "multi-agent" in facts.readme_excerpt
    assert facts.heuristics["primary_language"] == "Python"
    assert facts.heuristics["size_kb"] == 128
    assert facts.loc == 0  # honest: no clone, no line count


def test_fetch_repo_facts_rejects_non_github_url() -> None:
    with pytest.raises(ValueError, match="github.com"):
        asyncio.run(fetch_repo_facts("https://evil.example.com/acme/widget"))


def test_grader_returns_empty_for_unsupported_url() -> None:
    # A non-github URL never triggers a network call — chunks_for returns [].
    grader = GitHubApiRepoGrader()
    assert asyncio.run(grader.chunks_for("https://gitlab.com/a/b")) == []
