# Glasshat — Session Handoff (2026-05-15)

> 새 세션은 **반드시 새 폴더 경로**로 시작: `cd ~/Documents/GitHub/glasshat && /handon`. 이전 핸드오프(2026-05-14)는 `Panelyst` 이름 + `~/Documents/GitHub/panelyst/` 경로 기준이며, 이 세션에서 모두 변경되었습니다.

---

## §0 — 두 줄 요약

**오늘의 진척**: 사용자 지시("수상 가능성과 양쪽 룰과 양쪽 수상에 최대치까지 계획을 완성")에 따라 Phase 1 코드 진입을 보류하고 **Max-Wins Plan(전략) + Technical Apex Pass(고급 기능 47개 결정) + 7-Spike 기술 검증(모두 PASS) + Panelyst → Glasshat 리네이밍**을 완료. 모든 architectural risk 거의 0, Phase 1 빌드 진입 클리어 상태. 신규 팀원 온보딩 HTML 보고서 GitHub Pages에 배포.

**다음 세션 1순위 액션**: §3.1의 4개 진입점 중 하나 선택 → Phase 1 코드 작성 시작. (1.7+1.8 콘텐츠 / 1.3 Qdrant docker-compose / 1.12 Gemini 3 corpus 스크레이핑 / 1.10 Next.js 스캐폴드)

---

## §1 — 진행한 작업 (시간순)

### Phase A — 이전 세션 리로드 + 사용자 메타 지시 (16-17h KST)
- 이전 세션 핸드오프 2026-05-14 자동 로드 (`claudedocs/2026-05-14-session-handoff.md`)
- 사용자 §6 옵션 ⓐⓑⓒⓓ 중 하나 대신 **"수상 가능성과 양쪽 룰과 양쪽 수상에 최대치까지 계획을 완성"** 지시
- Phase 1 코드 진입 보류 결정. Deep 7차원 계획 모드 시작.

### Phase B — Max-Wins Plan v1 (실시간 웹리서치 + 5-전문가 패널)
- 라이브 웹리서치: Qdrant VSD 페이지 / Rapid Agent Devpost 공식 룰 (게시됨 확인) / Qdrant 2025 우승작 / Arize Phoenix MCP / Phoenix 자원 페이지
- 발견:
  - Qdrant submission URL 변경 (`forms.gle/YDQ2TDUi8MqS9Vx28`, 기존 `forms.hl.qdrant.tech` 대체)
  - Rapid Agent 공식 룰 게시. **Tech Implementation 타이브레이커 1순위**. 한국 제외국 명단 ≠ 포함 ✓
  - Qdrant 2025 우승작: **Vector Vintage** (3D terrain + R3F + Qdrant + Mistral + Neo4j). R3F가 top winners 3건 등장
  - Arize 스타터킷: **Google ADK** 사용 (Agent Builder 아님) + Phoenix MCP via Gemini CLI / npx
- 5-전문가 패널(Porter/Christensen/Godin/Doumont/Drucker) 분석 → 권고:
  1. Qdrant VSD = primary, Arize = 7일 repackaging
  2. **Panelyst → Glasshat** 리네이밍 (1순위 alt: Hatwatch / Hatcheck / Tribunal)
  3. 3D 그래프 stretch → must-build
  4. KO i18n 컷, 17 BMAD 풀 표시 컷, signed report UI 5초만 언급
  5. Audit-the-auditor 모먼트 = 양쪽 wow factor
- 사용자 결정: Qdrant primary ✓ · Glasshat 채택 ✓ · 3D must-build "날짜 무시" ✓
- 산출: **`docs/max-wins-plan.md`** (780 lines, 68KB) — 7차원 + 12 locked decisions + 양쪽 데모 스크립트

### Phase C — Gemini 3 코퍼스 전략
- 사용자 제안: `gemini3.devpost.com/project-gallery`의 4,499 제출작이 정확한 시드 코퍼스
- 라이브 페치 확인: 4,499 projects · $100K prize · 심사 weights 공개 (Tech 40% / Innovation 30% / Impact 20% / Presentation 10%) · 24+ ribbon winners
- 사용자 결정: **524 stratified** (24+ winners + 500 random) · Qdrant 데모에만 메타-narrative 명시 · Arize 데모는 Phoenix experiment 관점만
- 산출: max-wins-plan §3.4 신규 + §5.1 Qdrant 데모 close에 메타 캡션 1줄

