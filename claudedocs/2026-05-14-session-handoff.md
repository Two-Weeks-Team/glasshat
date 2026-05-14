# Panelyst — Session Handoff (2026-05-14)

> 새 세션은 `cd ~/Documents/GitHub/panelyst && /handon`으로 이어가세요. 이 파일이 `/handon` 자동 로드 대상입니다 (글로벌 `~/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/MEMORY.md`도 함께 자동 로드됨 — 4 해커톤 컨텍스트 + 사용자 선호 + GCP 셋업 + Gemini 패널 결과 등 영구 기억).

---

## §0 — 두 줄 요약

**Panelyst** = artifact-ingesting 공정 평가 에이전트 (PDF 덱 + 코드베이스 → 6 Thinking Hats → BMAD 100점 evidence-grounded + precedent-anchored → 3D 그래프 + 라이브 공정 모니터). 단일 코드로 **Qdrant VSD (6/1 PT)** + **Rapid Agent (6/12)** 양쪽 제출. non-chatbot. Gemini(Vertex 3-tier) + Agent Builder + **Arize**(파트너 MCP=모니터) + **Qdrant**(벡터 메모리). **현재 상태: scaffold + 아키텍처 + GCP·Gemini 검증 완료, 구현은 아직 시작 안 함.**

---

## §1 — 현재 위치 / git 상태

- 작업 폴더: `~/Documents/GitHub/panelyst/`
- 원격: `https://github.com/Two-Weeks-Team/panelyst` (public · Apache-2.0)
- 브랜치: `main` (HEAD = `8462215`, origin과 동기)
- 4 commits 모두 푸시됨: scaffold(`bdae2af`) → architecture(`c122c30`) → GCP+Gemini(`34ffb0b`) → HANDOFF+PLAN(`8462215`)
- 첫 커밋 2026-05-13 — Qdrant "no previous projects" 룰 컴플라이언트

## §2 — 이번까지 완료된 것

| Phase 0 (Pre-flight) | 상태 | 산출물 |
|---|:--:|---|
| Repo scaffold | ✅ | `panelyst/` monorepo 골격 (apps/web, apps/api, services/{ingest,code-grader,pipeline-orchestrator}, agents, packages/{rubric,shared}, infra, scripts, docs) |
| 권위 아키텍처 문서 | ✅ | `docs/architecture.md` — 토폴로지 텍스트 다이어그램 + 에이전트 그래프 mermaid + 시퀀스 mermaid + Phase 1-5 배포 매트릭스 + 인터페이스 추상화 + 2 휴먼 게이트 + non-chatbot/agent rationale |
| 전체 plan | ✅ | `PLAN.md` (엄브렐라 mirror — 6-전문가-팀 분석 + 듀얼 제출 전략 + 페이즈 + 리스크 + open items + next work) |
| 핸드오프 | ✅ | `HANDOFF.md` (이 세션 마무리 직전 상태) |
| GCP 풀 셋업 | ✅ | project `panelyst-hackathon` (916178791322), 결제 크레딧계정(`01B677-A6E5C9-B265AF`), 13 APIs, SA `panelyst-dev@…`, 8 역할, 키 `~/.config/gcloud/panelyst-dev-sa-key.json` (mode 600, repo 외부) — `docs/gcp-setup.md` |
| Vertex Gemini 3-tier 라이브 검증 | ✅ | `gemini-3.1-pro-preview` (global, p50 9.3s eval-JSON) · `gemini-3-flash-preview` (global, p50 4.0s) · `gemini-3.1-flash-lite` GA (global, p50 1.3s) + 2.5 패밀리 폴백 (us-central1) — 6모델 × 7 location 매트릭스 측정 |
| `.env` (gitignored) | ✅ | 실값 채워짐 — 3-tier 모델 + global/regional 분리 + 폴백 + 토큰 예산 + Phase 1-5 abstraction switches |
| `.env.example` | ✅ | 검증된 템플릿 |
| 영구 기억 13개 | ✅ | `~/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/` (MEMORY.md 인덱스 + project/reference/feedback 분류) |

**아직 안 한 것: 코드 한 줄도 작성 안 함** (Phase 1 시작 전).

## §3 — 재현 명령 / smoke-test

