# Glasshat — Session Handoff (2026-06-06)

## §0 두 줄 요약
- **비기술자용:** glasshat의 평가 엔진을 **실제로 Google Agent Engine에 배포**해서 라이브로 동작시키고, **Arize AX에 풀 trace + hit@13 0.6154 실험**까지 올렸으며, 그 결과를 README·랜딩에 반영하고 제출 전 전수감사로 갭을 닫았다. 기술/문서는 제출 준비 완료.
- **다음 세션 1순위:** 남은 건 **인간 작업뿐** — ① 데모 영상 녹화·업로드 ② Devpost 폼 제출(+Arize 트랙 선택) ③ 거주지 자격 자가확인 ④ (선택) 프로드 보안 하드닝 재배포. 코딩 잔여 없음.

D-day: **2026-06-11 14:00 PT**

---

## §1 진행한 작업 (시간순)

### Phase A — 클라우드 /goal: 5개 티어 PR (#67–#71, 머지)
`claudedocs/2026-06-05-arize-cloud-completion-plan.md`를 `/goal`로 자율 실행:
- **#67 P0** GEAP 마이그레이션 — GA 모델명(`gemini-3.1-pro`/`gemini-3.5-flash`), `gemini-enterprise` 백엔드(alias `vertex` 유지). **핵심 결정:** cloud SDK(aiplatform/arize)는 google-adk<2 충돌로 uv.lock에서 제외 → `deploy/requirements-cloud.txt` ephemeral overlay. deploy closure byte-identical.
- **#68 P1** ADK 1.x Sequential/Parallel/Loop → **ADK 2.0 `Workflow(edges=…)` graph** (parity-gated, 6/6).
- **#69 P2** Agent Engine 배포 드라이버 + 배포 가능 agent 모듈.
- **#70 P3** Arize AX Datasets+Experiment+Evaluator hit@13 하니스.
- **#71 P4** A2A AgentCard + 서버 (stretch).

### Phase B — PART B 실제 클라우드 실행 (genuine deploy)
- `agent_engines.create`로 **실제 Agent Engine 리소스 배포 + 라이브 쿼리 성공**. 배포 중 5개 실버그 발견·수정: reserved env(`GOOGLE_CLOUD_PROJECT`), cloudpickle 누락, extra_packages=copy-not-install(→merged `glasshat/` source tree), tracer 이중등록(MONITOR_BACKEND=arize 제거), `Event.invocation_id` 필수.

### Phase C — 사용자가 ARIZE creds 제공 → 라이브 AX 완성 (#72–#75)
- creds를 프로드에서 추출(`~/.glasshat-arize.env`: SPACE=`U3BhY2U6NDUxMzY6V012Yg==`=Space:45136, key=Secret Manager `phoenix-api-key`).
- **AX 실험 라이브:** `glasshat-hit-at-13-gemini` (실제 Gemini **hit@13 0.6154**, 8/13 winner top-13; mock 0.3846/chance 0.26) + dataset `glasshat-golden` + injection code evaluator.
- **#72** AX 실험 idempotent+비용절반(라이브 검증) · **#73** google-genai instrumentor 추가 → **deep nested trace** · **#74** README+`AGENT_PLATFORM` 메타+finale · **#75** 전용 cinematic "Agent Platform proof" 밴드 (chrome-devtools 스크린샷 검증).
- 라이브 deep-trace 리소스 = **`reasoningEngines/7480191458771730432`** (이전 시도 리소스 삭제).

### Phase D — 제출 전 전수감사 (#76, 머지)
3 병렬 에이전트(규칙/Arize-docs · 코드/보안 · 웹/정직성) + 라이브 실측. **판정: 블로킹 없음, Arize 트랙 충족·초과.** 닫은 갭: evidence-doc 모순 재작성(+`ax-live-capture.json` 커밋), 죽은 `-preview` 모델→GA, 테스트수 224/71·243/73→실제 **323py/74web**, compliance-docs 배너, 보안 정직공개(데모=legacy/open), "503 anchors" 전수 scrub, ArizeBand 카피 scoping, `* 2.*` 정리.

---

## §2 현재 상태