### Phase D — Wow Moment 기술 디자인
- audit-the-auditor 모먼트 5단계 분해 + ADK + Phoenix MCP 능력 라이브 검증 (Phoenix MCP README + ADK LoopAgent/Custom agents 페치)
- 발견: ADK는 **LoopAgent 네이티브 지원** + Custom BaseAgent + MCPToolset Stdio. Phoenix MCP는 27 tools (get-experiment-by-id, get-span-annotations, get-spans 등 모두 존재)
- 결론: 모든 5단계 기술적 블로커 0개
- 산출: **`docs/wow-moment-design.md`** (515 lines, 38KB) — 토폴로지 + spike spec + 12 fallback

### Phase E — Technical Apex Pass (사용자 질문 "기술적 정점 모두 활용했나?"에 대한 응답)
- 정직한 자가-진단: NO, 미설계 advanced 기능 다수
- 라이브 리서치: Qdrant hybrid+RRF · Recommendation API · Discovery · group-by · Phoenix Online Evals (Arize AX) · Gemini context caching (90% 절감, 4096+ tokens) · Gemini thinking_level · ADK callbacks 6 types
- **47 features 명시적 결정** (33 APPLY + 9 STRETCH + 5 CUT) + 심사축 커버리지 맵
- 데모 스크립트 densification: Qdrant 7 beats · Arize 8 beats · 모든 high-risk wow에 backup beat
- Triple-redundant detection 추가 (Phoenix Online Eval + Phoenix Custom Evaluator + Black hat counter-claim)
- 산출: **`docs/technical-apex-features.md`** (225 lines, 27KB) + max-wins-plan §5 데모 스크립트 재작성 + wow-moment-design §11 보강 + 메모리 `glasshat-technical-apex.md`
- 확률 추정: Qdrant top-3 28-35% → 35-42%, Arize 50-55% → 58-65%

### Phase F — 7-Spike 기술 검증 (실제 코드 실행)
- uv-managed Python 3.12 venv at `spikes/.venv` (Phoenix 15.9.0, ADK, qdrant-client, MCP SDK)
- **모두 PASS** (총 비용 ~$0.0001, 단일 Vertex Flash-Lite call):

| # | Spike | Metric |
|---|---|---|
| A | Phoenix MCP smoke | 27 tools / list-projects 27ms / get-spans 6ms |
| B | ADK LoopAgent + escalation | Convergence 2 iter + max_iter cap |
| C | ADK + Phoenix MCPToolset wiring | LlmAgent 1 run = 7 Phoenix spans (MCP tool call 자동 캡처) |
| D | Calibration policy on toy data | 35.4% MAE↓ held-out, Yellow A1 bucket 66%↓ |
| E | SSE animation latency | 802ms 평균 간격, 16ms 최대 전달 |
| F | Phoenix Online Eval (OSS) | 5/5 classification, eval+5 writes 30ms |
| G | Phoenix Annotation R/W | Write 12ms, full fidelity round-trip |

- 결정적 발견: ADK MCPToolset 정확 와이어링 = `MCPToolset(connection_params=StdioConnectionParams(server_params=mcp.StdioServerParameters(...)))` (두 단계 wrap; 문서 미명시)
- 확률 추정: Qdrant top-3 → 38-45%, Arize → 62-68%
- 산출: **`docs/spike-results.md`** (251 lines, 17KB) + 7 spike scripts + 7 result JSONs + 메모리 `glasshat-spike-validation.md`

### Phase G — 신규 팀원 온보딩 HTML 보고서
- `html-report` 스킬 사용
- 산출: **`claudedocs/2026-05-15-glasshat-onboarding-report.html`** (1,160 lines, 63KB) — 14 sections + 3 Chart.js 차트 + 12 tables + 14 callouts + 14 metric cards + dark dashboard 테마