```bash
cd ~/Documents/GitHub/panelyst

# 1) GCP 환경 OK 한지 헬스체크 (docs/gcp-setup.md §9에서 발췌)
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/panelyst-dev-sa-key.json
export GOOGLE_CLOUD_PROJECT=panelyst-hackathon
python3 - <<'PY'
from google.oauth2 import service_account
import google.auth.transport.requests, requests, os, time
creds = service_account.Credentials.from_service_account_file(
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
  scopes=["https://www.googleapis.com/auth/cloud-platform"])
creds.refresh(google.auth.transport.requests.Request())
for tier, (model, loc) in {
  "PRO":        ("gemini-3.1-pro-preview", "global"),
  "FLASH":      ("gemini-3-flash-preview",  "global"),
  "FLASH_LITE": ("gemini-3.1-flash-lite",   "global"),
}.items():
  host = "aiplatform.googleapis.com" if loc=="global" else f"{loc}-aiplatform.googleapis.com"
  url = f"https://{host}/v1/projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/locations/{loc}/publishers/google/models/{model}:generateContent"
  body = {"contents":[{"role":"user","parts":[{"text":"Reply OK"}]}],"generationConfig":{"maxOutputTokens":200,"temperature":0}}
  t0=time.perf_counter()
  r = requests.post(url, headers={"Authorization":f"Bearer {creds.token}","Content-Type":"application/json"}, json=body, timeout=60)
  dt=(time.perf_counter()-t0)*1000
  txt = r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","") if r.status_code==200 else r.text[:100]
  print(f"{tier:11s} {model:30s} {loc:8s} {dt:6.0f}ms HTTP {r.status_code} → {txt.strip()[:30]!r}")
PY
# → 세 모델 모두 HTTP 200 + 'OK' 응답이어야 함

# 2) 현 git 상태
git log --oneline -5
```

## §4 — 다음 작업 (Phase 1 — 로컬 E2E, 5/14 → 5/24, 10일)

**목적**: 클라우드 없이도 전체 루프 작동 + 인터페이스 추상화로 Phase 2-5 시 환경변수만 스위치.

| # | 태스크 | 산출물 | 의존 |
|---|---|---|---|
| 1.1 | Python 프로젝트 셋업 | `pyproject.toml`, ruff/mypy/pytest, `services/` 패키지 구조 | — |
| 1.2 | **LLM 어댑터** | `services/shared/llm.py`: Vertex global/regional 라우팅 + 3-tier + 폴백 + 토큰 예산 + Phoenix span 자동 래핑 | 0.4 |
| 1.3 | **Qdrant 6 컬렉션 + docker-compose** | `infra/docker-compose.local.yml` + `services/shared/qdrant.py` + 스키마 YAML | — |
| 1.4 | Phoenix 통합 | `services/shared/tracer.py` (OTel SDK → Phoenix in-process), 모든 hat/tool/score에 span | 1.2 |
| 1.5 | PDF ingest 경로 | `services/ingest/` (FastAPI): 업로드 → Gemini multimodal 파싱 → chunk → Qdrant `pitch_chunks` | 1.2, 1.3 |
| 1.6 | Code Grader Job | `services/code-grader/`: clone → static heuristics(15-20) → README → sample → Qdrant `repo_chunks` + facts → SQLite | 1.2, 1.3 |
| 1.7 | BMAD rubric + 75-technique registry | `packages/rubric/bmad-rubric.yaml` (17항목 100점) + `techniques.yaml` (≥20 활성) | — |
| 1.8 | 6 Hats system prompts | `agents/{white,red,yellow,black,green,blue}/prompt.md` + retrieval scope | 1.7 |
| 1.9 | Pipeline orchestrator (LangGraph) | `services/pipeline-orchestrator/`: BLUE planner → 5 hats parallel → BLUE synthesis → BMAD scorer (rubric-aware RAG) → evidence grounding → immutable run record | 1.2-1.8 |
| 1.10 | Next.js 프론트 스캐폴드 | `apps/web/`: 2 drop zones + plan card + monitor + report + 2D radar + vector-search + i18n KO/EN + SSE | 1.9 |
| 1.11 | `make demo` / `make doctor` | 결정론적 샘플 end-to-end + 헬스체크 | 1.9, 1.10 |
| 1.12 | `past_evals` 시드 (50–150 공개 Devpost) | Qdrant 채움 | 1.9, 1.11 |

