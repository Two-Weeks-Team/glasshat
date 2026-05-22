# Glasshat / Panelyst — Session Handoff (2026-05-22)

> **이 문서가 최신 권위 핸드오프입니다.** `2026-05-21-session-handoff.md`는 *빌드 시작 전* 계획/잠긴-결정 문서였고, 본 문서는 그 계획을 **전부 구현·배포 완료**한 결과입니다. 잠긴 결정(§2 of 2026-05-21)은 여전히 유효하며 모두 코드에 반영됨.
>
> ⚠️ 머신 간 주의: Claude Code 영구 메모리는 이 컴퓨터에만 있음(git 미전송). 다른 컴퓨터는 본 문서 + git 히스토리(PR #7–#14)를 권위 소스로.

---

## §0 — 두 줄 요약

빈 scaffold였던 Glasshat을 **8개 페이즈 PR(#7–#14)로 SDD+TDD 빌드**하여 **Cloud Run에 라이브 배포 완료** — 엔진(ADK 6-hat + 인코드 하이브리드 검색 + 캘리브레이션 self-correct) → FastAPI → Next.js 3D 뷰포트까지 동작. 실 Vertex Gemini + Phoenix + MCP e2e 입증, 150 테스트 green, 97.67% 커버리지.

**다음 세션 1순위**: (제품은 완성됨) → 해커톤 제출 준비(데모영상·Devpost 텍스트) **또는** 잔여 리파인먼트 1건(Phoenix-MCP 질의 기반 캘리브레이션 델타)을 결정.

---

## §1 — 진행한 작업 (시간순, 이번 세션)

| Phase | PR | 내용 |
|---|---|---|
| 계획 | — | 2026-05-21 핸드오프 로드 → `/goal` 조건(SDD+TDD+페이즈PR+무제한턴캡) 확정 → reconciled roadmap(`docs/superpowers/plans/`) |
| P1 | #7 | uv 워크스페이스 + CI + `glasshat.shared`(config/ids/enums/errors/protocols) + `glasshat.rubric`(SynthesizedRubric, JSON Schema, **rapid-agent 25/25/25/25 정정**, presets, validation) |
| P2 | #8 | `glasshat.shared.{llm,retrieval,tracing,docstore,blobstore}` — **Qdrant 대체 인코드 하이브리드**(cosine+BM25+RRF) + mock/Vertex LLM + NoOp/Phoenix tracer + memory/sqlite/firestore + local-fs/gcs |
| P3a | #9 | `glasshat.agents`(types·rubric_synthesizer·blue_planner·hats·audit·bmad_scorer·report) + `glasshat.ingest` + `glasshat.code_grader` |
| P3b | #10 | `glasshat.pipeline`(events·engine `run_evaluation` end-to-end+SSE+persist · adk_runtime: ADK instrument + Phoenix-MCP consultant) |
| P4a | #11 | `glasshat.api`(FastAPI: /health·/api/plan(gate1)·/api/evaluate·/api/evaluate/stream(SSE)·/api/runs/{id}·/override(gate2)) |
| P4b | #12 | `glasshat-web`(Next.js 16: landing·/judge·/participate·3D constellation r3f·SSE·typed client) + web CI job |
| P5a | #13 | infra(Dockerfile.api/web·compose·cloudbuild·deploy.sh hard-scoped) + CI docker-build + README Arize 단독 재서술 |
| P5b | #14 | 실 Vertex+Phoenix+MCP e2e(`scripts/real_e2e.py`) + **Cloud Run 라이브 배포** + 3D self-correction 스크린샷 + API CORS |

모든 PR: 독립 feature 브랜치 → merge commit(squash 금지) → 머지 전 CI green. TDD: 매 커밋 test→impl 순서.

---

## §2 — 현재 상태

**Git**: branch `main`, working tree clean. PR #7–#14 전부 MERGED. Open PR 없음. Remote `https://github.com/Two-Weeks-Team/glasshat`.

**Live (Cloud Run · project `panelyst-hackathon` · us-central1 · min-instances=0)**:
- Web: https://glasshat-web-o366v7tl2q-uc.a.run.app (`/` `/judge` `/participate` → 200)
- API: https://glasshat-api-o366v7tl2q-uc.a.run.app (`/health` → 200, `/api/evaluate` → self-corrected RunRecord)

**메트릭**: 150 tests passed (3 integration deselected) · **97.67% coverage** · ruff+ruff-format+mypy(strict) clean · main CI green(python·web·docker 3 jobs).

**실 e2e 입증(item 4)**: `scripts/real_e2e.py` — 실 Vertex Gemini(gemini-2.5-flash) + Vertex 임베딩(text-embedding-005) + 인코드 하이브리드 + self-host Phoenix(80 spans) + 실 Phoenix MCP stdio(27 tools, ADK agent의 list-projects 호출) → RubricSynthesizer(25/25/25/25)→6-hat→audit self-correct(8.0→7.04 등)→final 54.04. 증거: `claudedocs/2026-05-21-real-e2e-evidence.md`.

**환경**: node v22.16.0 · pnpm 9.15.0 · uv 0.11.7 · GCP ADC 존재(app.2weeks@gmail.com) · billing 크레딧계정 `01B677-A6E5C9-B265AF` 연결 · ⚠️ **활성 gcloud project = `ss-v2-prod`(프로덕션!)** — 배포 시 항상 `--project=panelyst-hackathon` 명시(deploy.sh가 자동으로 그렇게 함). Docker daemon DOWN(이미지 빌드는 CI/Cloud Build에서).

---

## §3 — 다음 세션에서 할 수 있는 것

**즉시 가능 (크레덴셜/외부 불필요)**:
1. **잔여 리파인먼트 — Phoenix-MCP 질의 기반 self-correct**: 현재 audit 델타는 인코드 캘리브레이션 테이블(deterministic spike-D)에서 옴. Phoenix에 캘리브레이션 데이터셋을 시드한 뒤 `PhoenixMcpConsultant`가 `get-dataset-examples`로 델타를 질의해 보정하도록 전환(`adk_runtime.py` + `audit.py`). 페이즈 PR로.
2. **재배포(데모 image)**: `bash infra/deploy.sh --confirm` (mock 백엔드, 안정·무과금-per-req).
3. **로컬 실 e2e 재현**: `scripts/real_e2e.py`(헤비 SDK 설치 + OTEL_SDK_DISABLED 없이 로컬 Phoenix면 OK; 설치는 §7 참조).
4. **테스트/커버리지 상향**, dual-rubric variance UI 시연 강화(`/participate`에 두 번째 rubric 비교 패널).

**사용자 입력/승인 필요**:
1. **해커톤 제출**: ≤3분 데모영상(현 `/goal`에서 제외됨) + Devpost 텍스트 설명 + public repo OSI 라이선스(Apache-2.0 이미 있음). 마감 2026-06-11 14:00 PT.
2. **배포 서비스에 실 Vertex/Phoenix 적용**: API Docker image에 `vertex`/`phoenix` extra 포함해 재빌드 + `PHOENIX_API_KEY` 제공(아래 §5).

---

## §4 — 할 수 없는 것 (외부 변수)

- **데모영상 녹화** — `/goal`에서 명시 제외. 사용자/팀이 직접.
- **Devpost 제출** — 사용자 계정·폼 필요.
- **배포 서비스의 cloud Phoenix 트레이스** — `PHOENIX_API_KEY` 미보유. 로컬 e2e는 self-host로 입증했으나, Cloud Run 서비스가 진짜 Phoenix Cloud로 트레이스 보내려면 키 필요(없으면 NoOp degrade).
- **gemini-3-preview 모델** — `global` 엔드포인트 필요. 현 `VertexLlmClient`는 `google_cloud_region` 사용 → e2e는 gemini-2.5 계열(us-central1)로 검증. 3.x 쓰려면 per-tier location 분기 추가 필요.

---

## §5 — 추가로 필요한 것

- **`PHOENIX_API_KEY` (+ collector endpoint)** — 배포 서비스 실 Phoenix용. `.env`(gitignore, 미생성) 또는 Secret Manager. **`.env` 수정은 사용자 명시 승인 필요**(이번 세션은 inline env만 사용, `.env` 미생성).
- **비용 모니터링** — Cloud Run(min=0이라 idle 0원) + Cloud Build + Vertex 호출. 크레딧계정 사용 중.
- **gcloud 활성 project 주의** — `ss-v2-prod`(프로덕션). 모든 배포 명령은 `--project=panelyst-hackathon` 명시(deploy.sh 강제). 전역 config 변경 금지.

---

## §6 — 다음 세션 시작 프롬프트

```text
/handon

이전 세션 핸드오프: claudedocs/2026-05-22-session-handoff.md

제품은 P1–P5b 빌드·배포 완료(PR #7–#14 머지, Cloud Run 라이브). 읽고 다음 결정에 답한 뒤 진행:
1. 다음 목표 = (a) 해커톤 제출 준비(데모영상 가이드·Devpost 텍스트) / (b) 잔여 리파인먼트(Phoenix-MCP 질의 기반 캘리브레이션 델타) / (c) 둘 다
2. 배포 서비스에 실 Vertex/Phoenix 적용할까? (그렇다면 PHOENIX_API_KEY 제공 + .env 생성 승인)
3. dual-rubric variance 비교 UI를 /participate에 강화할까?
4. 재배포 필요 시 infra/deploy.sh --confirm 실행 승인

D-day: 2026-06-11 14:00 PT (Rapid Agent / Arize 제출 마감)
제약: AI=Gemini/Google 전용 · Qdrant 미사용 · 오케스트레이터=ADK · 프로덕션(ss-v2-prod)·.env 미관여 · feature 브랜치+squash 금지 · 시작 전 git pull
```

---

## §7 — 핵심 자산 위치 reference

| 자산 | 경로 |
|---|---|
| 빌드 계획(페이즈별) | `docs/superpowers/plans/2026-05-21-*.md` (roadmap·phase1·phase2·phase3·phase4) |
| reconciled spec(잠긴결정 반영) | `docs/superpowers/plans/2026-05-21-glasshat-roadmap.md` |
| 실 e2e 스크립트 | `scripts/real_e2e.py` (env: GOOGLE_CLOUD_PROJECT=panelyst-hackathon, GOOGLE_GENAI_USE_VERTEXAI=true, GOOGLE_CLOUD_REGION=us-central1, GLASSHAT_GEMINI_FLASH=gemini-2.5-flash, PYTHONPATH=모든 src) |
| 실 e2e 증거 | `claudedocs/2026-05-21-real-e2e-evidence.md` |
| 3D self-correction 스크린샷 | `claudedocs/assets/glasshat-3d-self-correction.png` |
| 엔진 스테이지 | `agents/src/glasshat/agents/{types,rubric_synthesizer,blue_planner,hats,audit,bmad_scorer,report}.py` |
| 오케스트레이터 | `services/pipeline-orchestrator/src/glasshat/pipeline/{engine,events,adk_runtime}.py` |
| 인코드 하이브리드 검색 | `packages/shared/src/glasshat/shared/retrieval.py` |
| LLM 어댑터(mock/Vertex) | `packages/shared/src/glasshat/shared/llm.py` |
| API | `apps/api/src/glasshat/api/app.py` |
| 웹 | `apps/web/{app,components,lib}/` |
| 배포 | `infra/{Dockerfile.api,Dockerfile.web,docker-compose.yml,deploy.sh,cloudbuild-*.yaml}` |
| 로컬 SDK 설치(실 e2e용) | `uv pip install google-genai google-adk arize-phoenix arize-phoenix-otel openinference-instrumentation-google-adk openinference-instrumentation-google-genai mcp` |

빌드/검증 명령: `uv sync` → `uv run pytest --cov=glasshat` → `uv run ruff check . && uv run ruff format --check . && uv run mypy packages agents services apps/api`. 웹: `cd apps/web && pnpm install && pnpm build`.

---

## §8 — 알려진 issue / open question

1. **Phoenix-MCP self-correct 보정값 출처**: 실 e2e에서 MCP 왕복·self-correct 둘 다 실제이나, 보정 *값*은 인코드 캘리브레이션 테이블에서 옴(MCP 질의 델타 아님). 완전 충실하려면 Phoenix 데이터셋 시드 + `PhoenixMcpConsultant`가 질의해 델타 산출. (§3-즉시1)
2. **배포 image = mock 백엔드**: 런타임 image(`uv sync --no-dev`)에 vertex/phoenix extra 미포함 → 배포 API는 mock(안정·무과금). 실 Vertex 배포는 image에 extra 포함 재빌드 필요.
3. **gemini-3 preview**: `global` 엔드포인트 필요 → `VertexLlmClient`가 per-tier location 무시(google_cloud_region 사용). 현재 2.5 계열로 검증.
4. **로컬 PhoenixTracer 행(hang)**: arize-phoenix 설치+collector 없을 때 SimpleSpanProcessor 동기 export 재시도로 파이프라인 지연. 로컬 데모는 `OTEL_SDK_DISABLED=true`. 배포 image는 phoenix 미설치 → NoOp → 무영향.
5. **활성 gcloud project = ss-v2-prod(프로덕션)**: 배포 명령 항상 `--project=panelyst-hackathon` 명시. deploy.sh가 강제하고 활성 config 무시.
6. **CodeRabbit**: PR마다 advisory 리뷰(merge gate 아님). 일부 PR은 CodeRabbit pending 중 머지(CI green 기준).

---

작성: 2026-05-22 · 다음 세션: `cd ~/Documents/GitHub/glasshat && git pull && /handon`