### Phase H — GitHub Pages 배포
- Worktree-기반 orphan `gh-pages` 브랜치 생성 (현재 작업 브랜치 격리)
- gh API로 Pages 활성화 (이미 default 활성)
- 빌드 시간 ~30초
- 산출: **https://two-weeks-team.github.io/glasshat/** (HTTP 200, last-modified 07:07:45 UTC)

### Phase I — Glasshat 리네이밍 마이그레이션 실행
- 이름 충돌 체크: GitHub `Two-Weeks-Team/glasshat` 비어있음 ✓; SaaSWorthy SEO 도구 존재 (다른 카테고리, 사용자 진행 결정)
- branch `chore/rename-glasshat` 생성
- sed 일괄 교체 (Panelyst → Glasshat / PANELYST_ → GLASSHAT_): docs/architecture.md, gcp-setup.md, max-wins-plan.md, technical-apex-features.md, wow-moment-design.md, HANDOFF.md, PLAN.md, README.md, scripts/README.md, spikes/03_spike_c_adk_mcptoolset.py, .env.example
- 보존 (per memory `glasshat-max-wins-decisions` §8): GCP 프로젝트 `panelyst-hackathon`, SA `panelyst-dev`, GCS buckets, 메모리 slug `panelyst-project`
- `.env` 백업 + diff 사용자 승인 + 적용 (14 keys 변경)
- README 전면 재작성 (max-wins-plan §7 narrative)
- 메모리 `panelyst-project.md` body 업데이트 (post-rename 상태 반영, slug 유지)
- PR #1 생성 + 머지 (`gh pr merge --merge`, squash 금지 룰 준수): merge commit `5ac5ba7`
- `gh repo rename glasshat` 실행: Two-Weeks-Team/panelyst → **Two-Weeks-Team/glasshat** ✓
- `git remote set-url origin` 업데이트
- 로컬 폴더 rename: `~/Documents/GitHub/panelyst` → `~/Documents/GitHub/glasshat`
- uv venv (`spikes/.venv`) post-mv 작동 확인 — Phoenix 15.9.0 import OK
- HANDOFF.md + 온보딩 HTML 폴더/repo 경로 패치 + commit `9255e9a`
- gh-pages 재발행 (`6cd0366`): https://two-weeks-team.github.io/glasshat/ 새 경로 반영
- 옛 URL https://two-weeks-team.github.io/panelyst/ → 404 (GitHub Pages는 Pages URL 자동 리다이렉트 안 함, repo URL만 함)

---

## §2 — 현재 상태

### Git
- Working directory: `/Users/kimsejun/Documents/GitHub/glasshat/`
- Branch: `main` (clean, origin과 동기)
- Origin: `https://github.com/Two-Weeks-Team/glasshat.git`
- 최근 4 commits (이번 세션 추가):
  - `9255e9a` chore: update folder/repo paths after gh repo rename + local mv
  - `5ac5ba7` Merge pull request #1 from Two-Weeks-Team/chore/rename-glasshat
  - `c6d62bb` chore: rename Panelyst → Glasshat + add max-wins planning + spike validation
  - (이전: `baac1cd` docs: session handoff 2026-05-14 ...)

### Branches (remote)
| Branch | 역할 | 상태 |
|---|---|---|
| `main` | 메인 코드 + 문서 | clean, 9255e9a |
| `gh-pages` | GitHub Pages content (orphan) | 6cd0366, 자동 배포 |
| (deleted) `chore/rename-glasshat` | 머지 후 자동 삭제 | — |

### Live URLs
| | URL |
|---|---|
| Repo | https://github.com/Two-Weeks-Team/glasshat |
| GitHub Pages (온보딩 보고서) | **https://two-weeks-team.github.io/glasshat/** |
| PR #1 (merged) | https://github.com/Two-Weeks-Team/glasshat/pull/1 |

### 빌드 / 검증 메트릭 (스파이크)
- 7/7 PASS · 총 ~$0.0001 Vertex 비용 · 환경 Python 3.12.4 / Node 24 / Phoenix 15.9.0 / Docker 미실행 (필요 없음)
- Calibration policy 검증: 35.4% MAE↓ held-out (target ≥15%)
- SSE pacing: 802ms 평균 (target 800±100ms)

