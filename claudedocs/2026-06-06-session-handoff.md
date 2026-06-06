# Glasshat — Session Handoff (2026-06-06, V2)

## §0 두 줄 요약
- **비기술자용:** 이전 세션의 라이브 Agent Engine + Arize AX 배포 위에, 이번 세션은 **Phoenix MCP 보정 루프를 GCP에 실제로 세워(Cloud SQL + Cloud Run) 라이브로 동작**시키고, 랜딩·덱·README·컴플라이언스를 전부 그 실상태로 정직하게 맞춘 뒤, **3분짜리 시연 영상까지 ffmpeg로 완성(V2)**했다. 코드·문서·영상 모두 제출 준비 완료.
- **다음 세션 1순위:** 남은 건 **사람 손이 필요한 행정뿐** — ① `glasshat-final-v2.mp4`를 YouTube/Vimeo 공개 업로드 ② Devpost 폼 제출(+Arize 트랙 선택) ③ 거주지/팀 자격 자가확인. (선택) 프로드 보안 하드닝 재배포는 유저-게이트. **코딩·영상 제작 잔여 없음.**

D-day: **2026-06-11 14:00 PT**

---

## §1 진행한 작업 (시간순)

### Phase A–D — (이전 세션, HEAD `9e3d4d3`) 클라우드 /goal + 라이브 AX
- **#67–#71** GEAP 마이그레이션·ADK 2.0 Workflow·Agent Engine 배포·AX Datasets+Experiment·A2A.
- **PART B** `agent_engines.create`로 **실제 Agent Engine 배포 + 라이브 쿼리** (실버그 5개 수정).
- **#72–#75** 사용자 ARIZE creds → **라이브 AX 실험 `glasshat-hit-at-13-gemini` (실제 Gemini hit@13 0.6154)** + deep nested trace + 랜딩 proof 밴드.
- **#76** 제출 전 전수감사 (블로킹 없음). 라이브 deep-trace 리소스 `reasoningEngines/7480191458771730432`.
- (상세는 git 히스토리 + 이 파일 이전 리비전 참고.)

### Phase E — (이번 세션, HEAD `aa60bf9`) Phoenix-MCP 실배포 · 정직성 · 시연영상