| 항목 | 값 |
|---|---|
| Branch / HEAD | `main` @ **`9e3d4d3`** (origin과 동기, working tree clean) |
| Open PRs | **없음** (#67–#76 전부 머지) |
| Repo | https://github.com/Two-Weeks-Team/glasshat (Apache-2.0) |
| Live web | https://glasshat-web-o366v7tl2q-uc.a.run.app (`/judge` · `/participate`) |
| Live API | https://glasshat-api-o366v7tl2q-uc.a.run.app — `/health` → `{"status":"ok"}` ✅ |
| Agent Engine | `projects/916178791322/locations/us-central1/reasoningEngines/7480191458771730432` (serving) |
| Arize AX | project `glasshat`, Space:45136 — deep trace(72 GenerateContent+75 EmbedContent) + experiment `glasshat-hit-at-13-gemini` |
| Tests | py **323 passed** (3 deselected) · web **74 passed** · CI green |
| 기본값 | `mock`/`python`/`legacy`/`heuristic`/`code` (parity-preserved) |

**환경:** uv 0.11.7 · node v22.16 · pnpm 9.15 · 프로젝트는 uv-managed CPython 3.12 (시스템 python3은 3.14 — 직접 쓰지 말 것). `~/.glasshat-arize.env` **존재**(다음 세션 재사용 가능). ⚠️ **gcloud active project = `ss-v2-prod` (FOOTGUN)** — 모든 gcloud/배포에 `--project=panelyst-hackathon` + `GOOGLE_CLOUD_QUOTA_PROJECT=panelyst-hackathon` 명시.

---

## §3 다음 세션에서 할 수 있는 것

### 즉시 가능 (코드/검증, 자율)
- **재현 검증:** `source ~/.glasshat-arize.env` 후 `experiments/run_arize_experiment.py`(라이브 hit@13) 또는 `agent_engine_deploy.py`(재배포) — 둘 다 `uv run --with-requirements deploy/requirements-cloud.txt`.
- **라이브 AX 스팬 재확인:** `client.spans.list(project="glasshat")` (resp**.spans** 사용 — `list(resp)`는 tuple됨).
- (선택) `AgentPlatformProof` 카드 `<ul>/<li>` 시맨틱화(CodeRabbit LOW), `HANDOFF.md` 루트 모델문자열 갱신(L3), `data/devpost-gemini3/` 90MB blob LFS화(L1).

### 사용자 입력 필요
- 프로드 보안 하드닝 승인(아래 §4) · Devpost/영상 관련 결정.

---

## §4 할 수 없는 것 (외부 변수 / 인간 작업)
1. **데모 영상** 녹화 + YouTube/Vimeo 공개 (~3분, 영어/영어자막) — 팀원. 스크립트: `claudedocs/2026-06-02-demo-video-script.md`(현 shipped 상태에 맞춰 업데이트 권장).
2. **Devpost 폼 제출 + Arize 트랙 선택** — 인간만 가능.
3. **자격 자가확인** — 거주지 제외국(이탈리아·브라질·퀘벡·중국·러시아 등) + 팀 ≤4명.
4. **프로드 보안 하드닝 재배포** — `SCORING_MODE=structured` + `JUDGE_API_TOKEN`(Secret Manager). 코드/플래그는 ship됨; 프로드 재배포는 **유저 승인 필요**(프로드 보호 규칙). 현재 데모는 legacy(주입 가능)/judge endpoint 오픈이며 README가 정직히 공개.

---

## §5 추가로 필요한 것 (사용자 확인)
- **프로드 재배포 승인 여부** — `SCORING_MODE=structured` + `JUDGE_API_TOKEN` 플립(보안) 또는 `AGENT_RUNTIME=adk` 플립(B-FLIP). 둘 다 `infra/deploy.sh --confirm`, 유저-게이트.
- **Devpost 제출 텍스트** — `claudedocs/2026-06-02-devpost-text.md`는 stale(Agent-Engine/실험 누락). 제출 전 README "🛰️ Also deployed…" 기준으로 다시 쓸지 확인.
- ARIZE creds(`~/.glasshat-arize.env`) 유지/회전 여부.

---

## §6 다음 세션 시작 프롬프트

```text
/handon

이전 세션 핸드오프: claudedocs/2026-06-06-session-handoff.md

읽고 다음 결정 사항에 답한 뒤 진행하세요:
1. 프로드 보안 하드닝(SCORING_MODE=structured + JUDGE_API_TOKEN) 재배포를 지금 승인하나요? (유저-게이트 프로드 재배포)
2. Devpost 제출 텍스트(claudedocs/2026-06-02-devpost-text.md)를 현 shipped 상태로 다시 쓸까요?
3. 데모 영상 스크립트(claudedocs/2026-06-02-demo-video-script.md)를 Agent-Engine/AX 결과 반영해 갱신할까요?
4. 그 외 추가로 닫고 싶은 갭(LOW: ul/li 시맨틱, 90MB blob LFS, HANDOFF.md)이 있나요?

참고: ARIZE creds는 ~/.glasshat-arize.env 에 있음. gcloud active=ss-v2-prod 풋건 → 항상 --project=panelyst-hackathon.
D-day: 2026-06-11 14:00 PT
```

---

## §7 핵심 자산 위치 reference

| 자산 | 경로 |
|---|---|
| 클라우드 완성 계획(근본문서) | `claudedocs/2026-06-05-arize-cloud-completion-plan.md` |
| **라이브 AX 증거(머신리더블)** | `claudedocs/arize-evidence/ax-live-capture.json` + `2026-06-05-agent-engine-deploy-proof.md` |
| ADK 2.0 Workflow | `services/pipeline-orchestrator/src/glasshat/pipeline/adk_agents.py` |
| 배포 agent + tracing | `services/pipeline-orchestrator/src/glasshat/pipeline/agent_engine.py` |
| Agent Engine 배포 드라이버 | `deploy/agent_engine_deploy.py` (+ `deploy/requirements-cloud.txt`) |
| AX 실험 하니스 | `services/pipeline-orchestrator/src/glasshat/pipeline/arize_experiment.py` + `experiments/run_arize_experiment.py` |
| A2A | `services/pipeline-orchestrator/src/glasshat/pipeline/a2a.py` + `deploy/a2a_server.py` |
| 랜딩 proof 밴드 + 메타 | `apps/web/app/page.tsx` (`AgentPlatformProof`) + `apps/web/lib/deployment.ts` (`AGENT_PLATFORM`) |
| 컴플라이언스(판정) | `README.md` · `docs/rapid-agent-compliance.md` · `docs/evidence-matrix.md` |
| 프로드 배포 스크립트 | `infra/deploy.sh` (유저만 `--confirm`) |

---

## §8 알려진 issue / open question
- **OQ1 — 프로드 데모 보안:** 라이브 Cloud Run은 `SCORING_MODE=legacy`(deck의 `SCORE: 10` 주입으로 점수 조종 가능) + judge override/un-redacted 엔드포인트 오픈(`JUDGE_API_TOKEN` 미설정). 하드닝은 ship됐으나 프로드 플립은 유저-게이트. README가 정직 공개.
- **OQ2 — Agent Engine vs Cloud Run 런타임:** 라이브 Cloud Run은 python parity 경로(AGENT_RUNTIME 미설정→python). genuine ADK 2.0 Workflow는 **별도 Agent Engine** 배포(`7480…`). README Agent-runtime 행이 이를 명확화함.
- **OQ3 — gcloud 풋건:** active project `ss-v2-prod`. 한 번 `--project` 누락하면 프로드(8080 social-seeding) 위험. 매 명령 명시 필수.
- **OQ4 — Devpost/evidence 동기화:** `claudedocs/2026-06-02-devpost-text.md` + `demo-video-script.md`가 stale(이전 세션) — README가 authoritative. 제출 전 동기화 필요.
- **OQ5 — 90MB scraped corpus + spikes/ gitleaks ~253 hits** 공개 전 triage 미완(L1, 별도 메모리 `glasshat-spikes-secret-findings`).
- 비용: 이번 세션 실제 과금(Agent Engine 6회 배포 시도 + 실제 Gemini hit@13 2회 + 라이브 쿼리들) — 유저 승인됨. 실패 리소스 정리 완료, deep-trace 1개만 유지.
