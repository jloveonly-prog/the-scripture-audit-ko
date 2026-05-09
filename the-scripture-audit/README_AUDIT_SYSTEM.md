# 🏛️ THE SCRIPTURE AUDIT SYSTEM
**"Search the scriptures" — John 5:39 KJV**

> **버전**: BVCAP v1.5 + AIDD Unified v2.4
> **상태**: FULLY OPERATIONAL
> **핵심 철학**: AI는 주석서를 검색하지 않는다. 원문을 분해하고, 숫자를 역산하고, 체인을 완성한다.
> **BVCAP = BALANCE(저울)** — *"Thou art weighed in the balances"* Dan 5:27

---

## 🗺️ 폴더 구조 (Architecture Overview)

```
the-scripture-audit/
│
├── 📋 README_AUDIT_SYSTEM.md        ← 지금 이 문서 (시스템 전체 지도)
├── ⚖️  BVCAP_1.0.md                  ← BALANCE 검증 기준 (루트 — 판결 양식)
├── 🧠 BVCAP_Skill_Pipeline.md       ← 전체 파이프라인 상세 참조 (루트)
│
├── 🕊️  CALLING(소명)/                ← [1단계] 자세 준비 — 페르소나 + 철학 주입
│   ├── Persona_Scribe42.md          (나는 누구인가 — 42 기록자 + 철학 주입)
│   ├── OVERRIDE_AcademicBias.md     (학계 통설 → H0 격리 선언)
│   └── AIDD_AgentDirectives.md      (에이전트 기본 수칙)
│
├── 📖 DOCTRINE(교훈)/               ← [2단계] 전술 훈련 — 무기를 쓰기 전 익혀야 할 규칙
│   │  "He teacheth my hands to war" — Psalm 18:34
│   ├── ARMOUR_Bearer.md          (전투 실행 순서도 — 어떤 순서로 무기를 쓰는가)
│   ├── ANCHOR_ThirdData.md          (제3 앵커 수집 규칙 — 역산의 열쇠)
│   ├── DEOVERLAP_Serial.md          (중첩 해체 + 직렬화 규칙)
│   ├── GATE_Index.md          (충돌 유형 분류 규칙 + 레퍼런스 인덱스)
│   └── ANALOGY_Modern.md            (비유 창작법 — 1초 이해 달성 기술)
│
├── 📚 CHRONICLE(전례)/              ← [3단계] 시청각 교육 — 과거 전투 기록
│   ├── [A]_아하지야_42vs22.md       ← 연대기 직렬 역산 전례
│   ├── [A]_데라_아브람출생.md
│   ├── [B]_사울_다마스쿠스.md       ← 순차 병렬 통합 전례
│   ├── [B]_무덤사건_부활아침_순차통합.md ← 🏆 S등급 전례 (4복음서 다중 인물 분기 최고 복잡도)
│   ├── [B+E]_고난주간_타임라인.md
│   ├── [C]_솔로몬_외양간_4만vs4천.md ← 기능 범주 분리 전례
│   ├── [D+G]_팀나_족보난제.md
│   ├── [E]_목요일십자가설.md
│   ├── [F+E]_베드로_갈보리순교설.md
│   ├── [G+H+I]_요한1서_콤마.md      ← 복합 TYPE 최고 수준 전례
│   ├── [I+F]_창세기1장.md
│   ├── [I+D]_마태복음1장_14세대.md
│   ├── [J]_도마_신라전래설.md
│   └── [O+P+Q]_천년왕국_리틀시즌.md ⭐ NEW (과거 성취론 3중 무기 방어 표준 전례)
│
├── 🏹 QUIVER(무기고)/               ← [4단계] 전쟁터에 들고 가는 무기만 (TYPE 17개)
│   ├── TYPE-A_Chronological.md      (연대기 직렬 역산)
│   ├── TYPE-B_Sequential.md         (사건 순차 병렬 통합)
│   ├── TYPE-C_Functional.md         (기능적 범주 분리)
│   ├── TYPE-D_Hebrew.md             (히브리 서사 관습 역이용)
│   ├── TYPE-E_Competing.md          (경쟁 모델 전수 기각)
│   ├── TYPE-F_Typology.md           (예표 삼중 평행 구조 증명)
│   ├── TYPE-G_Grammar.md            (KJV 접속사/문법 구조 해부)
│   ├── TYPE-H_Manuscript.md         (사본학적 증거 독립성 역전)
│   ├── TYPE-I_Frequency.md          (어휘 빈도 대칭 설계 검증)
│   ├── TYPE-J_History.md            (외부 역사 문헌 교차 검증)
│   ├── TYPE-K_Science.md            (과학적·법의학적 정합 검증)
│   ├── TYPE-L_Chain.md              (귀납적 연쇄 추론 — 체인 완성)
│   ├── TYPE-M_SUSPECT.md            (의심 감지 + 서브모듈 TYPE-M-ξ 포함)
│   ├── TYPE-N_Exclusivity.md        (배타성 전수 조사)
│   ├── TYPE-O_PhysicalMarker.md     ⭐ NEW (물리적 흔적 부재 검증)
│   ├── TYPE-P_Retorsion.md          ⭐ NEW (역논법 / 부메랑 논증)
│   ├── TYPE-Q_LanguageQuantifier.md ⭐ NEW (성경적 언어 수량화 제약)
│   ├── TYPE-R_SyntaxConfusion.md    ⭐ NEW (구문/주어 혼동 적발)
│   └── TYPE-T_TenseAndLexical.md    ⭐ NEW (시제 및 어휘 오독 적발)
│
├── 📥 INBOX(공격목록)/              ← [입력] 해결할 성경 공격 목록
│   ├── Bible_Defense_List.md        (30가지 난제 + TYPE 매핑)
│   └── Shabir_Ally_101_Contradictions.md (이슬람 101가지 모순 공격)
│
└── 📁 VERDICT(판결록)/             ← [출력] 완성된 감사 보고서 저장소
    └── (VERDICT_[난제명].md 포맷으로 저장)
```

