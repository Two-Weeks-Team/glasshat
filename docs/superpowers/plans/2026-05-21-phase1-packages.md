# Phase 1 — Foundation + Packages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax. Derives from `2026-05-21-glasshat-roadmap.md`.

**Goal:** Establish the `uv` workspace + CI toolchain and build `packages/shared` (`glasshat.shared`) and `packages/rubric` (`glasshat.rubric`) — the typed contracts and rubric engine — with full TDD and ≥90% coverage, shipping as one CI-green PR on `feat/arize-packages`.

**Architecture:** Python 3.12 `uv` workspace, PEP-420 namespace package `glasshat.*`. `glasshat.shared` holds config/ids/errors/enums/abstraction Protocols. `glasshat.rubric` holds the `SynthesizedRubric` pydantic model, BMAD vocabulary, 4 presets (rapid-agent corrected to 25/25/25/25 + ordered tie-break), preset loader, custom-YAML validator, the §7 validation pipeline, and canonicalization (`rubric_schema_hash` + `weights_vector`). The pydantic model is the contract source; `synthesized.schema.json` is generated from it and CI-checked for drift.

**Tech Stack:** Python 3.12, uv, pydantic v2, pydantic-settings, PyYAML, pytest, pytest-cov, ruff, mypy. GitHub Actions CI.

---

## File Structure

```
pyproject.toml                       # root: uv workspace, ruff/mypy/pytest config, coverage gate
.python-version                      # 3.12
.gitignore                           # add var/, .venv/, __pycache__, .coverage, etc.
.env.example                         # rewritten: Qdrant removed, ADK, Gemini-only
.github/workflows/ci.yml             # lint + typecheck + test + coverage

packages/shared/
  pyproject.toml                     # glasshat-shared, namespace pkg
  src/glasshat/shared/__init__.py
  src/glasshat/shared/ids.py         # canonical_json, sha256_hex, new_uuid
  src/glasshat/shared/errors.py      # GlasshatError + subclasses
  src/glasshat/shared/enums.py       # Hat, RunMode, Aggregation, SourceType, SourceKind
  src/glasshat/shared/config.py      # Settings (pydantic-settings), get_settings()
  src/glasshat/shared/protocols.py   # LlmClient, Retrieval, DocStore, BlobStore, Tracer Protocols
  tests/test_ids.py
  tests/test_config.py
  tests/test_enums.py

packages/rubric/
  pyproject.toml                     # glasshat-rubric (dep: glasshat-shared)
  synthesized.schema.json            # generated from SynthesizedRubric, CI-checked
  src/glasshat/rubric/__init__.py
  src/glasshat/rubric/bmad.py        # BMAD_VOCABULARY (17 primitives), is_valid_primitive
  src/glasshat/rubric/models.py      # Criterion, TieBreaker, ThresholdGate, RubricSource, ScoringRule, SynthesizedRubric
  src/glasshat/rubric/canonical.py   # canonicalize, compute_schema_hash, compute_weights_vector
  src/glasshat/rubric/presets.py     # load_preset, list_presets, PRESETS_DIR
  src/glasshat/rubric/validation.py  # validate_rubric, validate_custom_yaml, RubricWarning
  src/glasshat/rubric/schema.py      # synthesized_schema(), schema_matches_disk()
  src/glasshat/rubric/presets/qdrant.yaml
  src/glasshat/rubric/presets/rapid-agent.yaml   # CORRECTED 25/25/25/25 + tie-break order
  src/glasshat/rubric/presets/cmux-aim.yaml
  src/glasshat/rubric/presets/gemini3.yaml
  tests/test_bmad.py
  tests/test_models.py
  tests/test_canonical.py
  tests/test_presets.py
  tests/test_validation.py
  tests/test_schema_sync.py
```

---

## Task 0: Branch + workspace foundation

**Files:** Create `pyproject.toml`, `.python-version`, `.gitignore`, `packages/shared/pyproject.toml`, `packages/shared/src/glasshat/shared/__init__.py`, `packages/rubric/pyproject.toml`, `packages/rubric/src/glasshat/rubric/__init__.py`.

