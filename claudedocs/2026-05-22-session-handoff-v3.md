# Glasshat — Session Handoff (2026-05-22, v3: production self-assessment → gemini-3.1 migration → live)

> Supersedes `claudedocs/2026-05-22-session-handoff-v2.md`. v2 = web rebuild + live Arize AX.
> v3 = production-grade self-assessment, two gap-closure PRs, and a redeploy onto
> **gemini-3.1-flash-lite**. Full self-assessment: `claudedocs/2026-05-22-production-self-assessment.md`.

## §0 두 줄 요약
- **비기술자 한 줄**: 제품을 "제출 가능한가?" 기준으로 항목별 자체평가했고, 두 개의 약점(에이전트별 추적 분리 누락 + 금지된 옛 모델 사용)을 각각 PR로 고쳐 라이브에 반영했다. 이제 라이브는 **최신 Gemini 3.1 Flash-Lite**로 실제 평가를 수행하고, 모든 화면이 Lighthouse 90점+이며, 평가 6단계가 Arize AX에서 역할별로 분리 추적된다.
- **다음 세션 1순위**: 제출 자산(데모 영상 스크립트 + Devpost 텍스트) 작성 — 이번 세션 범위 밖으로 의도적으로 미룸. D-day **2026-06-11 14:00 PT**.

## §1 이번 세션에 한 일 (시간순)
- **자체평가 Round 1**: 베이스라인 게이트 green 확인(py 152 / web 40), 6개 오케스트레이션 에이전트 코드 정독. 2개 FAIL 식별 — (b2) AX span이 6-hat에만 있음, (c2) 라이브가 금지 모델 `gemini-2.5-flash` 사용.
- **PR #27 (merged)** — `feat(llm): location-aware Vertex client + migrate to gemini-3.1-flash-lite`. 근본원인: `VertexLlmClient`가 모든 호출을 `google_cloud_region`(us-central1)로 보내고 per-tier `*_location`(이미 기본값 global)을 무시 → 3.x는 global 전용이라 regional 404 → 그래서 deploy.sh가 2.5로 핀했었음. 수정: 위치별 client 캐시(생성=global, 임베딩 text-embedding-005=regional) + deploy.sh를 `gemini-3.1-flash-lite`(GA)로. +5 단위테스트.
- **PR #28 (merged)** — `feat(obs): per-agent glasshat spans`. `run_evaluation`의 6단계 각각에 `glasshat.agent` span(RubricSynthesizer/BluePlanner/SixHatPanel/Audit/BMADScorer/ReportAssembler). recording-tracer 테스트 추가.
- **재배포** — `ARIZE_SPACE_ID=… bash infra/deploy.sh --confirm` 성공(real Vertex 3.1-flash-lite + Arize AX).
- **라이브 검증** — /health+3라우트 200, `POST /api/evaluate` 200 → RunRecord `2b2e29c2` final 56.93 + 4 self-correction, AX register 정상(export 에러 0), Lighthouse 라이브 3페이지 92/93/95 perf 전부 ≥90.

## §2 현재 상태
| 항목 | 상태 |
|---|---|
| Branch | `main` (clean) + 이 핸드오프용 `docs/session-3.1-migration-handoff` |
| 머지 PR (이번 세션) | **#27, #28** (feature→PR→main, merge commit, squash 0, CI green) |
| Live Web | https://glasshat-web-o366v7tl2q-uc.a.run.app (`/ /judge /participate` → 200) |
| Live API | https://glasshat-api-o366v7tl2q-uc.a.run.app (`/health` ok; `/api/evaluate` 실 Gemini 3.1) |
| 배포 모드 | real — Vertex **gemini-3.1-flash-lite**(flash+flash_lite), gemini-3.1-pro-preview(pro), 전부 **global** 엔드포인트 + Arize AX. Cloud Run min=0 |
| 관측 | Arize AX, `otlp.arize.com`, project `glasshat`, space `U3BhY2U6NDUxMzY6V012Yg==`; 6 에이전트 + 6-hat 각자 span |
| Lighthouse (라이브) | `/` 92/95/96 · `/judge` 93/96/96 · `/participate` 95/96/96 (Perf/A11y/BP) |
| 테스트 | py **157** + web **40** green; cov 97.85% (≥90) |
| 게이트 | ruff/format/mypy/pytest + eslint/tsc/vitest/build green; CI(lint·web·docker) green |
| 모델 정책 | **2.5 영구 금지**. 3.1-flash-lite 사용 중. 최악-케이스 폴백 = 3.1 접근 불가 입증 시 gemini-3.5-flash(현재 불필요) |
| Secret/IAM | `phoenix-api-key`(=AX 키) Secret Manager; SA에 aiplatform.user + secretmanager.secretAccessor |

