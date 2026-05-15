# Glasshat Prototype Review Board (2026-05-15)

10-persona panel review of `mockups/index.html` v0.2. 51+ improvement points across 10 categories.

## P0 (블로커) — 적용 필수

### A. 시작 속도 (사용자 명시 불만 "초기 시작속도 느림")
- **PERF-1**: Three.js 580KB blocking → defer + lazy load (IntersectionObserver), preload CDN
- **PERF-8**: Google Fonts 4 families × 8 weights → 2 families × 2 weights, preconnect
- **PERF-9**: preconnect for jsdelivr.net

### B. 첫 5초 와우 도착 (모든 페르소나 공통)
- **JUD-1 / DES-1**: 3D constellation을 hero card로 격상 (Tier 1) — 0초부터 visible
- **VC-1 / UX-1**: hero에 category + buyer + pain 한 문장 추가
- **DES-2**: rubric-final 24px → clamp(48px,6vw,72px) + drop-shadow glow + scale animation
- **VC-8**: 5초 안에 before/after card (LLM judge 9.2 → Glasshat 6.4)

### C. Qdrant load-bearing 가시성
- **JUD-2**: 'Qdrant Live' persistent badge + 카운터 (recommend() calls, anchors)
- **JUD-3**: 'Why -1.4?' expand panel + named real anchors (Aegis/Netra/Proofy as 실제 winners.json)

### D. 점수 보정 신뢰성 + 정직
- **VC-6**: SOC2 / EU AI Act / NIST AI RMF 명시
- **UX-12**: "numbers real, calls simulated" 정직 라벨

### E. B2B/B2C wedge 명확화
- **VC-2**: Judge mode 우세 + Participant은 free flywheel
- **VC-3**: hackathon → enterprise eval 브릿지 narration
- **VC-4**: vs Phoenix/LangSmith/Athina 차별화 한 줄

### F. 모드/CTA 라벨링
- **UX-2**: CTA를 role-based로 ('Watch as Judge', 'Watch as Participant')
- **DES-11**: viewport mode 색 시각 신호 (top border accent)

### G. 차별화 요청 사항
- **JUD-4**: trace를 OpenTelemetry waterfall 스타일로 변경
- **JUD-6**: 3D OrbitControls + hover tooltips + axis labels
- **JUD-7**: 'So what?' 다음 액션 한 줄
- **JUD-8**: Phoenix Online Eval card에 eval rule + dataset 표시

## P1 (강화)

- **PERF-2**: resize → debounced setSize (init 재실행 안 함)
- **PERF-3**: dispose geometries/materials, InstancedMesh 사용
- **PERF-4**: idleLoop visibility-gated (IntersectionObserver + visibilitychange)
- **PERF-5**: scrubber seek = snapshot 기반 (not full re-run)
- **PERF-6**: backdrop-filter selective (hero + header만), blur 20px → 12px
- **PERF-7**: scrubber-fill width → transform: scaleX (composite-only)
- **DES-3**: spacing 2-tier system
- **DES-4**: OKLCH hat colors (L=72, C=0.17, hue만 변경)
- **DES-6**: 6-step type scale
- **DES-7**: glass selective (hero + header만)
- **DES-9**: easing semantics 일관 (spring/out/in-out 의미 분리)
- **UX-3**: plain English caption 보조 모드
- **UX-4**: manual mode coachmark + scene snap
- **UX-5**: hat 라벨 'A1/A4' 코드 제거, plain criterion만
- **UX-6**: Winner Gravity 명확화 (Aegis 정체 명시)
- **UX-7**: scrubber에 scene markers + non-flicker seek
- **UX-8**: 끝에 forward CTA 추가
- **UX-10**: trace highlight (wow window)
- **UX-11**: viewport switch confirm
- **VC-5**: data moat narrative (calibration corpus 카운터)
- **VC-7**: cost meter 숨김 idle / 'zero backend wired' 제거
- **VC-9**: 'why now' 한 줄
- **VC-10**: post-demo CTAs (call/writeup/star)

## P2 (polish)

- **PERF-7**: tick 루프 DOM 캐싱 + dedupe
- **DES-5**: SVG hat-as-prism mark
- **DES-8**: radius tokens (xs/sm/md/lg/xl)
- **DES-10**: caption strip + microcopy refresh
- **UX-9**: cost ticker $0.000 → labeled
- A11Y (5명 결과 도착 후 추가)
- MO (motion designer 도착 후)
- DEM (demo director 도착 후)
- BE (backend 도착 후)
- SK (skeptic 도착 후)
