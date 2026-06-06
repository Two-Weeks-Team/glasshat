# Glasshat / Panelyst — Session Handoff (2026-05-21)

> **이 문서가 최신 권위 핸드오프입니다.** `claudedocs/2026-05-15-session-handoff.md`는 **구 dual-track(Qdrant primary + Arize)** 기준이라 아래 결정들과 상충 — 본 문서가 대체합니다.
>
> ⚠️ **머신 간 주의**: Claude Code 영구 메모리(`~/.claude/projects/.../memory/*.md`)는 **이 컴퓨터에만** 있고 git으로 전송되지 않습니다. 다른 컴퓨터의 새 세션은 **이 문서 + `claudedocs/hackathon-source-2026-05-21/`** 를 권위 소스로 삼으세요.

---

## §0 — 한 줄 요약

이번 세션은 **코드 0줄**. 대신 (a) 정체성을 **Arize 트랙 단독**으로 확정, (b) Rapid Agent 공식 룰/리소스/Arize 자료 **원문 캡처 + 학습**, (c) 룰과 충돌하던 전제 3건을 **잠긴 결정 6건**으로 정정, (d) GCP 배포 타깃 검증. **다음 세션 1순위 = 빈 scaffold를 실제 production 코드로 채우기 시작.**

---

## §1 — 정체성 정정 (중요)

- 이 repo의 해커톤은 이제 **Arize 트랙 단독**. Qdrant VSD는 별도 프로젝트 **memex**로 이관됨(2026-05-20).
- README/docs의 dual-claim("two viewports for Qdrant + Rapid Agent", "Qdrant 42-52%", "Qdrant VSD is primary")는 **Arize 단독으로 재서술 대상**.
- 단 **dual-rubric variance는 *기능*으로 유지**: 같은 제출에 서로 다른 룰을 적용해 정당한 rubric-aware 점수 차이를 보이는 시연(공정성 증명).

---

## §2 — 잠긴 결정 6건 (docs/ 보다 우선, 사용자 승인 완료 2026-05-21)

1. **스코어링 = 공식 룰**: 4개 균등 25%씩 — ① Technological Implementation ② Design ③ Potential Impact ④ Quality of the Idea. 타이브레이크 = **나열 순서**(Tech→Design→Impact→Idea) 후 심사위원 투표. ⚠️ 미션의 "Tech40/Inn30/Imp20/Pres10"은 **틀림** — RubricSynthesizer는 25/25/25/25 + 순서 타이브레이크를 산출해야 함. (함의: Design 25% + Idea 25% → 시각적 와우 + 참신성이 Tech와 동급 비중.)
2. **AI = Gemini/Google 전용** (룰: "그 외 모든 AI 도구 불허"). 모든 생성=Vertex Gemini; Phoenix LLM-as-judge 모델=Gemini; 임베딩=Vertex; sparse=통계 BM25(rank-bm25, 신경망 아님). **프로덕션에 OpenAI/Anthropic 금지** (`spikes/uv.lock`엔 pydantic-ai extras로 딸려있음 — 절대 ship 안 함).
3. **오케스트레이터 = Google ADK** (LangGraph 아님). Arize가 허용하는 code-owned 런타임, 스타터킷도 ADK.
4. **Qdrant 제거.** → Vertex 임베딩 + **in-code hybrid retrieval**: dense 코사인 + rank-bm25 sparse + RRF 융합; weight-aware anchor = past_evals를 `rubric_schema_hash`로 필터 후 `weights_vector` 코사인; recommendation(anti-pattern anchor)=최근접 코사인; 3D constellation=Vertex 임베딩에 PCA/UMAP. 6 "컬렉션"(pitch_chunks, repo_chunks, techniques, bmad_criteria, past_evals, web_evidence)은 **Firestore + 인메모리 인덱스**로. 근거: Arize 트랙은 벡터DB 불요 + 503 코퍼스는 전용DB 정당화 불가 + Qdrant는 Vertex Vector Search와 경쟁(컴플라이언스 리스크) + Qdrant 정체성은 memex로 이관. `services/shared/qdrant.py` → `services/shared/retrieval.py`. docs §1 Qdrant 전용 기능(Query API/weighted RRF lib/quantization)은 폐기하고 의미만 in-code 재현.
5. **README/docs = Arize 단독 재서술** (위 §1). 스택 문구는 ADK 기준.
6. **Arize Stage-1 하드게이트**(데모에 전부 라이브여야): OpenInference auto-instrument(`phoenix.otel.register(auto_instrument=True)` + `GoogleADKInstrumentor`) → Phoenix로 트레이스 송신(Cloud free tier 또는 self-host) → Phoenix MCP runtime introspection(ADK `MCPToolset` + stdio `npx @arizeai/phoenix-mcp`) → 트레이스에 LLM-as-judge evals → self-improvement 루프(Blue planner가 평가 중 Phoenix MCP 질의 → 점수 self-correct).