### 환경 상태
| 자원 | 상태 |
|---|---|
| GCP 프로젝트 `panelyst-hackathon` | 활성, 13 APIs 활성화 |
| Service Account `panelyst-dev@panelyst-hackathon.iam.gserviceaccount.com` | 활성, 키 `~/.config/gcloud/panelyst-dev-sa-key.json` mode 600 |
| `.env` (gitignored) | post-rename (GLASSHAT_* 14 keys) · 백업 `.env.backup-pre-rename` 보존 |
| `.env.example` | post-rename + 신규 키 prefix · 위치: repo root |
| Qdrant 컬렉션 | 미생성 (Phase 1.3) |
| Phoenix Cloud 계정 | 미가입 (in-process 또는 self-host 로컬 docker로 dev) |
| Arize 스페이스 | 미가입 (위와 동일) |

### 영구 메모리
경로: `/Users/kimsejun/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/`
- 신규 entries (이번 세션):
  - `glasshat-max-wins-decisions.md` — 12 locked decisions
  - `glasshat-technical-apex.md` — 33 APPLY + 9 STRETCH + 5 CUT
  - `glasshat-spike-validation.md` — 7-spike 결과
- 갱신 entries: `panelyst-project.md` (slug 유지, 본문은 Glasshat 상태) · `MEMORY.md` (3 신규 entries 인덱스 추가)

---

## §3 — 다음 세션에서 할 수 있는 것

### §3.1 즉시 가능 (사용자 입력 없이 진행 가능한 작업 4개)

다음 중 하나 선택하면 Phase 1 진입:

**A. Phase 1.7 + 1.8 — 콘텐츠 (코드 의존성 없음, 1일)**
- `packages/rubric/bmad-rubric.yaml` (17항목 100점) + `packages/rubric/techniques.yaml` (≥20 active)
- `agents/{white,red,yellow,black,green,blue}/prompt.md` system prompts
- Phoenix Prompt Playground 등록 (STRETCH 2.8)

**B. Phase 1.3 — Qdrant 로컬 + 6 컬렉션 스키마 (1-2일)**
- `infra/docker-compose.local.yml` + `services/shared/qdrant.py` + `packages/shared/qdrant-schemas/<collection>.yaml` (hybrid dense+sparse + payload index + Scalar Quantization on past_evals)
- Reference: `qdrant-collection-design` 메모리

**C. Phase 1.12 — Gemini 3 코퍼스 스크레이핑 (1-2일, 파이프라인 코드 무관)**
- robots.txt 확인 + 188 페이지 인덱스 수집 (1 RPS throttle)
- Stratified 샘플링 524개 (24+ winners + 500 random)
- Devpost 디테일 페치 → `seed/gemini3-projects-524.jsonl`
- Reference: `docs/wow-moment-design.md` §6.3

**D. Phase 1.1 + 1.2 — Python 셋업 + LLM 어댑터 (2일)**
- `pyproject.toml`, ruff/mypy/pytest, `services/` 구조
- `services/shared/llm.py`: Vertex global/regional 라우팅 + 3-tier + thinking_level + context caching + responseSchema + OpenInference span 자동
- Phase 1 코드의 토대 — 모든 후속 작업 의존

### §3.2 사용자 입력 필요

- **팀 구성 확정** (Glasshat top-3 등 양쪽 해커톤 1-4명 등록): 현재 솔로, 양쪽 제출 전 결정 필요
- **Phoenix Cloud / Arize 가입** (Arize 트랙 필수): Phase 1.4 진입 시 또는 hosted run 시점
- **상업화 의도 시 Glasshat trademark 재검토** (해커톤 자체엔 무관)
- **2026 Qdrant Best-in-Category 스폰서 게시 시 알림**: 매칭 스폰서 발견 시 secondary narrative 추가 가능

---

## §4 — 할 수 없는 것 (외부 변수)