- [ ] **Step 1: Branch.** `git checkout -b feat/arize-packages`
- [ ] **Step 2: Root `pyproject.toml`** — uv workspace, tool config:

```toml
[project]
name = "glasshat"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["glasshat-shared", "glasshat-rubric"]

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
glasshat-shared = { workspace = true }
glasshat-rubric = { workspace = true }

[dependency-groups]
dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.6", "mypy>=1.11", "types-PyYAML"]

[tool.pytest.ini_options]
addopts = "-q --cov=glasshat --cov-report=term-missing --cov-fail-under=90"
testpaths = ["packages/shared/tests", "packages/rubric/tests"]

[tool.ruff]
line-length = 100
target-version = "py312"
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
namespace_packages = true
explicit_package_bases = true
mypy_path = "packages/shared/src:packages/rubric/src"
```

- [ ] **Step 3:** `.python-version` = `3.12`. `.gitignore` add `var/`, `.venv/`, `__pycache__/`, `*.pyc`, `.coverage`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `dist/`.
- [ ] **Step 4: `packages/shared/pyproject.toml`:**

```toml
[project]
name = "glasshat-shared"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.7", "pydantic-settings>=2.3"]
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/glasshat"]
```

- [ ] **Step 5: `packages/rubric/pyproject.toml`** (same shape; deps `glasshat-shared`, `pydantic>=2.7`, `PyYAML>=6`; `[tool.uv.sources] glasshat-shared = { workspace = true }`).
- [ ] **Step 6:** empty `__init__.py` for both `glasshat/shared` and `glasshat/rubric` (namespace: do NOT create `glasshat/__init__.py` — PEP 420 implicit).
- [ ] **Step 7: Smoke test** `packages/shared/tests/test_smoke.py`:

```python
def test_import_namespace():
    import glasshat.shared  # noqa: F401
```

- [ ] **Step 8:** `uv sync` then `uv run pytest packages/shared/tests/test_smoke.py -v` → PASS. `uv run ruff check .` clean. `uv run mypy packages` clean.
- [ ] **Step 9: Commit** `chore(p1): uv workspace + toolchain foundation`.

---

## Task 1: `glasshat.shared.ids` (canonical JSON + hashing)

**Files:** Create `packages/shared/src/glasshat/shared/ids.py`, `packages/shared/tests/test_ids.py`.

- [ ] **Step 1: Failing test** `test_ids.py`:

```python
from glasshat.shared.ids import canonical_json, sha256_hex, new_uuid

def test_canonical_json_is_key_sorted_and_compact():
    a = canonical_json({"b": 1, "a": [3, 2]})
    b = canonical_json({"a": [3, 2], "b": 1})
    assert a == b == '{"a":[3,2],"b":1}'

def test_sha256_hex_is_stable_and_64_hex():
    h = sha256_hex("abc")
    assert h == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert len(h) == 64

def test_new_uuid_unique_v4():
    assert new_uuid() != new_uuid()
    assert len(new_uuid()) == 36
```

- [ ] **Step 2:** `uv run pytest packages/shared/tests/test_ids.py -v` → FAIL (module missing).
- [ ] **Step 3: Implement** `ids.py`:

```python
import hashlib
import json
import uuid
from typing import Any

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def new_uuid() -> str:
    return str(uuid.uuid4())
```

- [ ] **Step 4:** rerun → PASS.
- [ ] **Step 5: Commit** `feat(p1): glasshat.shared.ids canonical json + hashing`.

---

## Task 2: `glasshat.shared.enums` + `errors`

**Files:** Create `enums.py`, `errors.py`, `packages/shared/tests/test_enums.py`.

- [ ] **Step 1: Failing test** `test_enums.py`:

```python
from glasshat.shared.enums import Hat, RunMode, Aggregation, SourceKind
from glasshat.shared.errors import GlasshatError, RubricValidationError

def test_six_hats():
    assert {h.value for h in Hat} == {"blue", "white", "red", "yellow", "black", "green"}

def test_aggregation_values():
    assert Aggregation.WEIGHTED_SUM.value == "weighted_sum"
    assert Aggregation.SIMPLE_AVERAGE.value == "simple_average"
    assert Aggregation.TIE_BREAK_ORDERED.value == "tie_break_ordered"

def test_source_kind():
    assert {s.value for s in SourceKind} == {"preset", "url", "pdf", "custom"}

def test_run_mode():
    assert {m.value for m in RunMode} == {"judge", "participant"}

def test_error_hierarchy():
    assert issubclass(RubricValidationError, GlasshatError)
```

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `enums.py` (str-Enums for Hat, RunMode, Aggregation, SourceKind) and `errors.py`:

```python
# errors.py
class GlasshatError(Exception): ...
class RubricValidationError(GlasshatError): ...
class SynthesisError(GlasshatError): ...
class RetrievalError(GlasshatError): ...
class LlmError(GlasshatError): ...
```

```python
# enums.py
from enum import Enum
class Hat(str, Enum):
    BLUE="blue"; WHITE="white"; RED="red"; YELLOW="yellow"; BLACK="black"; GREEN="green"
class RunMode(str, Enum):
    JUDGE="judge"; PARTICIPANT="participant"
class Aggregation(str, Enum):
    WEIGHTED_SUM="weighted_sum"; SIMPLE_AVERAGE="simple_average"; TIE_BREAK_ORDERED="tie_break_ordered"
class SourceKind(str, Enum):
    PRESET="preset"; URL="url"; PDF="pdf"; CUSTOM="custom"
```

- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(p1): glasshat.shared enums + error hierarchy`.

---

## Task 3: `glasshat.shared.config` (env settings with safe defaults)

**Files:** Create `config.py`, `packages/shared/tests/test_config.py`.

- [ ] **Step 1: Failing test** — settings must load with NO env (defaults) and honor env override:

```python
import os
from glasshat.shared.config import Settings

def test_defaults_load_without_env():
    s = Settings(_env_file=None)
    assert s.google_cloud_region == "us-central1"
    assert s.llm_backend == "mock"          # safe default for tests/CI
    assert s.monitor_backend == "phoenix-local"
    assert s.docstore_backend == "memory"

def test_env_override(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "vertex")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "panelyst-hackathon")
    s = Settings(_env_file=None)
    assert s.llm_backend == "vertex"
    assert s.google_cloud_project == "panelyst-hackathon"
```

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `config.py` using `pydantic_settings.BaseSettings`. Fields (env-mapped, defaults): `google_cloud_project: str = ""`, `google_cloud_region="us-central1"`, gemini model tiers (pro/flash/flash-lite + locations, defaults from `.env.example`), `llm_backend: Literal["vertex","mock"]="mock"`, `monitor_backend="phoenix-local"`, `docstore_backend: Literal["memory","sqlite","firestore"]="memory"`, `blob_backend="local-fs"`, `agent_runtime="adk-local"`. `model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)`. Add `get_settings()` `@lru_cache`.
- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(p1): glasshat.shared.config env settings`.

---

## Task 4: `glasshat.shared.protocols` (abstraction interfaces)

**Files:** Create `protocols.py`, `packages/shared/tests/test_protocols.py`.

- [ ] **Step 1: Failing test** — protocols are runtime-checkable; a minimal impl satisfies them:

```python
from glasshat.shared.protocols import LlmClient, Retrieval

def test_llmclient_protocol_structural():
    class Fake:
        async def generate(self, prompt: str, *, tier: str = "flash", **kw) -> str: return "x"
        async def embed(self, texts: list[str]) -> list[list[float]]: return [[0.0]]
    assert isinstance(Fake(), LlmClient)

def test_retrieval_protocol_structural():
    class FakeR:
        def search(self, query, *, top_k=5, **kw): return []
        def index(self, docs): return None
    assert isinstance(FakeR(), Retrieval)
```

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `protocols.py` with `@runtime_checkable` `Protocol` classes: `LlmClient` (`async generate`, `async embed`), `Retrieval` (`search`, `index`), `DocStore` (`get`, `put`, `query`), `BlobStore` (`put_blob`, `get_blob`), `Tracer` (`span` contextmanager + `set_attr`). Method bodies are `...` (Protocols, not impls — implementations land in P2).
- [ ] **Step 4:** run → PASS. `mypy` clean.
- [ ] **Step 5: Commit** `feat(p1): glasshat.shared.protocols abstraction interfaces`.

---

## Task 5: `glasshat.rubric.bmad` (BMAD vocabulary)

**Files:** Create `bmad.py`, `packages/rubric/tests/test_bmad.py`. (Source: `rubric-synthesis-spec.md` §5 item 2.)

- [ ] **Step 1: Failing test:**

```python
from glasshat.rubric.bmad import BMAD_VOCABULARY, is_valid_primitive

def test_seventeen_primitives():
    assert len(BMAD_VOCABULARY) == 17
    assert set(BMAD_VOCABULARY) >= {"A1","A4","B1","B4","C1","C5","D1","D4"}

def test_labels_present():
    assert BMAD_VOCABULARY["C3"] == "testing"
    assert BMAD_VOCABULARY["A1"] == "problem clarity"

def test_is_valid_primitive():
    assert is_valid_primitive("C1") and not is_valid_primitive("Z9")
```

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `bmad.py` — dict of all 17 from spec §5: A1 problem clarity, A2 target users, A3 differentiation, A4 market impact, B1 stack fit, B2 system design, B3 scalability, B4 feasibility, C1 implementation completeness, C2 code quality, C3 testing, C4 docs, C5 reproducibility, D1 demo clarity, D2 storytelling, D3 visual polish, D4 timing. `is_valid_primitive(code) -> bool`.
- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(p1): glasshat.rubric.bmad 17-primitive vocabulary`.

---

## Task 6: `glasshat.rubric.models` (SynthesizedRubric pydantic contract)

**Files:** Create `models.py`, `packages/rubric/tests/test_models.py`. (Source: `rubric-synthesis-spec.md` §3.)

- [ ] **Step 1: Failing test** — valid rubric constructs; validators reject bad input:

```python
import pytest
from pydantic import ValidationError as PydErr
from glasshat.rubric.models import SynthesizedRubric, Criterion

def _crit(**kw):
    base = dict(id="tech-implementation", label="Tech", weight=0.25, scale=5,
                bmad_mapping=["C1"], descriptor_levels={1:"a",2:"b",3:"c",4:"d",5:"e"},
                evidence_required=True, source_clause="x", source_excerpt="y")
    base.update(kw); return Criterion(**base)

def test_valid_criterion():
    c = _crit(); assert c.id == "tech-implementation" and c.scale == 5

def test_descriptor_levels_must_cover_scale():
    with pytest.raises(PydErr):
        _crit(descriptor_levels={1:"a",2:"b",3:"c"})   # missing 4,5 for scale 5

def test_bmad_mapping_nonempty():
    with pytest.raises(PydErr):
        _crit(bmad_mapping=[])

def test_bmad_mapping_must_be_valid_primitive():
    with pytest.raises(PydErr):
        _crit(bmad_mapping=["Z9"])

def test_weighted_sum_weights_must_total_one():
    crits = [_crit(id=f"c{i}", weight=0.25) for i in range(4)]
    r = SynthesizedRubric.model_validate(_rubric_dict(crits, "weighted_sum"))
    assert abs(sum(c.weight for c in r.criteria) - 1.0) < 0.01
    with pytest.raises(PydErr):
        bad = [_crit(id=f"c{i}", weight=0.5) for i in range(4)]   # sums 2.0
        SynthesizedRubric.model_validate(_rubric_dict(bad, "weighted_sum"))
