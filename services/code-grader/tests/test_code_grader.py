from pathlib import Path

from glasshat.code_grader import grade_repo


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