- **Rapid Agent 공식 룰 변경**: 게시됨 확인했으나 추후 amendment 가능 — 매주 재확인 권장
- **2026 Qdrant Best-in-Category 스폰서 리스트 미공개**: Qdrant 측 발표 대기
- **Gemini 3.1 Pro preview API 변경**: 변경 시 LLM 어댑터의 `gemini-2.5-pro` fallback로 자동 처리 가능
- **Phoenix Cloud free tier rate-limit 정책**: 변경 시 self-host docker로 fallback (interface abstraction 이미 설계됨)
- **데모 녹화용 Phoenix corpus 사전 시드**: Phase 1.12 + 1.13 완료 시점에만 가능, 코드 빌드 선행

---

## §5 — 추가로 필요한 것

### §5.1 사용자가 확인해야 할 항목
- [ ] `Glasshat` 이름 최종 확정 (이번 세션에 결정됨, 확인용)
- [ ] 팀 구성 (Devpost 등록 시 필요)
- [ ] Phase 1 어디서 시작할지 (§3.1 A/B/C/D 중 선택)
- [ ] 추후 GitHub Pages 보고서 비공개 전환 의향 (현재 누구나 접근 가능, 해커톤 심사관 포함)

### §5.2 환경 점검 (새 세션 시작 시 자동 실행)
- [ ] `cd ~/Documents/GitHub/glasshat` 작동 (panelyst 아님 — 폴더 rename됨)
- [ ] `git status` 깨끗 + remote URL = `Two-Weeks-Team/glasshat.git`
- [ ] `gh auth status` — gh CLI 로그인 유효
- [ ] `~/.config/gcloud/panelyst-dev-sa-key.json` 존재 + mode 600 (GCP 자원명은 KEEP — 변경 안 함)
- [ ] `.env`의 `GLASSHAT_*` 키들 채워짐 (14개)

---

## §6 — 다음 세션 시작 프롬프트

### 폴더 이동 + 진입 단계별 가이드

이전 세션이 `panelyst` 폴더에서 끝났고, 이번 세션에 폴더가 `glasshat`으로 rename됐습니다. **세 가지 가능한 시작 시나리오**:

**시나리오 1 — 일반 (가장 자주 사용)**: 이미 `~/Documents/GitHub/glasshat`가 존재함을 알고 있는 경우

```bash
cd ~/Documents/GitHub/glasshat
/handon
```

**시나리오 2 — 이전 명령 기억 (panelyst로 cd 시도)**: 이전 핸드오프나 메모리에서 `panelyst`라는 이름이 나왔을 때

```bash
# panelyst 폴더는 더 이상 존재하지 않음
cd ~/Documents/GitHub/panelyst   # → No such file or directory
# 상위로 이동 후 변경된 이름 확인
cd ~/Documents/GitHub/
ls -la | grep -i hat              # glasshat 발견
cd glasshat
/handon
```

**시나리오 3 — 새 머신 / 새 클론**: 처음 클론하는 경우

```bash
cd ~/Documents/GitHub/
gh repo clone Two-Weeks-Team/glasshat     # 또는 git clone https://github.com/Two-Weeks-Team/glasshat.git
cd glasshat
cp .env.example .env                       # 새 환경 셋업 시
# .env 값 채우기 (docs/gcp-setup.md 참고)
/handon
```

### 복사-붙여넣기 가능한 시작 프롬프트

```text
/handon

이전 세션 핸드오프: claudedocs/2026-05-15-session-handoff.md

읽고 다음 결정 사항에 답한 뒤 진행하세요:
1. Phase 1 어디서 시작? (§3.1의 A 콘텐츠 / B Qdrant / C 코퍼스 스크레이핑 / D Python+LLM 어댑터)
2. 팀 구성 — 솔로 유지 또는 합류 인원 있나요?
3. Phoenix Cloud / Arize 가입을 지금 진행, 아니면 Phase 1.4 도달 시?
4. GitHub Pages 온보딩 보고서 공개 유지, 비공개 전환, 또는 sanitize?

해커톤 D-day: Qdrant VSD 2026-06-01 23:59 PT · Rapid Agent 2026-06-11 14:00 PT (사용자는 "시간 무시" 지시 — 마감일은 우선순위 ordering에만 사용)

핵심 룰 재확인: non-chatbot · all-code-in-period · Apache-2.0 in About sidebar · Vertex SA key (AI Studio 아님) · ADK on Cloud Run (Agent Builder 등록만)
```