**E1. "Why now" 내러티브 (#81, #82)** — vibe-coding 범람(AI가 제출물은 폭증시켰지만 심사는 그대로)을 덱 F1 + 랜딩 + README + Devpost에 2-actor 프레이밍으로.

**E2. Phoenix MCP를 GCP에 실제로 배포 (#83–#85)** — 이전엔 `PHOENIX_COLLECTOR_ENDPOINT` 미설정→정직 fallback(table prior)였음. 이번에:
- **`glasshat-phoenix` Cloud Run + Cloud SQL(Postgres, ENTERPRISE edition)** 신설, SA에 `roles/cloudsql.client`, unix socket 연결.
- `scripts/seed_phoenix_calibration.py`로 **`glasshat-calibration` 데이터셋 시드**(13 preset criteria × 3 bucket, spike-D mean_delta 미러, httpx REST idempotent).
- **잠복버그 3개 수정**(adk_runtime.py): `consult` p25/p75 = 0.0/10.0 고정(잘못된 `_percentile` 제거), MCP arg `dataset`→`dataset_name`, `_parse_examples`가 `{"data":{"examples":[]}}` 언랩. + npx OOM → **API 메모리 2Gi(#84)** + Dockerfile **phoenix-mcp 사전설치(#85)**.
- 칩 `wired`→**`live`** 플립(ProofStrip/Timeline/Receipt/ArizeBand). **프로드 재배포(유저 승인)** → 라이브 MCP read+write 루프 검증(eval 8.0→6.87, "Phoenix MCP Server running on stdio"×2/eval, cell n 7→8).

**E3. 문서 완성 (#86–#88)** — 컴플라이언스·evidence·랜딩·덱 스펙·README의 stale spike-D 프레이밍을 **라이브 Phoenix-MCP**로 전수 교체, 불일치/파이프이스케이프 수정.

**E4. 덱 재타이밍 + 정직 F10 (#89–#91)** — 덱을 녹음 내러티브 비트에 맞춤(#89). **F10을 "recalibration, not a fake flip"으로 정직화**: 내레이션(#90) + 덱 슬라이드(#91) 모두 — 라이브 `/judge` footage가 "no rank change · ±0 pts · Δ=0"이라 "audit changes who wins" 과대주장을 제거하고 실제 코호트(Glasshat 54.3→52.8 등, 순위 유지)로 교체.

**E5. 시연 영상 조립 (ffmpeg) — 산출물 = `glasshat-final-v2.mp4`**
- 내레이션 11비트(MiniMax, voice KimSejun, Speed 1.2; **F10=정직 27초**, cover=F4 재사용→V2에서 교체) + 화면녹화 3개(라이브 감사 / Arize 트레이스 / `/judge` rank-flip) + 덱 영상(Playwright 자동캡처, 2:12).
- 조립: 덱 cover→F7 → 라이브 감사(원속) → Arize(48-spans 단어에 Agent Path 정렬) → `/judge`(로딩 15초→12배속 압축) → 덱 F11 · 11비트 오디오 타임스탬프 배치(amix).
- 보정: 녹화 **dock/메뉴바 crop→깨끗한 16:9**, 덱 카운트다운 **"GO" 잔상 제거**(tpad clone), Arize **"48 spans" 정렬**.
- **V1**(`glasshat-final-2-42.mp4`): cover "Trust it"만 + F4 무음. **V2**(`glasshat-final-v2.mp4`, **권장**): 유저 피드백 반영 — cover(0-5s) **+** F4 히어로(40-45s) **둘 다 "Trace it. Trust it."**(F11에서 same-take 추출, 0.45s stop-start). → brief의 hero "F4 primary + F11 echo" 복원. 오디오싱크·시각 전수검증 완료.

---

## §2 현재 상태

| 항목 | 값 |
|---|---|
| Branch / HEAD | `main` @ **`aa60bf9`** (origin 동기, working tree clean — untracked는 claudedocs 계획문서들뿐) |
| Open PRs | **없음** (#67–#91 전부 머지, merge-commit) |
| Repo | https://github.com/Two-Weeks-Team/glasshat (Apache-2.0) |
| Live web | https://glasshat-web-o366v7tl2q-uc.a.run.app — `/` `/judge` `/participate` 전부 **HTTP 200** ✅ |
| Live API | https://glasshat-api-o366v7tl2q-uc.a.run.app/health → **200** ✅ |
| **Live Phoenix** | https://glasshat-phoenix-o366v7tl2q-uc.a.run.app (Cloud Run + Cloud SQL, `glasshat-calibration` 데이터셋 시드됨) |
| Agent Engine | `reasoningEngines/7480191458771730432` (serving, deep nested trace) |
| Arize AX | project `glasshat`, Space:45136 — deep trace + experiment `glasshat-hit-at-13-gemini` (hit@13 0.6154) |
| **시연 영상** | **`~/Downloads/glasshat-final-v2.mp4`** (1920×1080·30fps·H.264·AAC·**2:41**·~20MB·faststart) ← 제출용 |
| 기본값 | `mock`/`python`/`legacy`/`heuristic`/`code` (parity-preserved) |

**환경:** uv 0.11.7 · node v22.16 · pnpm 9.15 · ffmpeg 사용가능(`curl` 없음→python urllib로 헬스체크). 시크릿: `~/.glasshat-arize.env` · `~/.glasshat-phoenix.env` · `~/.vibevoice-minimax.env` (전부 chmod 600, 재사용 가능). ⚠️ **gcloud active project = `ss-v2-prod` (FOOTGUN)** — 모든 gcloud에 `--project=panelyst-hackathon` + `GOOGLE_CLOUD_QUOTA_PROJECT=panelyst-hackathon`.

---

## §3 다음 세션에서 할 수 있는 것

### 즉시 가능 (자율)
- **영상 미세조정(원하면):** 조립 스크립트 `/tmp/asm.sh`(세그먼트→concat→audio→mux) + `/tmp/make_v2.sh`(cover/F4 = "Trace it. Trust it.")는 **`/tmp`(휘발성)** — 영구화하려면 repo `_scripts/`로 옮길 것. 소재는 `~/Downloads/glasshat-narration-beats/`(F1~F11) + `~/Downloads/glasshat-deck-2-12.mp4` + 데모클립 2개 + 데스크탑 녹화 3개. cover "Trace it. Trust it." 톤이 차분하면 MiniMax로 `Trace it. Trust it.` 단독 생성 후 `tracetrust.mp3` 교체.
- **라이브 재검증:** Phoenix `/participate`에서 "Run live audit" → 실제 Vertex+Phoenix-MCP 호출(~10-20초). AX 스팬 `client.spans.list(project="glasshat")`(resp**.spans**).

### 사용자 입력 필요
- 프로드 보안 하드닝 승인(§4) · Devpost/영상 업로드 결정.

---

## §4 할 수 없는 것 (외부 변수 / 인간 작업)
1. **영상 업로드** — 파일(`glasshat-final-v2.mp4`)은 **완성**. YouTube/Vimeo 공개 업로드는 사람.
2. **Devpost 폼 제출 + Arize 트랙 선택** — 인간만.
3. **자격 자가확인** — 거주지 제외국 + 팀 ≤4명.
4. **프로드 보안 하드닝 재배포** — `SCORING_MODE=structured` + `JUDGE_API_TOKEN`(Secret Manager). 코드/플래그 ship됨; 프로드 플립은 **유저 승인 필요**. 현재 데모=legacy(주입가능)/judge 오픈이며 README가 정직 공개.

---

## §5 추가로 필요한 것 (사용자 확인)
- **프로드 재배포 승인 여부** — 보안 하드닝(structured+token) 또는 `AGENT_RUNTIME=adk` 플립. 둘 다 `infra/deploy.sh --confirm`, 유저-게이트.
- **Devpost 제출 텍스트** — `claudedocs/2026-06-02-devpost-text.md`는 이번 세션 "why now"+Phoenix-live 반영됨(#82/#87); 제출 전 README 최신본과 한 번 더 대조.
- 시크릿 파일 3종 유지/회전 여부.

---

## §6 다음 세션 시작 프롬프트

```text
/handon

이전 세션 핸드오프: claudedocs/2026-06-06-session-handoff.md

상태: 코드·문서·시연영상(glasshat-final-v2.mp4) 전부 완성. 남은 건 행정.
읽고 다음 결정에 답한 뒤 진행하세요:
1. 시연영상 V2를 그대로 업로드/제출할까요, 아니면 cover "Trace it. Trust it." 톤을 MiniMax 단독생성으로 교체할까요?
2. 프로드 보안 하드닝(SCORING_MODE=structured + JUDGE_API_TOKEN) 재배포를 지금 승인하나요? (유저-게이트)
3. Devpost 제출 텍스트를 현 shipped 상태로 최종 검수할까요?
4. 조립 스크립트(/tmp/asm.sh, /tmp/make_v2.sh)를 repo _scripts/로 영구화할까요?

시연 링크: https://glasshat-web-o366v7tl2q-uc.a.run.app/participate (라이브 감사) · /judge (rank board)
참고: 시크릿 ~/.glasshat-arize.env · ~/.glasshat-phoenix.env. gcloud active=ss-v2-prod 풋건 → 항상 --project=panelyst-hackathon.
D-day: 2026-06-11 14:00 PT
```

---

## §7 핵심 자산 위치 reference

| 자산 | 경로 |
|---|---|
| **시연 영상 (제출용)** | `~/Downloads/glasshat-final-v2.mp4` (V1: `glasshat-final-2-42.mp4`) |
| 영상 소재 | `~/Downloads/glasshat-narration-beats/` (F1~F11) · `~/Downloads/glasshat-deck-2-12.mp4` · `glasshat-F8F9-demo-full-40s.mp4` · `glasshat-F10-rankflip-clean.mp4` · `~/Desktop/화면 기록 *.mov`×3 |
| 영상 조립 스크립트 (휘발성/tmp) | `/tmp/asm.sh` · `/tmp/make_v2.sh` (repo 미보존 — 필요시 `_scripts/`로) |
| Phoenix 시드 | `scripts/seed_phoenix_calibration.py` |
| MCP 보정 런타임 | `services/pipeline-orchestrator/src/glasshat/pipeline/adk_runtime.py` |
| 덱 / 내레이션 | `pitch/deck.html` · `pitch/narration-script.md` |
| 라이브 AX 증거 | `claudedocs/arize-evidence/ax-live-capture.json` |
| ADK 2.0 Workflow / 배포 | `services/pipeline-orchestrator/src/glasshat/pipeline/adk_agents.py` · `deploy/agent_engine_deploy.py` |
| 컴플라이언스 | `README.md` · `docs/rapid-agent-compliance.md` · `docs/evidence-matrix.md` |
| 프로드 배포 | `infra/deploy.sh` (유저만 `--confirm`) |

---

## §8 알려진 issue / open question
- **OQ1 — 영상 조립 스크립트 비영구:** `/tmp/asm.sh`·`/tmp/make_v2.sh`는 `/tmp`라 리부트시 소실. 재현 필요하면 repo로 옮길 것. (영상 파일 자체는 `~/Downloads`에 안전.)
- **OQ2 — cover 톤:** V2의 cover/F4 "Trace it. Trust it."은 F11 클로징 take에서 추출 → 차분함. 히어로용 강한 톤 원하면 MiniMax 단독생성 교체.
- **OQ3 — 프로드 데모 보안:** 라이브 Cloud Run = `SCORING_MODE=legacy`(주입가능) + judge 엔드포인트 오픈(`JUDGE_API_TOKEN` 미설정). 하드닝 ship됨, 프로드 플립 유저-게이트. README 정직 공개.
- **OQ4 — Agent Engine vs Cloud Run:** 라이브 Cloud Run = python parity 경로 + 라이브 Phoenix-MCP 보정. genuine ADK 2.0 Workflow deep-trace = 별도 Agent Engine(`7480…`). README가 명확화.
- **OQ5 — gcloud 풋건:** active project `ss-v2-prod`. `--project` 누락시 프로드(8080 social-seeding) 위험.
- **OQ6 — 90MB scraped corpus + spikes/ gitleaks ~253 hits** 공개 전 triage 미완(메모리 `glasshat-spikes-secret-findings`).
- 비용: Phoenix Cloud SQL/Run + 프로드 재배포 + 라이브 eval/실험 — 유저 승인됨.