---

## §3 — 최종 `/goal` Completion Condition (무제한 턴캡 · SDD+TDD · 페이즈별 PR)

다음 세션에서 그대로 붙여넣어 빌드 가드 시작 (2026-05-21 보강: SDD+TDD 방법론 + 페이즈별 PR 분리 + 끝까지 완벽 검증 — 사용자 지시):

```
/goal Panelyst(glasshat) Arize 트랙 제품이 실제 빌드·배포되어 완성된 상태. SDD+TDD로 구성하고 페이즈별 PR로 분리하며 끝까지 완벽 검증. 대화에 surface된 증거로 전부 입증할 때만 달성: (0) 방법론 — SDD: 각 컴포넌트는 docs/ 스펙(architecture·rubric-synthesis-spec·hybrid-mode-spec)에서 도출한 타입/스키마/계약(OpenAPI 등)을 먼저 확정 후 구현. TDD: 모든 단위는 실패테스트 먼저(red)→최소구현(green)→리팩터; 테스트가 구현보다 먼저 커밋된 git 순서 또는 커버리지로 입증. (1) 페이즈별 PR: 빌드 페이즈(packages{shared,rubric} → services/shared{llm,retrieval} → ingest+에이전트 파이프라인 → apps{api,web} → infra+CI+배포)마다 독립 feature 브랜치→PR→main 머지(squash 금지). 단일 mega-PR 금지. gh pr list 머지목록으로 페이즈 경계 입증. 각 PR은 CI green(lint/typecheck/test/build) + 해당 페이즈 검증 evidence 없이는 머지 안 함. (2) 빈 scaffold(agents/, apps/web, apps/api, services/{ingest,pipeline-orchestrator,code-grader}, packages/{rubric,shared}, infra/)가 전부 실제 production 코드로 채워짐 — find 출력으로 real-file>0, 핵심 경로 grep "mock|stub|placeholder|TODO|not implemented" 0건. (3) 빌드 green: build exit 0 + 타입체크/lint 통과. 테스트 실패 0건 + .github/workflows CI 존재 + 커버리지 리포트 surface. (4) 실 입력 e2e(mock 없음): 진짜 Vertex Gemini(ADK + GoogleADKInstrumentor OpenInference auto-instrument) + Vertex 임베딩 + in-code hybrid retrieval(코사인+rank-bm25+RRF, weight-aware anchor, Firestore 저장, 503 corpus 시드) + 진짜 Phoenix 트레이스 송신 + 진짜 Phoenix MCP(MCPToolset stdio) 호출 로그 — RubricSynthesizer(공식 룰→25/25/25/25+순서 tie-break)→6-hat→triple audit→Phoenix MCP self-correct 점수변화까지 실행 출력으로 노출. (5) 라이브 배포: Cloud Run(project panelyst-hackathon, us-central1, min=0) URL curl HTTP 200, /judge·/participate 두 뷰포트 응답. (6) 3D self-correction: SSE로 6-hat 점수 self-correct + 3D 그래프(PCA/UMAP) 재형성이 실제 파이프라인 출력으로 구동됨을 로그/스크린샷으로 surface. (7) 최종 완벽 검증: 전체 e2e 재실행 통과 + 모든 페이즈 PR 머지 + CI green + 배포 200 동시 입증. README Arize 단독 재서술(Qdrant dual-claim 제거, dual-rubric variance 기능 유지) + 배포 링크 + 재현 가이드. 제약: AI는 Gemini/Google 전용(OpenAI/Anthropic 금지); Qdrant 미사용(Vertex+in-code); 오케스트레이터=ADK; GCP=[REDACTED-EMAIL]/billing 크레딧계정; 프로덕션 서버·타 프로젝트 미관여; .env 사용자 확인없이 수정금지(Secret Manager); 잠근 결정(스코어링·Qdrant제거·Google전용AI·ADK) 우선; mock/stub 금지; feature 브랜치+squash 금지; 시작 전 git pull. 데모영상 녹화 제외.
```

---

## §4 — 공식 룰 핵심 (권위, 2026-05-21 fetch)

전체 원문: `claudedocs/hackathon-source-2026-05-21/` (00-INDEX부터).