---

## §7 — 핵심 자산 위치 reference

### 권위 문서 (반드시 읽기)
| 파일 | 역할 | 크기 |
|---|---|---|
| `README.md` | 1페이지 컨셉 + 양쪽 demo narration + compliance disclosure | ~9KB |
| `docs/max-wins-plan.md` | 듀얼 제출 winning thesis + 12 locked decisions + 양쪽 데모 스크립트 | 780 lines · 68KB |
| `docs/wow-moment-design.md` | Audit-the-auditor 5단계 + 토폴로지 + 3-redundant detection + 12 fallback | 515 lines · 38KB |
| `docs/technical-apex-features.md` | 47 features 결정 매트릭스 + 심사축 커버리지 맵 | 225 lines · 27KB |
| `docs/spike-results.md` | 7-spike 결과 + 발견 + Phase 1 진입 권고 | 251 lines · 17KB |
| `docs/architecture.md` | 토폴로지 + 에이전트 그래프 + 시퀀스 + 페이즈별 배포 | ~12KB |
| `docs/gcp-setup.md` | 검증된 GCP 부트스트랩 + Gemini 3 측정 | ~8KB |
| `PLAN.md` | 엔지니어링 인벤토리 (umbrella mirror) · §1 ADDENDUM이 max-wins-plan.md를 권위로 가리킴 | ~32KB |
| `HANDOFF.md` (in-repo) | 2026-05-14 핸드오프 (path는 patched, 내용은 outdated) | ~7.6KB |
| `claudedocs/2026-05-14-session-handoff.md` | 이전 세션 (Phase 0 완료 시점) | ~10KB |
| `claudedocs/2026-05-15-session-handoff.md` | **본 문서** | — |
| `claudedocs/2026-05-15-glasshat-onboarding-report.html` | 신규 팀원 온보딩 (14 sections + 차트 + Pages 배포) | ~73KB |

### Spike 스크립트 (재현 가능)
- `spikes/01_spike_a_phoenix_mcp_smoke.py` ~ `07_spike_g_phoenix_annotations.py`
- `spikes/results/*.json` — 모두 `overall_pass=true`
- `spikes/.venv/` — uv-managed venv (Phoenix 15.9.0, ADK, qdrant-client, MCP)
- `spikes/pyproject.toml` (name=glasshat-spikes) + `uv.lock`

### 영구 메모리 (Claude Code 세션 간 자동 로드)
경로: `/Users/kimsejun/.claude/projects/-Users-kimsejun-Documents-GitHub-hackathon-submissions/memory/`
- `MEMORY.md` (인덱스)
- `panelyst-project.md` (slug 유지, post-rename 본문)
- `glasshat-max-wins-decisions.md`
- `glasshat-technical-apex.md`
- `glasshat-spike-validation.md`
- `gemini-model-panel-verified.md`
- `gcp-panelyst-hackathon.md`
- `qdrant-vsd-hackathon.md`, `rapid-agent-hackathon.md`
- `qdrant-collection-design.md`, `fairthon-lineage.md`
- `hackathon-pipeline-2026-may-jun.md`
- `production-safety-rules.md`, `user-*.md`

### 외부 URL (출처 검증용)
- Qdrant VSD: https://try.qdrant.tech/hackathon-vsd · 제출 form https://forms.gle/YDQ2TDUi8MqS9Vx28
- Rapid Agent: https://rapid-agent.devpost.com/ · 룰 /rules · Arize /details/arize-resources
- Qdrant 2025 winners: https://qdrant.tech/blog/vector-space-hackathon-winners-2025/
- Phoenix MCP README: https://github.com/Arize-ai/phoenix/blob/main/js/packages/phoenix-mcp/README.md
- Arize 스타터킷: https://github.com/Arize-ai/gemini-hackathon
- ADK docs: https://adk.dev/ (구 google.github.io/adk-docs 리다이렉트)
- Gemini 3 hackathon (524 corpus 출처): https://gemini3.devpost.com/