```

(Provide `_rubric_dict(criteria, aggregation)` helper in the test building the full `SynthesizedRubric` dict with `schema_version="1.0"`, `rubric_id`, `source`, `scoring_rule`, `tie_breakers`, `weights_vector`, `confidence`.)

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `models.py`:
  - `Criterion(BaseModel)`: `id:str`, `label:str`, `weight:float|None`, `scale:int` (∈{5,7,100} or generic int ≥2), `bmad_mapping:list[str]` (min_length=1, each `is_valid_primitive`), `descriptor_levels:dict[int,str]`, `evidence_required:bool=True`, `source_clause:str`, `source_excerpt:str=""`. `@model_validator` enforcing descriptor_levels keys == `set(range(1, scale+1))` (when scale ≤ 10; for scale==100 require keys for documented bands — keep simple: require coverage only when `scale<=10`).
  - `TieBreaker`: `order:int`, `criterion_id:str`.
  - `ThresholdGate`: `id:str`, `condition:str`, `check:Literal["manual","automated"]`.
  - `RubricSource`: `type:SourceKind`, `identifier:str`, `fetched_at:str|None`, `source_text_excerpt:str=""`.
  - `ScoringRule`: `aggregation:Aggregation`, `final_scale:str`.
  - `SynthesizedRubric`: all fields from spec §3 + `@model_validator` enforcing weighted_sum→sum(weights)≈1.0; simple_average→weights all None or equal; tie_breakers reference existing criterion ids; tie_breaker orders are `1..n` unique.
- [ ] **Step 4:** run → PASS. `mypy` clean.
- [ ] **Step 5: Commit** `feat(p1): glasshat.rubric.models SynthesizedRubric contract`.

---

## Task 7: `glasshat.rubric.canonical` (hash + weights vector)

**Files:** Create `canonical.py`, `packages/rubric/tests/test_canonical.py`. (Source: spec §3 `weights_vector`, §5 item 3 canonical order, §8 anchor.)

- [ ] **Step 1: Failing test:**

```python
from glasshat.rubric.canonical import canonicalize, compute_schema_hash, compute_weights_vector
# build two rubrics with criteria in different order but same content
def test_weights_vector_is_alpha_by_criterion_id(make_rubric):
    r = make_rubric(weights={"tech-implementation":0.25,"design":0.25,
                             "potential-impact":0.25,"quality-of-idea":0.25})
    # alpha order: design, potential-impact, quality-of-idea, tech-implementation
    assert compute_weights_vector(r) == [0.25,0.25,0.25,0.25]

def test_schema_hash_order_independent(make_rubric):
    r1 = make_rubric(order=["tech-implementation","design"])
    r2 = make_rubric(order=["design","tech-implementation"])
    assert compute_schema_hash(r1) == compute_schema_hash(r2)

def test_schema_hash_changes_with_weights(make_rubric):
    a = make_rubric(weights={"a":0.5,"b":0.5}); b = make_rubric(weights={"a":0.6,"b":0.4})
    assert compute_schema_hash(a) != compute_schema_hash(b)
```

(Provide a `make_rubric` pytest fixture in `conftest.py` building valid `SynthesizedRubric`s.)

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `canonical.py`: `canonicalize(r)` → dict with criteria sorted by `id`, only structurally-significant fields (id, weight, scale, aggregation, tie_breaker order, bmad_mapping sorted) — exclude volatile fields (rubric_id, fetched_at, confidence, source excerpts). `compute_weights_vector(r)` → `[c.weight or 0.0 for c in sorted(criteria, key=id)]`. `compute_schema_hash(r)` → `sha256_hex(canonical_json(canonicalize(r)))` (reuse `glasshat.shared.ids`).
- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(p1): glasshat.rubric.canonical schema hash + weights vector`.

---

## Task 8: Presets (4 YAML) + loader — **rapid-agent corrected to 25/25/25/25**

**Files:** Create `presets/{qdrant,rapid-agent,cmux-aim,gemini3}.yaml`, `presets.py`, `packages/rubric/tests/test_presets.py`. (Source: spec §4 + roadmap §0 correction.)