---

## 🔑 6단계 철학 — 폴더 역할 한눈에

| 단계 | 폴더 | 역할 | KJV 근거 |
|:---:|:---|:---|:---|
| **1** | `CALLING(소명)` | 자세 준비 — 42 기록자 페르소나 + 철학 주입 | "the holy calling" 딤후 1:9 |
| **2** | `DOCTRINE(교훈)` | 전술 훈련 — 무기 사용 전 규칙/프로토콜 숙지 | "He teacheth my hands to war" 시 18:34 |
| **3** | `CHRONICLE(전례)` | 시청각 교육 — 과거 전투 기록으로 실전 감각 | "the book of the chronicles" 왕하 |
| **4** | `QUIVER(무기고)` | 실전 무기만 — TYPE-A~N (14개), 전쟁터에 들고 참전 | "His quiver" 시 127:5 |
| **입력** | `INBOX(공격목록)` | 해결할 성경 공격 목록 대기 | — |
| **출력** | `VERDICT(판결록)` | 완성된 판결 보고서 저장 | "weighed in the balances" 단 5:27 |

---

## ⚖️ BVCAP = BALANCE (저울) — 검증 시스템의 위치

> **BVCAP은 TYPE과 다르다.**
> - `TYPE-A~N` = **무기** (싸우는 도구, QUIVER에 보관)
> - `BVCAP` = **저울** (싸운 결과를 계량하는 검증 시스템, 루트에 위치)

BVCAP은 TYPE 무기들이 도출한 결과를 받아 ✅ / ⚠️ / ❌ 판결을 내린다.
그래서 BVCAP 파일들은 어떤 폴더 안에도 속하지 않고 **루트에 위치**한다.

---

## 🚀 사용 방법 (How to Use)

### 📌 방법 1: 빠른 단발 공격 방어

```
"[난제 내용]을 검증해줘.
1. CALLING(소명)/Persona_Scribe42.md — 페르소나 장착
2. DOCTRINE(교훈)/ARMOUR_Bearer.md — 전투 순서 확인
3. CHRONICLE(전례)/에서 동일 TYPE 전례 확인
4. QUIVER(무기고)/TYPE-X.md — 해당 무기로 분석 실행
5. BVCAP_1.0.md — BALANCE 검증 후 판결 선고
완료 후 VERDICT(판결록)/에 마스터피스 양식으로 저장해."
```

**예시:**
> "INBOX의 Shabir Ally 공격 중 Q01(다윗 인구조사)을 검증해줘.
> QUIVER/ARMOUR_Bearer.md 파이프라인을 따르고,
> VERDICT/VERDICT_Q01_다윗인구조사.md로 저장해."

---

### 📌 방법 2: 특정 무기(TYPE) 지정 방어

`INBOX/Bible_Defense_List.md`에서 TYPE이 매핑된 항목은 직접 지정 가능.

```
"[난제]를 TYPE-[X] 무기로 검증해줘.
QUIVER/TYPE-[X]_[이름].md 절차를 따르고,
CHRONICLE/[X]_[유사난제].md를 품질 기준으로 참고해서
VERDICT/에 마스터피스 보고서로 저장해."
```

**예시 (숫자 충돌):**
> "아하지야 22세 vs 42세 난제를 TYPE-A 무기로 검증해줘.
> `QUIVER/TYPE-A_Chronological.md` 절차를 따르고,
> `CHRONICLE/[A]_아하지야_42vs22.md`를 품질 기준으로 참고해."

**예시 (사본 공격):**
> "요한1서 5:7 콤마 구절 삭제 공격을 TYPE-G+H+I 복합 무기로 검증해줘.
> `CHRONICLE/[G+H+I]_요한1서_콤마.md`를 품질 기준으로 참고해."

---

### 📌 방법 3: 전수 배치 실행 (Shabir Ally 101 도장 깨기)

```
"INBOX/Shabir_Ally_101_Contradictions.md를 열어서
체크박스가 비어있는 항목을 순서대로 하나씩 검증해줘.
각 항목마다 QUIVER/ARMOUR_Bearer.md 파이프라인을 실행하고
VERDICT/ 폴더에 개별 보고서로 저장해. 완료 항목은 [x]로 표시해."
```

