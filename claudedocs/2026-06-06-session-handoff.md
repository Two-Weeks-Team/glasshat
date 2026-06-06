# Glasshat — Session Handoff (2026-06-06, V3 · pre-submission FINAL)

## §0 두 줄 요약
- **비기술자용:** 라이브 Agent Engine + Arize AX + Phoenix-MCP 배포 위에, 이번 세션은 **3분 시연 영상(V2)을 ffmpeg로 완성**하고, **GitHub About/Pages 메타데이터를 정직하게 교정**하고, **제출 전 5각도 종합감사(병렬 에이전트)로 honesty·secrets·hygiene 갭을 전부 닫았다**(PR #92). 코드·문서·영상·repo-메타 전부 제출 준비 완료.
- **다음 세션 1순위:** 남은 건 **사람 손이 필요한 행정뿐** — ① `~/Downloads/glasshat-final-v2.mp4`를 YouTube/Vimeo 공개 업로드 ② Devpost 폼 제출(+Arize 트랙) ③ 거주지/팀 자격 자가확인. (선택) 프로드 보안 하드닝은 **§SEC 참고 — 권장은 "현 상태 유지"**.

D-day: **2026-06-11 14:00 PT**

---

## §1 진행한 작업 (시간순)

### Phase A–D — (이전 세션, HEAD `9e3d4d3`) 클라우드 /goal + 라이브 AX
`#67–#71`(GEAP·ADK2.0 Workflow·Agent Engine·AX Experiment·A2A) → PART B 실제 Agent Engine 배포+라이브 쿼리 → `#72–#75`(ARIZE creds → 라이브 AX 실험 hit@13 0.6154 + deep trace + 랜딩 proof) → `#76` 전수감사. (상세는 git 히스토리.)

### Phase E — (이번 세션 전반) Phoenix-MCP 실배포 · 정직 F10 · 영상
- **#81/#82** "why now" 내러티브(vibe-coding 범람) → 덱/랜딩/README/Devpost.
- **#83–#85** **Phoenix MCP를 GCP에 실배포**: `glasshat-phoenix` Cloud Run + Cloud SQL(ENTERPRISE), `scripts/seed_phoenix_calibration.py`로 `glasshat-calibration` 시드, 잠복버그 3개(p25/p75·dataset_name·data-wrapper) 수정, API 2Gi, Dockerfile phoenix-mcp 사전설치, 칩 wired→live, 프로드 재배포 검증(eval 8.0→6.87, cell n 7→8).
- **#86–#88** 문서 stale spike-D→live Phoenix-MCP 전수 교체.
- **#89–#91** 덱 재타이밍 + **정직 F10**(narration #90 + 덱 #91): "recalibration, not a fake flip"(라이브 /judge가 "no rank change·±0 pts·Δ=0").
- **영상 V1→V2**: 내레이션 11비트(MiniMax, F10=정직27초) + 녹화3개(라이브감사/Arize/judge) + 덱영상(Playwright) → ffmpeg 조립. dock crop→16:9, GO 잔상 제거, Arize 48-spans 정렬. **V2 = cover+F4 둘 다 "Trace it. Trust it."**(F11 same-take, 0.45s stop-start).

### Phase F — (이번 세션 후반) 제출 전 메타·정직·보안 FINAL (main `1e47479`)
- **GitHub About 교정**: 옛 "Panelyst" 설명 → Glasshat 한줄 + homepage→**라이브 Cloud Run 데모** + topics 14개.
- **GitHub Pages 랜드마인 제거**: `two-weeks-team.github.io/glasshat`이 한국어 내부 "온보딩 보고서"(Panelyst×15·"4,499/524 corpus"·"-preview" 모델·Qdrant·prototype.html "503 anchors")였음. API unpublish는 **org 제한 422**로 막힘 → **gh-pages를 라이브 데모 redirect로 force-replace**(noindex). 검증: Panelyst=0.
- **5각도 병렬 감사**(compliance/honesty/security/presentation/live) → **PR #92**(merge): README+Devpost "audit changes who wins"→정직 recalibration/Δ=0; 샘플 7.84→7.6; min-instances 0→1; **GCP billing-id+email redact 6파일**; .gitignore 보안패턴; .env.example Panelyst 제거; **87MB raw 스크랩 untrack**(gemini3_dataset/projects.json, golden set winners/submissions.json 유지=재현); README 배지+스크린샷+영상placeholder+보안콜아웃; Devpost repo링크. **내부 기획문서 10개(claudedocs/2026-06-05-*)는 커밋 안 함**(미추적 유지).
- **검증**: Agent Engine `7480191458771730432`가 **유일 서빙**(REST 실측; 메모리의 3417은 삭제됨→docs 정확). 라이브 web/api/phoenix 전부 200.
- **보안 하드닝 정밀분석** → §SEC.

---

## §2 현재 상태

| 항목 | 값 |
|---|---|
| Branch / HEAD | `main` @ **`1e47479`** (origin 동기, working tree clean; untracked = claudedocs/2026-06-05-* 기획문서 + 영상소재) |
| Open PRs | **없음** (#67–#92 전부 머지) |
| Repo About | ✅ Glasshat 설명 · homepage=라이브 데모 · 14 topics |
| GitHub Pages | ✅ 라이브 데모 redirect (stale 제거) |
| Live web/api/phoenix | 전부 **200**: web `glasshat-web-o366v7tl2q-uc.a.run.app`(/·/judge·/participate), api `.../health`, phoenix `glasshat-phoenix-o366v7tl2q-uc.a.run.app` |
| Agent Engine | `reasoningEngines/7480191458771730432` (유일 서빙, deep trace) |
| Arize AX | project `glasshat`, Space:45136 — deep trace + `glasshat-hit-at-13-gemini`(hit@13 0.6154) |
| **시연 영상** | **`~/Downloads/glasshat-final-v2.mp4`** (1920×1080·30fps·H.264·AAC·**2:41**·~20MB) ← 제출용 |
| 기본값 | `mock`/`python`/**`legacy`**/`heuristic`/`code` (데모 byte-identical, parity-preserved) |

**환경:** uv 0.11.7 · node v22.16 · pnpm 9.15 · `curl` 없음(python urllib 사용). 시크릿(전부 chmod 600 재사용가능): `~/.glasshat-arize.env` · `~/.glasshat-phoenix.env` · `~/.vibevoice-minimax.env`. ⚠️ **gcloud active=`ss-v2-prod` FOOTGUN** → 항상 `--project=panelyst-hackathon` + `GOOGLE_CLOUD_QUOTA_PROJECT=panelyst-hackathon`.

---

## §3 다음 세션에서 할 수 있는 것 (자율)
- **영상 미세조정**: 조립 스크립트 `/tmp/asm.sh`+`/tmp/make_v2.sh`는 **`/tmp`(휘발성)** — 영구화하려면 repo `_scripts/`로. 소재: `~/Downloads/glasshat-narration-beats/`(F1~F11) + `glasshat-deck-2-12.mp4` + 데모클립2 + `~/Desktop/화면 기록 *.mov`×3.
- **라이브 재검증**: `/participate` "Run live audit"(실제 Vertex+Phoenix-MCP, ~10-20초). AX 스팬 `client.spans.list(project="glasshat")`(resp**.spans**).
- (선택) 보안 하드닝 플립 — §SEC의 명령 + 재검증 절차.

---

## §4 할 수 없는 것 (사람 작업)
1. **영상 업로드** — 파일 완성. YouTube/Vimeo 공개 + Devpost/README placeholder에 링크는 사람.
2. **Devpost 폼 제출 + Arize 트랙 선택** — 인간만.
3. **자격 자가확인** — 거주지 제외국 + 팀 ≤4명.

---

## §SEC 🔒 프로드 보안 하드닝 (유저-게이트) — 상세·정확 (실측 기반)

**결론 먼저: 공개 데모는 현 상태(legacy/open) 유지를 권장.** 이미 README에 정직 공개됐고, 하드닝 경로가 ship+flag-gated라 "구현했고 플립만 하면 됨"이 신뢰 가점. 플립하면 데모가 깨짐(아래).

### 이미 항상 ON (gated 아님, ship됨)
- **heuristic injection guard** (`agents/.../injection_guard.py`) — `SCORE:10`·`ignore previous`·`</submission>`(tag-forge)·`act as judge` 등 패턴을 Arize에 `glasshat.injection_flag` span으로 **관측**. **차단은 안 함**(구조적 방어가 진짜 차단).
- **rate limit** 30/min/IP(sliding window, `app.py` `_rate_limit`) · **SSRF 차단**(private/loopback/link-local/metadata IP 무조건 차단, redirect 미추종, PARTICIPANT는 `rules_url` 불가) · **CORS** 라이브는 web origin 잠금.

### 유저-게이트 플립 2개 (config.py 기본 = legacy / 빈값)
1. **`SCORING_MODE=structured`** — *구조적* 주입 방어. (`agents/.../hats.py:155-165` 실측)
   - legacy: submission을 hat 프롬프트에 직접 삽입 → 응답에서 첫 `SCORE:` 정규식 스크랩 → 심어진 `SCORE: 10`이 점수를 **조종 가능**.
   - structured: submission을 **격리 `<submission>` 블록** + **system_instruction**(역할 분리) + **타입드 JSON `score`**(`response_schema=HatScoreResponse`)로 받음 → 심어진 `SCORE:10`이 점수가 **될 수 없음**(그냥 채점 대상 텍스트).
2. **`JUDGE_API_TOKEN`** — judge 표면 Bearer 게이팅. (`app.py:158-188` 실측)
   - 게이팅 대상: **score override**(`/api/.../override`, `_require_judge`), **JUDGE-mode 실행**(rules_url/custom_yaml 잠금해제 = SSRF+임의 루브릭, `_enforce_mode`), **un-redacted 뷰**.
   - 빈값=열림(1회 경고). `/participate`(participant preset)는 토큰과 무관하게 열림.

### 플립 방법 (정확)
`infra/deploy.sh:134`의 `API_ENV`에 `SCORING_MODE=structured` 추가 + `JUDGE_API_TOKEN`을 Secret Manager 시크릿(`--set-secrets`)으로 주입 → 사용자가 `bash infra/deploy.sh --confirm`(프로드 게이트, gcloud active 무시하고 panelyst-hackathon 타겟). deploy.sh:129-133 주석이 정확히 이 플립을 "judged/secured instance용"으로 안내.

### ⚠️ 대가/리스크 (핵심)
| 플립 | 데모 영향 |
|---|---|
| `JUDGE_API_TOKEN` 설정 | **공개 `/judge` 데모 깨짐**: override/lock/mark-winner → 토큰 없는 심사위원에게 **401**, un-redacted 뷰 redacted. (`/participate`는 영향 없음) |
| `SCORING_MODE=structured` | **라이브 점수 바뀜**(structured ≠ legacy 스크랩) → 캐시 `/participate` 샘플 + **녹화 영상(legacy 숫자)**과 어긋남. + **프로드 미검증**(라이브·테스트 전부 legacy) → 마감 직전 첫 라이브 = parse/점수 리스크 |
| 공통 | 프로드 재배포(이미지 재빌드, 짧은 다운타임), 유저-게이트 |

### 옵션
- **(권장) 플립 안 함** — 공개 데모 유지. README 정직 disclosure + ship된 하드닝 경로 = 성숙한 답 + 신뢰 가점. 데모는 실제 이해관계 없어 위험은 이론적.
- **(중간) `SCORING_MODE=structured`만** — 주입 제거 + `/judge` 버튼 생존(JUDGE_API_TOKEN 빈값 유지). 단 점수 shift + 프로드 미검증 → 즉시 재검증 + 캐시 샘플 재생성 필요.
- **(별도 secured 인스턴스)** — 보안 심사용 별도 URL이면 둘 다 플립 + 검증. 공개 인터랙티브 데모용으론 비권장.

---

## §5 추가로 필요한 것 (사용자 확인)
- 보안 하드닝 플립 여부 + 옵션(§SEC) — 기본 권장은 "현 상태 유지".
- Devpost 제출 텍스트 최종 검수(`claudedocs/2026-06-02-devpost-text.md` — 이번 세션 정직 교정 반영됨).
- 시크릿 파일 3종 유지/회전.

---

## §6 다음 세션 시작 프롬프트

```text
/handon

이전 세션 핸드오프: claudedocs/2026-06-06-session-handoff.md

상태: 코드·문서·시연영상(glasshat-final-v2.mp4)·repo-메타 전부 완성. 남은 건 행정.
읽고 다음 결정에 답한 뒤 진행하세요:
1. 시연영상 V2를 그대로 제출할까요, cover "Trace it. Trust it." 톤을 MiniMax 단독생성으로 교체할까요?
2. 보안 하드닝(§SEC) — 플립 안 함(권장) / structured만 / 둘 다·secured 별도 중 무엇?
3. Devpost 제출 텍스트 최종 검수할까요?
4. 조립 스크립트(/tmp/asm.sh, /tmp/make_v2.sh)를 repo _scripts/로 영구화할까요?

시연: https://glasshat-web-o366v7tl2q-uc.a.run.app/participate (라이브 감사) · /judge (rank board)
시크릿: ~/.glasshat-arize.env · ~/.glasshat-phoenix.env. gcloud active=ss-v2-prod 풋건 → 항상 --project=panelyst-hackathon.
D-day: 2026-06-11 14:00 PT
```

---

## §7 핵심 자산 위치 reference

| 자산 | 경로 |
|---|---|
| **시연 영상 (제출용)** | `~/Downloads/glasshat-final-v2.mp4` (V1: `glasshat-final-2-42.mp4`) |
| 영상 소재 | `~/Downloads/glasshat-narration-beats/`(F1~F11) · `glasshat-deck-2-12.mp4` · `glasshat-F8F9-demo-full-40s.mp4` · `glasshat-F10-rankflip-clean.mp4` · `~/Desktop/화면 기록 *.mov`×3 |
| 영상 조립 스크립트(휘발성/tmp) | `/tmp/asm.sh` · `/tmp/make_v2.sh` (repo 미보존) |
| 보안 — scoring mode | `agents/src/glasshat/agents/hats.py` (legacy vs structured) · `agents/.../injection_guard.py` |
| 보안 — judge gate | `apps/api/src/glasshat/api/app.py` (`_require_judge`/`_enforce_mode`) · `packages/shared/.../config.py` |
| 프로드 배포 | `infra/deploy.sh` (유저만 `--confirm`; SCORING_MODE/JUDGE_API_TOKEN은 L134 API_ENV) |
| Phoenix 시드 / MCP | `scripts/seed_phoenix_calibration.py` · `services/.../adk_runtime.py` |
| 덱 / 내레이션 | `pitch/deck.html` · `pitch/narration-script.md` |
| 라이브 AX 증거 | `claudedocs/arize-evidence/ax-live-capture.json` |
| 컴플라이언스 | `README.md` · `docs/rapid-agent-compliance.md` · `docs/evidence-matrix.md` |

---

## §8 알려진 issue / open question
- **OQ1 — 보안 하드닝**: §SEC. 기본 권장 = 현 상태 유지(정직 공개 + ship된 opt-in). 플립 시 데모 깨짐 + 점수 shift + 프로드 미검증.
- **OQ2 — 영상 조립 스크립트 비영구**: `/tmp/*.sh` 리부트시 소실. 영상 파일은 `~/Downloads`에 안전.
- **OQ3 — cover 톤**: V2 cover/F4 "Trace it. Trust it."은 F11 클로징 take 추출 → 차분. 강한 톤 원하면 MiniMax 단독생성 교체.
- **OQ4 — Agent Engine vs Cloud Run**: 라이브 Cloud Run = python parity + 라이브 Phoenix-MCP. genuine ADK 2.0 Workflow deep-trace = 별도 Agent Engine(`7480…`). README 명확화.
- **OQ5 — gcloud 풋건**: active `ss-v2-prod`. `--project` 누락시 프로드(8080 social-seeding) 위험.
- **OQ6 — claudedocs/ 공개**: 세션 핸드오프·기획문서가 tracked(투명성). billing-id+email은 redact 완료. 내부 maximal/security specs(2026-06-05-*)는 미추적 유지(비공개). 90MB raw 스크랩 untrack 완료(golden set만 유지).
- 비용: Phoenix Cloud SQL/Run + 프로드 재배포 + 라이브 eval/실험 — 유저 승인됨.