## §3 다음 세션에서 할 수 있는 것
**즉시 (자격증명 불필요)**
- **제출 자산**: 데모 영상 스크립트(샷 리스트·나레이션) + Devpost 제출 텍스트(요약/기술/Arize·Gemini 사용처). ← **다음 1순위**.
- AX UI 육안 확인 가이드 작성(사용자가 app.arize.com 로그인해 project glasshat 트레이스 확인).
- 추가 정성 UX 점검 / 카피 다듬기.

**사용자 입력/승인 필요**
- 추가 라이브 재배포(코드 변경 시 자동) — 비용 무관 승인 받음.
- `.env` 생성/수정 — 명시적 승인.

## §4 할 수 없는 것 (외부)
- Devpost 제출(계정·폼)·데모 영상 녹화 — 사용자만.
- AX UI 트레이스 육안 확인 — 사용자 로그인 필요(코드측 export는 검증됨).

## §5 환경 주의 (재현된 함정)
- **venv extra 토글로 깨짐**: 증상 `No module named 'anyio.pytest_plugin'` → `rm -rf .venv && uv sync --frozen`. 이번 세션 첫 게이트에서 실제 발생, 위 명령으로 복구.
- **`.next` 깨짐 + macOS sync `* N.ext` 중복파일**: `find . -name '* [0-9].*' … -delete` + `rm -rf apps/web/.next` 후 재빌드.
- **active gcloud project = `ss-v2-prod`(prod)**: `deploy.sh`가 `--project=panelyst-hackathon` 하드스코프로 무시 — 직접 gcloud 시 항상 `--project` 명시.
- **commit hook**: factory-policy가 `<>`,`()`,`*` 포함 `-m`/heredoc을 "shell expansion"으로 차단 → 커밋 메시지/PR 본문은 **파일로 작성 후 `-F`/`--body-file`** 사용.
- **chrome-devtools MCP 프로파일 락**: 다른 Chrome 실행 중이면 충돌 → Lighthouse는 `npx lighthouse --chrome-flags="--user-data-dir=/tmp/lh-chrome-iso"` 격리 프로파일로 측정.

## §6 다음 세션 시작 프롬프트
```text
/handon
이전 세션 핸드오프: claudedocs/2026-05-22-session-handoff-v3.md

읽고 진행. 이번 1순위 = 제출 자산(데모 영상 스크립트 + Devpost 텍스트). 결정 필요시만 질문.
제약: AI=Gemini/Google 전용·2.5 영구 금지(3.1-flash-lite 유지)·Qdrant 미사용·ADK·관측=Arize AX·
프로덕션(ss-v2-prod)/8080 미관여·gcloud는 --project=panelyst-hackathon·Arize키 Secret Manager만·
.env 승인없이 수정금지·페이즈별 PR·squash 금지·시작 전 git pull.
D-day: 2026-06-11 14:00 PT.
```

## §7 핵심 자산 위치 (v2에서 변경분만)
| 자산 | 경로 / 비고 |
|---|---|
| LLM 위치-인지 client | `packages/shared/src/glasshat/shared/llm.py` — `_locations()`/`_client_for(location)` 캐시 |
| 모델 env (배포) | `infra/deploy.sh` `GEMINI_ENV` — 3.1-flash-lite/pro-preview, LOCATION=global |
| 에이전트별 span | `services/pipeline-orchestrator/src/glasshat/pipeline/engine.py` — `agent_*` span, `glasshat.agent` 속성 |
| 자체평가 리포트 | `claudedocs/2026-05-22-production-self-assessment.md` (Round 1 + Round 2) |
| (그 외 엔진/API/web/tracer 경로는 v2 §7과 동일) | |

## §8 알려진 issue / open question
- **AX 트레이스 육안 미확인** (코드측 export OK, 0 에러). 사용자 로그인 필요.
- **gemini-3.1-pro-preview**: 프리뷰 모델, URL 루브릭 합성 경로에서만 호출(프리셋 데모 경로는 LLM 없이 결정론적). 라이브 eval로는 미검증.
- **deps 보류 2건(v2)**: `@vitejs/plugin-react`@5, `starlette`@0.52 (상류 캡). 변동 없음.
- **min-instances=0 + 배치 span flush**: 인스턴스 스케일다운 전 OTLP 배치가 flush되는지 — 단기 데모엔 무해, register/0-에러 확인됨.