- [ ] **Step 1: Failing test** — the locked-decision correction is the headline assertion:

```python
import pytest
from glasshat.rubric.presets import load_preset, list_presets
from glasshat.rubric.canonical import compute_weights_vector

def test_four_presets():
    assert set(list_presets()) == {"qdrant","rapid-agent","cmux-aim","gemini3"}

def test_all_presets_load_and_validate():
    for pid in list_presets():
        load_preset(pid)  # must construct a valid SynthesizedRubric (raises if invalid)

def test_rapid_agent_is_equal_25_not_40_30_20_10():
    r = load_preset("rapid-agent")
    weights = {c.id: c.weight for c in r.criteria}
    assert weights == {"tech-implementation":0.25,"design":0.25,
                       "potential-impact":0.25,"quality-of-idea":0.25}
    assert compute_weights_vector(r) == [0.25,0.25,0.25,0.25]

def test_rapid_agent_tie_break_order():
    r = load_preset("rapid-agent")
    order = [tb.criterion_id for tb in sorted(r.tie_breakers, key=lambda t: t.order)]
    assert order == ["tech-implementation","design","potential-impact","quality-of-idea"]
```

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `presets.py` (`PRESETS_DIR = Path(__file__).parent/"presets"`, `list_presets()`, `load_preset(pid)` → read YAML `synthesized:` block → `SynthesizedRubric.model_validate`). Author the 4 YAMLs. `rapid-agent.yaml` criteria = tech-implementation, design, potential-impact, quality-of-idea, each `weight: 0.25`, `scale: 5`, full 5-level descriptors, `bmad_mapping` per spec, `aggregation: weighted_sum`, `final_scale: 0-100`, `tie_breakers` ordered Tech→Design→Impact→Idea, `confidence: 1.0`. `qdrant.yaml` per spec §4 example (3 axes equal 0.333, simple_average). `gemini3.yaml`/`cmux-aim.yaml` from spec §1 table (gemini3 = 4 axes; encode the official-rule weighting consistent with locked decision — gemini3 concluded event uses its own published weights as documented; mark `source_excerpt`).
- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(p1): rubric presets (rapid-agent corrected to 25/25/25/25)`.

---

## Task 9: `glasshat.rubric.validation` (§7 pipeline + custom YAML)

**Files:** Create `validation.py`, `packages/rubric/tests/test_validation.py`. (Source: spec §7.)

- [ ] **Step 1: Failing test:**

```python
from glasshat.rubric.validation import validate_rubric, validate_custom_yaml, RubricWarning

def test_source_clause_traceability_warns_when_excerpt_absent(make_rubric):
    r = make_rubric(source_excerpts={"a":"NOT IN SOURCE"})
    warns = validate_rubric(r, source_text="the official rules text")
    assert any("traceab" in w.message.lower() for w in warns)

def test_descriptor_coverage_clean_rubric_has_no_warnings(make_rubric):
    r = make_rubric()  # well-formed
    assert validate_rubric(r, source_text=None) == []

def test_validate_custom_yaml_roundtrip():
    yaml_str = open("packages/rubric/src/glasshat/rubric/presets/qdrant.yaml").read()
    # custom yaml path expects the SynthesizedRubric body
    import yaml as y
    body = y.safe_load(yaml_str)["synthesized"]
    r = validate_custom_yaml(body)
    assert r.scoring_rule.aggregation.value == "simple_average"

def test_validate_custom_yaml_rejects_garbage():
    import pytest
    from glasshat.shared.errors import RubricValidationError
    with pytest.raises(RubricValidationError):
        validate_custom_yaml({"not":"a rubric"})
```

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `validation.py`: `@dataclass RubricWarning(code, message)`. `validate_rubric(rubric, source_text=None) -> list[RubricWarning]` running spec §7 checks that aren't already enforced by the model: (2) source-clause traceability (when `source_text` given, each `source_excerpt` must appear verbatim — else warn), (3) weights consistency (warn if mismatch slipped through), (4) descriptor coverage (warn), (5) bmad coverage (warn). `validate_custom_yaml(body: dict) -> SynthesizedRubric` → `try: SynthesizedRubric.model_validate(body) except pydantic.ValidationError as e: raise RubricValidationError(str(e))`.
- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(p1): glasshat.rubric.validation pipeline + custom YAML`.