---

## ⚡ 에이전트 내부 실행 흐름

```
[공격 접수]
INBOX/ → Bible_Defense_List or Shabir_Ally_101
    ↓
[CALLING 장착] — Persona_Scribe42.md + OVERRIDE_AcademicBias.md
  → "나는 42 기록자다. 학계 통설은 H0으로 격리한다."
    ↓
[QUIVER 실행] — ARMOUR_Bearer.md 순서도 따라
  SUSPECT_Anomaly  → "왜 이것만 다른가?" 의심 감지
  ANCHOR_ThirdData → 제3 앵커 구절 수집
  DEOVERLAP_Serial → 직렬 배치 + 매트릭스 역산
    ↓
[FULL SCAN] — TYPE-A ~ TYPE-N 전수 실행
  발동된 TYPE → 메모리 보관
  미발동 TYPE → 스킵
    ↓
[CHRONICLE 참조] — 동일 TYPE 완성 전례 열어 품질 기준 확인
    ↓
[BVCAP 검증] — BALANCE(저울)로 결과 계량
  TYPE-L  → 발동 TYPE들 연쇄 체인 구성
  ANALOGY → 현대 비유 생성 (1초 이해)
  BVCAP_OutputFormat → 5단계 양식 적용
    ↓
[판결 선고]
✅ CONSISTENT / ⚠️ UNRESOLVED / ❌ CONTRADICTION
    ↓
[저장]
VERDICT/VERDICT_[난제명].md
```

---

## 📊 무기(TYPE) 빠른 참조 맵

| 무기 | 이름 | 발동 조건 |
|:---:|:---|:---|
| **TYPE-M** | 의심 감지 (SUSPECT) | 항상 첫 번째 — "왜 이것만 다른가?" |
| **TYPE-M-ξ** | 해석 기준 일관성 검사 | TYPE-M 서브모듈 — 물리/영적 이중 잣대 혼용 탐지 |
| **ANCHOR** | 제3 앵커 수집 | 항상 두 번째 — 충돌 구절 외 독립 데이터 확보 |
| **DE-OVERLAP** | 중첩 해체 | 항상 세 번째 — 직렬 배치 후 역산 시작 |
| **TYPE-A** | 연대기 직렬 역산 | 숫자/나이/기간 충돌 |
| **TYPE-B** | 사건 순차 통합 | 두 기록이 정반대 묘사 |
| **TYPE-B-ψ** | 심리적 시간차 | 동일 인물의 감정 변화로 행동이 달라진 경우 |
| **TYPE-B-μ** | 미시 자세 변화 | 동일 장면 내 초 단위 상태 변화 (서있음→앉음 등) |
| **TYPE-B-π** | 지각 필터 | 증인이 봤으나 심리적으로 처리 불가한 경우 |
| **TYPE-C** | 기능적 범주 분리 | 동일 단어 숫자가 배수 차이 |
| **TYPE-D** | 히브리 관습 역이용 | 족보 순서/인물 호칭 충돌 |
| **TYPE-E** | 경쟁 모델 전수 기각 | 여러 해석이 경쟁하는 난제 |
| **TYPE-F** | 예표 삼중 구조 증명 | 인물 사명/장소 전승 충돌 |
| **TYPE-G** | KJV 문법 구조 해부 | 구절 삭제 공격 |
| **TYPE-H** | 사본 독립성 역전 | "사본이 많은 쪽이 옳다" 공격 |
| **TYPE-I** | 어휘 빈도 대칭 검증 | 단어 반복 횟수·단어 수 패턴 |
| **TYPE-J** | 외부 역사 문헌 교차 | 역사성 공격 |
| **TYPE-K** | 과학·법의학 정합 | "과학적으로 불가능" 공격 |
| **TYPE-L** | 귀납적 연쇄 추론 | 항상 마지막 — 체인 완성 |
| **TYPE-N** | 배타성 전수 조사 | TYPE-M 감지 후 발동 |
| **TYPE-O** ⭐ | 물리적 흔적 부재 검증 | "X가 과거에 성취됐다" 주장 방어 — 현재 흔적 역추적 |
| **TYPE-P** | 역논법 / 부메랑 논증 | "예수님이 마귀라면 즉사 율법이 적용되어야 한다" |
| **TYPE-Q** | 성경적 언어 수량화 제약 | (ex. 무장 해제된 영적 존재 수량 파악 불가) |
| **TYPE-R** | 구문/주어 혼동 적발 | "thine enemy" = 하나님이 원수되심 (주어 오독 적발) |
| **TYPE-T** | 시제 및 어휘 오독 적발 | "disquieted" = 시제(과거완료)와 의미(안식 방해) 오독 적발 |
| **IMPORT-X** | 외부 데이터 이식 | 이미지·엑셀 → BVCAP 타임라인 변환 |
| **ANALOGY** | 현대 비유 창작 | 항상 출력 직전 — 1초 이해 달성 |
| **BVCAP_1.0** | 최종 BALANCE 검증 | 루트의 `BVCAP_1.0.md` — 판결 양식 기준 |