---

## §8 — 알려진 issue / open question

### Open questions (대기 중)
1. **2026 Qdrant Best-in-Category 스폰서**: Qdrant 측 미공개. 매주 모니터링 — 매칭 발견 시 secondary narrative 추가.
2. **Rapid Agent 룰 amendment 가능성**: 게시됨, 그러나 contest 진행 중 변경 가능 — 매주 페이지 재확인.
3. **Phoenix Cloud free tier 정책 변경**: monitor.
4. **팀 등록 (Devpost)**: 솔로 / 합류 미정 — 양쪽 제출 전 결정.

### Known issues (있지만 블로커 아님)
- GitHub Pages 옛 URL `/panelyst/` 404 — GitHub는 Pages URL 자동 리다이렉트 안 함. 공유 링크는 `/glasshat/` 사용.
- `panelyst-project.md` 메모리 slug 유지 — backlink 연속성 위해. 본문은 모두 Glasshat 반영.
- GCP 자원명 (`panelyst-hackathon`, `panelyst-dev` 등)은 의도적 KEEP — rename 시 billing/IAM 혼란, 심사 가치 0.
- `HANDOFF.md` (in-repo) 내용은 2026-05-14 기준 outdated. 본 핸드오프 (`claudedocs/2026-05-15-session-handoff.md`)가 최신.

### 잠재 리스크 (Phase 1 진입 시 점검)
- **★ Phoenix corpus 사전 시드 누락**: 데모 녹화 전 Phase 1.12 (524 scrape) + 1.13 (Phoenix Experiment 시드) 필수. 누락 시 audit 모먼트에서 consultation이 빈손 → 데모 평탄. 자세히는 `docs/wow-moment-design.md` §6.
- **3D 그래프 시각적 under-deliver**: 2D radar fallback 동일 데이터 보장. 시각 검증 후만 죽이기.
- **듀얼 제출 분산 → 양쪽 mediocre**: Lock — Qdrant 제출 전 zero Arize-only 코드.

---

## §9 — 이번 세션에서 추가된 산출물 인덱스

| 카테고리 | 신규 파일 / 변경 |
|---|---|
| 권위 문서 (신규) | `docs/max-wins-plan.md` · `docs/wow-moment-design.md` · `docs/technical-apex-features.md` · `docs/spike-results.md` |
| 권위 문서 (수정) | `README.md` (전면 재작성) · `PLAN.md` (ADDENDUM 추가) · `docs/architecture.md` · `docs/gcp-setup.md` · `HANDOFF.md` (path patch) · `scripts/README.md` |
| 환경 | `.env` (14 keys: PANELYST_* → GLASSHAT_*) · `.env.example` (동일) · `.env.backup-pre-rename` · `.env.example.backup-pre-rename` (둘 다 gitignored) · `.gitignore` (backup patterns 추가) |
| Spike 스크립트 | `spikes/` 전체 (7 scripts + 7 result JSONs + pyproject + uv.lock + README + .venv) |
| HTML 보고서 | `claudedocs/2026-05-15-glasshat-onboarding-report.html` |
| 핸드오프 | `claudedocs/2026-05-15-session-handoff.md` (본 문서) |
| 영구 메모리 (신규) | `glasshat-max-wins-decisions.md` · `glasshat-technical-apex.md` · `glasshat-spike-validation.md` |
| 영구 메모리 (수정) | `MEMORY.md` (3 entries 인덱스 추가) · `panelyst-project.md` (post-rename body) |
| Git | `chore/rename-glasshat` branch (PR #1 merged) · `gh-pages` branch (orphan, Pages 호스팅) |
| External | repo rename Two-Weeks-Team/panelyst → glasshat · 로컬 folder rename · 원격 URL 업데이트 |

---

작성: 2026-05-15 16:14 KST · 다음 세션은 이 폴더에서 `/handon`으로 즉시 이어집니다.
