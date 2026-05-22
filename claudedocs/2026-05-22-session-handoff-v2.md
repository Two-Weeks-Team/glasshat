# Glasshat — Session Handoff (2026-05-22, v2: web rebuild → live Arize AX)

> Supersedes `claudedocs/2026-05-22-session-handoff.md` (that one is the prior empty→live build; preserved in git `ba78bdf`).

## §0 두 줄 요약
- **비기술자 한 줄**: 라이브 사이트가 "텅 비어 보이고 동작 안 함" → 두 화면(`/judge`·`/participate`)을 실제 동작하는 제품으로 다시 짓고, 실제 Google Gemini로 라이브 배포했으며, 디자인을 끌어올리고(전 페이지 Lighthouse ≥90), 평가 과정을 Arize AX(관측 플랫폼)로 실시간 전송까지 연결했다.
- **다음 세션 1순위**: **프로덕션 등급 자체평가 → 갭 해소 → 제출 가능 상태**. `/goal`(cap 800) 그대로 시작(§6). 첫 작업은 오케스트레이션 에이전트별 역할 실효성 점검(이미 일부 확인 — §8).

## §1 진행한 작업 (시간순, 이번 세션)
- **Phase A — 진단**: 라이브 페이지가 ~227줄 껍데기(`/judge`=정적 플레이스홀더, `/participate`=하드코딩 버튼 1개)인데 엔진/API는 풍부함을 확인. 숨은 근본원인: `Dockerfile.web`가 `NEXT_PUBLIC_API_BASE`를 빌드타임에 안 넣어 라이브 클라이언트가 same-origin→모든 `/api` 404.
- **Phase B — 웹 재구축 (PR #15–#18)**: 타입드 API 계약·디자인 시스템·`GET /api/presets`(#15) → `/participate` 전체 흐름(#16) → `/judge` 배치·랭킹·tie-break·override·lock(#17) → 랜딩 + 빌드타임 API-base 수정 + 실-Vertex 배포 인에이블 + 검증(#18).
- **Phase C — /goal 실행 (G1/G2)**: G1 실 Arize Phoenix(self-host) e2e — 실 Vertex Gemini + 29 spans + 실 ADK→MCP(27 tools) + self-correct(#19). G2 실-Vertex 라이브 배포(`--no-phoenix`, 실 Gemini RunRecord). **키 정체 발견**: `ak-` 키는 Phoenix Cloud가 아니라 Arize AX 키.
- **Phase D — 디자인 상향 (PR #20–#23)**: D1 mesh-gradient 디자인 시스템·Reveal·hover-lift → D2 애니메이션 히어로 모티프·bento grid → D3 CountUp·reveals·elevate → D4 Lighthouse 감사(전 페이지 ≥90)+반응형.
- **Phase E — Arize AX 연결 (PR #24) + 재배포**: 사용자가 Space ID 제공(`U3BhY2U6NDUxMzY6V012Yg==`). 1급 `arize` 모니터 백엔드(`ArizeTracer`) 추가, `deploy.sh` real 모드를 AX로, 재배포 → **라이브 서비스가 AX project `glasshat`로 span 전송**(검증: 등록 로그 + export 에러 0 + 라이브 eval run 58f6892c final 64.6).
- **Phase F — deps 최신화 (PR #25) + 문서 (PR #26)**: 메이저까지 업그레이드(eslint10/TS6/vitest4/jsdom29/three0.184), Python `uv lock --upgrade`. README+검증문서 갱신.

## §2 현재 상태

| 항목 | 상태 |
|---|---|
| Branch | `main` (clean), open PR 0 |
| Repo | https://github.com/Two-Weeks-Team/glasshat |
| 머지 PR (이번 세션) | **#15–#26** (전부 feature 브랜치→PR→main, squash 0, CI green) |
| Live Web | https://glasshat-web-o366v7tl2q-uc.a.run.app (`/` `/judge` `/participate` → 200) |
| Live API | https://glasshat-api-o366v7tl2q-uc.a.run.app (`/health` ok; `/api/evaluate` 실 Gemini) |
| 배포 모드 | real (Vertex Gemini `gemini-2.5-flash` us-central1 + **Arize AX 트레이싱**), Cloud Run min=0 |
| 관측 | Arize AX, `otlp.arize.com`, project `glasshat`, space `app.2weeks` (Space ID `U3BhY2U6NDUxMzY6V012Yg==`) |
| Lighthouse | 랜딩 90/95/96(desktop)·95/95/96(mobile) · `/judge`·`/participate` 100/96/96 — Perf/A11y/BestPractices |
| 테스트 | py **158** + web **40** (`uv pytest` + `pnpm test` green) |
| 게이트 | uv ruff/mypy(34)/pytest + pnpm lint(eslint10)/typecheck(ts6)/test(vitest4)/build green; CI(lint·web·docker) green |
| Deps | 최신 메이저. 보류: `@vitejs/plugin-react`@5(6=vite8, vitest4=vite7), `starlette`@0.52(FastAPI `<1.0`) |
| 환경 | node v22.16.0 · pnpm 9.15.0 · uv 0.11.7 · Python 3.12(uv-managed) |
| Secret/IAM | `phoenix-api-key`(=AX 키) in Secret Manager; Cloud Run SA에 `aiplatform.user`+`secretmanager.secretAccessor` |

## §3 다음 세션에서 할 수 있는 것

**즉시 가능 (자격증명 불필요)**
- 프로덕션 등급 **자체평가 리포트** 작성(시각적 와우/오케스트레이션/I-O 흐름, PASS·FAIL+근거).
- 오케스트레이션 에이전트별 역할 실효성 코드 점검(synthesizer/planner/6-hat/audit/scorer/report).
- 갭 해소 PR(페이즈별), 게이트·CI green 유지.
- mock 백엔드로 로컬 e2e·브라우저 점검, Lighthouse 재측정.
- 종합 핸드오프 갱신 + memory 갱신.

**사용자 입력/승인 필요**
- 라이브 재배포(`ARIZE_SPACE_ID=… bash infra/deploy.sh --confirm`) — 과금, 승인.
- `.env` 생성/수정(필요 시) — 명시적 승인.
- 데모 영상/Devpost 제출 텍스트 — 사용자 콘텐츠.

## §4 할 수 없는 것 (외부 변수)
- 해커톤 제출 자체(Devpost 계정·폼) — 사용자만.
- Arize AX UI에서 트레이스 육안 확인 — 사용자 계정 로그인 필요(코드 측 export는 검증됨).
- gemini-3.x preview 모델 접근(현재 2.5 GA로 핀; 3.x는 global 엔드포인트 전용·접근 불확실).

## §5 추가로 필요한 것
- 재배포 시 `ARIZE_SPACE_ID` env 제공(또는 그대로 `U3BhY2U6NDUxMzY6V012Yg==` 사용 승인).
- 환경 점검: macOS sync가 `* N.ext` 중복 파일을 계속 생성 → 커밋 전 `find . -name '* [0-9].*' … -delete`. `.next`가 재빌드 누적으로 깨질 수 있음 → `rm -rf apps/web/.next` 후 재빌드.
- 로컬 실 e2e 시 venv가 extra 토글로 깨질 수 있음 → 증상 시 `rm -rf .venv && uv sync`.

## §6 다음 세션 시작 프롬프트
```text
/handon
이전 세션 핸드오프: claudedocs/2026-05-22-session-handoff-v2.md

읽고 아래 /goal로 바로 진행하세요(프로덕션 제출 가능 상태 + 핸드오프). 결정 필요시만 질문:
1. 자체평가에서 FAIL 나오는 갭은 이번 세션에서 닫을까, 다음으로 미룰까?
2. 재배포(ARIZE_SPACE_ID=U3BhY2U6NDUxMzY6V012Yg== bash infra/deploy.sh --confirm) 승인?
3. gemini-2.5 유지 vs 3.x preview 시도?
4. 데모영상/Devpost 텍스트도 만들까?

/goal Glasshat을 프로덕션 제출 가능 상태로 끌어올리고 다음 세션이 이어받을 완전한 핸드오프를 남긴다. 비주얼 컨셉부터 완성까지 한 단계씩 프로덕션 등급으로 자체평가하며 멈추지 말고 진행. [종료] 1.자체평가 리포트 surface(표,PASS/FAIL+근거): (a)시각적 와우 Lighthouse≥90 전페이지+정성 (b)오케스트레이션 RubricSynthesizer·BluePlanner·6-hat·Audit·BMADScorer·ReportAssembler 각 역할 증거(e2e 로그+AX span 분리) (c)인풋→아웃풋 흐름(plan gate→SSE→결과→3D, 라이브 200+실 Gemini RunRecord). 2.FAIL/갭은 페이즈별 PR 해소 또는 핸드오프 next-step 명시, 변경마다 게이트 green. 3.종합 핸드오프 + memory 갱신. 4.게이트: uv ruff/mypy/pytest+pnpm lint/typecheck/test/build green, Actions green, shipped grep "mock|stub|placeholder|TODO" =0(named mock 제외), 라이브 /health ok+3라우트 200. [검증]대화 출력만으로. [제약]AI=Gemini/Google전용·Qdrant미사용·ADK·관측=Arize AX·프로덕션(ss-v2-prod)/8080/타프로젝트 미관여(deploy.sh panelyst-hackathon hard-scope)·Arize키 Secret Manager만·.env 승인없이 수정금지·페이즈별 PR·squash/mega-PR금지·시작전 git pull·외부의존 막힐때만 보고. or stop after 800 turns.

D-day: 2026-06-11 14:00 PT (Rapid Agent / Arize 제출 마감)
```

## §7 핵심 자산 위치
| 자산 | 경로 |
|---|---|
| 엔진 stages | `agents/src/glasshat/agents/{rubric_synthesizer,blue_planner,hats,audit,bmad_scorer,report}.py` |
| 파이프라인 | `services/pipeline-orchestrator/src/glasshat/pipeline/{engine,events,adk_runtime}.py` |
| 관측(tracer) | `packages/shared/src/glasshat/shared/tracing.py` (NoOp/Phoenix/**Arize AX**) · config.py(`monitor_backend`, `arize_space_id`) |
| API | `apps/api/src/glasshat/api/app.py` (health·presets·plan·evaluate·stream·runs·override) |
| Web | `apps/web/app/{page,judge,participate}.tsx` · `components/*` · `lib/{api,stages,participate-state,ranking,projection}.ts` |
| 배포 | `infra/{deploy.sh,Dockerfile.api,Dockerfile.web,cloudbuild-*.yaml}` |
| 실 e2e | `scripts/{real_e2e.py(self-host Phoenix),real_phoenix_cloud_e2e.py,real_arize_ax_e2e.py}` |
| 검증 문서 | `claudedocs/2026-05-22-{web-rebuild,design-elevation}-verification.md` |
| 디자인 증거 | `claudedocs/assets/design-{landing,mobile,participate}.png`, `live-landing.png` |
| 계획 | `docs/superpowers/plans/2026-05-22-{web-rebuild,design-elevation}.md` |

## §8 알려진 issue / open question + 부분 평가 결과
- **부분 자체평가(오케스트레이션, 시작됨)**: 6-hat은 `HAT_PERSONAS`로 **진짜 서로 다른 관점**(white=facts, red=intuition, yellow=optimism, black=critic, green=alternatives, blue=synthesis) — 각자 evidence retrieve + persona 프롬프트 + `SCORE:` 추출. 스텁 아님. 다음 세션은 synthesizer/planner/audit/scorer/report의 역할 실효성도 동일하게 코드+e2e로 확인할 것.
- **mock vs real**: CI/로컬 기본은 named `mock`/`memory` 백엔드(스텁 아닌 결정론적 구현). 라이브는 real Vertex+AX. self-assessment 시 "mock" grep은 named 백엔드 제외.
- **gemini-2.5 핀**: config 기본값은 gemini-3.x preview지만 배포는 2.5로 핀(3.x는 regional 404). 3.x 시도하려면 global 엔드포인트 필요.
- **AX 트레이스 육안 확인 미완**: 코드측 export 검증됨(에러0), 사용자 AX UI 확인은 미수행.
- **deps 보류 2건**: `@vitejs/plugin-react`@5, `starlette`@0.52 (상류 캡 — §2).
- **워크스페이스 위생**: `* N.ext` 중복 파일·`.next` 깨짐·venv extra 토글 (§5 대응법).