---

## Task 10: `synthesized.schema.json` generation + drift check

**Files:** Create `schema.py`, `synthesized.schema.json`, `packages/rubric/tests/test_schema_sync.py`, `scripts/gen_rubric_schema.py`.

- [ ] **Step 1: Failing test** `test_schema_sync.py`:

```python
import json
from pathlib import Path
from glasshat.rubric.schema import synthesized_schema

def test_disk_schema_matches_model():
    disk = json.loads(Path("packages/rubric/synthesized.schema.json").read_text())
    assert disk == synthesized_schema(), "Run scripts/gen_rubric_schema.py and commit"
```

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3: Implement** `schema.py`: `synthesized_schema() -> dict` returns `SynthesizedRubric.model_json_schema()`. `scripts/gen_rubric_schema.py` writes it to `packages/rubric/synthesized.schema.json` (pretty, sorted). Run the script to produce the file, commit it.
- [ ] **Step 4:** run → PASS.
- [ ] **Step 5: Commit** `feat(p1): generated synthesized.schema.json + drift guard`.

---

## Task 11: `.env.example` rewrite + CI workflow

**Files:** Modify `.env.example`; Create `.github/workflows/ci.yml`.

- [ ] **Step 1:** Rewrite `.env.example` per roadmap §0/§1: remove `QDRANT_*`; set `AGENT_RUNTIME=adk-local`; `MONITOR_BACKEND=phoenix-local` + `PHOENIX_API_KEY`/`PHOENIX_COLLECTOR_ENDPOINT`/`PHOENIX_PROJECT_NAME`; `LLM_BACKEND=mock`; `DOCSTORE_BACKEND=memory`; keep Gemini tiers + GCP identity; add comment "Gemini/Google only — no OpenAI/Anthropic".
- [ ] **Step 2: CI** `.github/workflows/ci.yml` — on push/PR: setup-python 3.12 + install `uv` (astral-sh/setup-uv) → `uv sync` → `uv run ruff check .` → `uv run ruff format --check .` → `uv run mypy packages` → `uv run pytest` (coverage gate `--cov-fail-under=90` already in pyproject).
- [ ] **Step 3:** Run the full suite locally: `uv run ruff check . && uv run mypy packages && uv run pytest` → all green, coverage ≥90%.
- [ ] **Step 4: Commit** `ci(p1): GitHub Actions lint+typecheck+test + .env.example Arize/Gemini-only`.

---

## Task 12: PR

- [ ] **Step 1:** Push `feat/arize-packages`. Confirm CI green on GitHub (`gh run watch` / `gh pr checks`).
- [ ] **Step 2:** Open PR with body summarizing scope + locked-decision corrections (rapid-agent 25/25/25/25, Qdrant removed from env). **No squash** on merge (preserve TDD commit ordering).
- [ ] **Step 3:** Surface evidence: `uv run pytest` summary + coverage %, `gh pr checks` green.

---

## Self-Review notes

- **Spec coverage:** rubric-synthesis-spec §3 (model)→T6, §4 (presets)→T8, §5 (BMAD)→T5/§prompt deferred to P3 agent, §7 (validation)→T9, §8 (weights_vector)→T7. Foundation/CI→T0/T11. ✓
- **Type consistency:** `compute_weights_vector`, `compute_schema_hash`, `load_preset`, `validate_custom_yaml`, `synthesized_schema` names used consistently across tasks. ✓
- **Deferred to later phases (not P1):** the RubricSynthesizer *agent/prompt* (P3), Vertex embedding-based anchor *retrieval* (P2 `retrieval`), Firestore persistence of `past_evals` (P2/P3). P1 is pure typed contracts + rubric logic, zero external deps.