- **마감**: 2026-06-11 14:00 PT. 콘테스트 기간 2026-05-05~06-11. 심사 06-22~07-06. 수상 통보 후 영업일 2일 내 응답.
- **신규성**: 콘테스트 기간 내 신규 원작(first commit 2026-05-13 ✓).
- **플랫폼**: web/Android/iOS 중 하나 (Next.js 웹 ✓).
- **제출물**: 호스팅 URL(테스트 가능) + 텍스트 설명 + public OSS repo(OSI 라이선스 repo 상단 노출, Apache-2.0 ok) + ≤3분 데모영상(YouTube/Vimeo, 영어 또는 영어자막, 3rd-party 로고/광고 금지).
- **필수 스택**: Gemini + Google Cloud Agent Builder + 파트너 MCP 서버. Arize 트랙: code-owned 런타임(ADK/Cloud Run/Gemini CLI/Agent Runtime/Gemini Enterprise SDK).
- 🔴 **경쟁 제한**: "Google Cloud(클라우드 플랫폼 역량) 또는 선택 파트너와 직접 경쟁하는 서비스 금지" + "Google Cloud AI / 파트너 내장 AI만, 그 외 모든 AI 도구 불허." → 결정 §2-2, §2-4로 대응 완료(Qdrant 제거, Gemini 전용).
- **팀**: 최대 4명. 한 제출은 최대 1개 상.
- **상금/트랙**: 1st $5k / 2nd $3k / 3rd $2k.
- **미캡처**: FAQ(`/details/faq`)는 JS 렌더링이라 본문 미확보 — Qdrant/경쟁툴 추가 클라리피케이션 필요 시 Discord(discord.gg/7Dqk5ebCD4)/forum/이메일(ryoung@arize.com)로 확인.

---

## §5 — Arize 기술 와이어링 (스타터킷 기준)

- 스타터킷: `github.com/Arize-ai/gemini-hackathon` (Apache-2.0, ADK + `phoenix.otel.register(auto_instrument=True)`).
- 인스트루멘터: `openinference-instrumentation-google-adk`(`GoogleADKInstrumentor`), `-google-genai`(`GoogleGenAIInstrumentor`, Gemini+Vertex 둘 다), `-vertexai`(`VertexAIInstrumentor`).
- 신 `google-genai` SDK 사용: `genai.Client(vertexai=True)`. 구 `vertexai` SDK(google-cloud-aiplatform)는 **2026-06-24 제거**. 인스트루멘테이션은 `google.genai` import 전에 register. Vertex는 IAM/ADC 인증(API key 아님).
- Phoenix MCP: `npx -y @arizeai/phoenix-mcp@latest --baseUrl <url> --apiKey <key>` (stdio). ADK는 `MCPToolset(connection_params=StdioConnectionParams(server_params=mcp.StdioServerParameters(...)))` (spike C에서 검증한 2단계 wrap).
- 환경변수: `PHOENIX_API_KEY`, `PHOENIX_COLLECTOR_ENDPOINT`, `PHOENIX_PROJECT_NAME`.

---

## §6 — 환경 / 배포 타깃

| 자원 | 값 |
|---|---|
| GCP 활성 계정 | `[REDACTED-EMAIL]` |
| 프로젝트 | `panelyst-hackathon` |
| 리전 | `us-central1` |
| 결제 | `[REDACTED-BILLING-ID]` ("크레딧계정", open, 연결됨) |
| ADC | 이 머신엔 존재 (`~/.config/gcloud/application_default_credentials.json`) |
| 활성 API | run, aiplatform(Vertex), artifactregistry, cloudbuild, secretmanager |
| 배포 | Cloud Run, `min-instances=0` |

**다른 컴퓨터에서 해야 할 환경 셋업** (git으로 안 옴):
- `gcloud auth login` + `gcloud auth application-default login` (계정 [REDACTED-EMAIL]), `gcloud config set project panelyst-hackathon`.
- `.env`는 gitignored — `.env.example` 기준으로 재생성, secret은 Secret Manager.
- Phoenix Cloud(app.phoenix.arize.com) 가입 + API key (또는 self-host).
- `spikes/.venv`는 uv-managed, 머신 로컬 — 새 머신에선 `uv sync` 재생성.

---

## §7 — 현재 빌드 상태

- **제품 코드 0**: agents/ · apps/{web,api} · services/{code-grader,ingest,pipeline-orchestrator} · packages/{rubric,shared} · infra/ 전부 `.gitkeep`+README만.
- **설계 완료**: docs/ ~250KB (max-wins-plan, technical-apex-features, wow-moment-design, rubric-synthesis-spec, hybrid-mode-spec, architecture, spike-results 등).
- **7 spike 전부 PASS**: `spikes/01~07` + `spikes/results/*.json`. ADK MCPToolset 정확 와이어링 검증됨.
- **클릭형 프로토타입 v0.2 live**: `mockups/index.html` (OKLCH + bento + Three.js 3D constellation + spring motion).
- **코퍼스**: `data/devpost-gemini3/` (Gemini 3 Devpost 데이터셋, calibration corpus 시드용).