**Phase 1 완료 기준**: 클린 머신에서 `cp .env.example .env && docker compose up && make demo` → 90초 내 점수 리포트 + 3D 그래프 + 모니터 트레이스.

**그 다음**: Phase 2 (GCP 점진 확장 — Cloud Run·Firestore·Eventarc·GCS, 5/25-28) → Phase 3 (Agent Builder wrap, 5/29-31) → **Phase Q (Qdrant 제출 6/1)** → Phase 4 (Qdrant Cloud 6/2-4) → Phase 5 (Arize hosted + Rapid Agent 다듬기 6/5-10) → **Phase R (Rapid Agent 제출 6/11-12)**. 상세: `PLAN.md` §6-§9, 영구 기억 `panelyst-project`.

## §5 — 제약 / 리스크

- **시간**: 사용자 "시간 제약 무시" 지시했지만 캘린더는 못 무시 — Qdrant 6/1이 가장 빠름, Qdrant-first 빌드.
- **Non-chatbot 룰** (Qdrant 하드 제약): 챗박스 절대 안 만듦. UI는 드롭존 + 플랜 카드 + 모니터 + 리포트 + 검색 페이지.
- **"All code in period" 룰**: 새 repo·새 코드만, fairthon 코드 재사용 금지. 컨셉 계보는 README에 공개 (이미 명시).
- **Gemini 3 family `global` 엔드포인트 전용**: regional 404. LLM 어댑터(1.2)가 자동 라우팅하도록 설계.
- **Gemini 3.1 Pro preview = API 변경 가능성**: 폴백 `gemini-2.5-pro` 준비됨 — 어댑터에서 자동 폴백.
- **Rapid Agent 공식 룰 미게시**: 게시 즉시 재검증. 현재 가정 기반 빌드.
- **프로덕션 안전선**: port 8080 절대 안 건드림, 합성 데이터만, `.env` 명시 인가 없이 수정 금지.

## §6 — Resume 프롬프트 (복사용)

> 작업 폴더: `~/Documents/GitHub/panelyst/`. `/handon` 으로 이 파일 자동 로드됨. GCP 셋업 + Gemini 3-tier 검증 완료 (`docs/gcp-setup.md`). **Phase 1 (로컬 E2E)** 시작 안 함. 다음으로 §4 표 중 무엇부터 진행할지: ⓐ 1.1 Python 프로젝트 셋업 + 1.2 LLM 어댑터 (Vertex global/regional 라우팅 + 3-tier + 폴백) ⓑ 1.3 Qdrant docker-compose + 6 컬렉션 스키마 ⓒ 1.7+1.8 BMAD rubric + 75-technique + 6 Hats prompts (콘텐츠 작업, 코드 의존 없음) ⓓ 1.10 Next.js 프론트 스캐폴드 (앞단 빠르게 보이게). **하드 룰**: non-chatbot · 모든 코드 fresh (no fairthon reuse) · Vertex(`global` for Gemini 3) via SA key · Arize는 Rapid Agent 파트너 · Qdrant load-bearing. Qdrant-first build (6/1).

---

## §7 — 이번 세션에서 추가된 것들 (5/14)

- `docs/architecture.md` 신규 (commit `c122c30`)
- GCP 프로젝트 + SA + 13 APIs (commit `34ffb0b`)
- Gemini 6모델 × 7 location 라이브 측정 + 5 gotchas 문서화 (`docs/gcp-setup.md`, commit `34ffb0b`)
- `.env` 실값 + `.env.example` 갱신 (commit `34ffb0b`)
- `HANDOFF.md` + `PLAN.md` 복원 (commit `8462215`)
- 영구 기억 14 파일 (MEMORY.md 인덱스 + 13 entries) at `~/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/`
- 엄브렐라 HTML 보고서 `2026-05-14-hackathon-pipeline-plan.html` (claudedocs/reports/)

작성: 2026-05-14 KST · 다음 세션은 이 폴더에서 `/handon` 으로 즉시 이어집니다.