---

## §8 — 다음 세션 빌드 순서 (권장)

> **방법론 (2026-05-21 추가, 사용자 지시)**: 각 페이즈 = 독립 feature 브랜치 → PR → main 머지(squash 금지, mega-PR 금지). 모든 컴포넌트는 **SDD**(docs/ 스펙 → 타입·계약 먼저) + **TDD**(실패테스트 red → green → refactor; 테스트가 구현보다 먼저 커밋). 각 PR은 CI green + 페이즈 검증 evidence 없이는 머지 금지. 마지막에 전체 e2e 재실행으로 완벽 검증.

1. `git pull` → 페이즈별 feature 브랜치 생성 (예: `feat/arize-packages`, `feat/arize-services-shared`, `feat/arize-ingest-agents`, `feat/arize-apps`, `feat/arize-infra-deploy`).
2. `docs/` 정독(특히 architecture, technical-apex-features §2/§4/§6, rubric-synthesis-spec, wow-moment-design) + 본 핸드오프 §2 잠긴 결정 반영.
3. `packages/shared`(공용 타입/스키마) → `packages/rubric`(BMAD vocab + SynthesizedRubric 스키마, **25/25/25/25**).
4. `services/shared/llm.py`(Vertex Gemini 어댑터 + OpenInference span) + `services/shared/retrieval.py`(Vertex 임베딩 + in-code hybrid + weight-aware anchor; **Qdrant 아님**).
5. `services/ingest`(PDF 덱 + repo + 룰 파싱) → RubricSynthesizer agent → 6-hat ADK 패널 → triple audit → Phoenix MCP self-improvement(Blue).
6. `apps/api`(파이프라인 API + SSE) → `apps/web`(Next.js, mockups 미감 실현, 3D self-correction).
7. `infra/`(Dockerfile, Cloud Run) + `.github/workflows`(lint/typecheck/test/build) → 배포 → e2e 검증 → README Arize 단독 재서술.
8. 각 컴포넌트 완료 시 evidence(실행로그/스크린샷/배포URL)와 함께 보고. 충돌·트레이드오프는 진행 전 질문.

---

## §9 — 원문 캡처 인덱스 (claudedocs/hackathon-source-2026-05-21/)

`00-INDEX.md` · `01-overview.md` · `02-rules.md` · `03-arize-resources.md` · `04-resources.md` · `05-gemini-hackathon-starterkit.md` · `06-phoenix-mcp-server.md` · `07-vertex-ai-gemini-tracing.md` · `08-openinference-google-packages.md` · `09-phoenix-llm-evals.md` · `10-faq-NOT-CAPTURED.md`

> 주의: WebFetch 마크다운 추출본(raw HTML 아님). 법적 룰 원문은 제출 전 라이브 페이지 재확인.

---

## §10 — 정직한 수상 가능성 평가 (사용자 질문에 대한 답)

**"완벽하게 수상 가능성 확보"는 아직 아님.** 확보한 것은 *강한 계획·컴플라이언스 정렬*이고, 미확보는 *작동하는 제품 그 자체*다.

✅ 확보됨:
- 룰/리소스 정확 학습 + 최대 실격 리스크(경쟁 클로즈) 제거(Qdrant→Vertex/in-code, Gemini 전용).
- 스코어링 정정으로 전략 정렬: Design 25% + Idea 25% → 시각적 와우 + 참신성 투자 정당화.
- GCP 배포 타깃 검증, Arize 게이트 전부 spike로 검증됨, 설계 완비.

❌ 미확보 (전부 다음 세션 이후):
- **제품 코드 100% 미작성** (빈 scaffold). 배포·e2e·데모영상 0.
- 와우 모먼트가 실제 파이프라인으로 구동되는지 미입증(현재 mockup만).
- "세상 바꿀 아이디어" 품질은 주관적 + 경쟁(8,702 등록, Arize 트랙 서브셋).

**결론**: 우승은 *보장 불가*(실행 품질·심사·경쟁에 좌우). 지금까지 한 일은 우승 *확률을 최대화하는 토대*를 깔고 가장 큰 지뢰를 제거한 것. 진짜 승부는 **빌드+배포+작동 입증**에서 난다.

---

작성: 2026-05-21 · 다음 세션: `cd ~/Documents/GitHub/glasshat && git pull && /handon` (또는 §3의 `/goal` 붙여넣기).
