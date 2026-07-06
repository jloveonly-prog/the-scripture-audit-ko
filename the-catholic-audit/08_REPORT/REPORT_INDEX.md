# 📁 CVCAP 마스터피스 보고서 인덱스
## — Track 1 (성경 법정) + Track 2 (문헌 법정) 전과 기록 —

> **STATUS**: CVCAP 2.0 자동화 파이프라인 가동 중 | **엔진**: CVCAP 2.0 (Dual-Track + Doctrine DB 자동 탐지)
> **작전 목표**: 가톨릭 교도권·무류성의 내부 붕괴(Implosion) 확정

---

## 🆕 현재 가동 중인 산출물 (CVCAP 2.0 — 05_DOCTRINE_DB 기반 자동 탐지)

> 아래는 `05_DOCTRINE_DB/`(80개 교리 카드)를 입력으로 `scripts/conflict_detector.py`가 자동 색인하고,
> 사람이 종합 정리한 **현재 활성 보고서**입니다. 아래 "3차전 작전 지도"(CVCAP 1.0 시기 수작업 전투 기록)보다 최신입니다.

| 산출물 | 위치 | 내용 | 상태 |
|:---|:---|:---|:---:|
| 종합 감사 보고서 | [catholic_error_report.md](./catholic_error_report.md) | 구원론·무류성·성사론 등 6개 주제 심층 분석 + 부록(자동 탐지 매뉴얼) | ✅ 최신 |
| 자동 탐지 결과 (필터 통과) | [auto_conflict_results.csv](./auto_conflict_results.csv) | Cross-claim 재확인 필터를 통과한 충돌 후보 49건 | ✅ 최신 |
| 자동 탐지 제외 사례 (투명성 공개) | [auto_conflict_excluded_self_negation.csv](./auto_conflict_excluded_self_negation.csv) | 오탐(사실상 동일 입장)으로 판정되어 제외된 18건 | ✅ 최신 |
| 충돌 네트워크 시각화 | [conflict_network.html](./conflict_network.html) | Vis.js 기반 인터랙티브 그래프 (Chrome으로 열기) | ✅ 최신 |
| 확정 콜리전 카드 | [`../06_COLLISION_CARDS/confirmed/`](../06_COLLISION_CARDS/confirmed/) | COL-001~008, 수작업 정밀 검증 완료 | ✅ 최신 |
| 제로데이 스캔 후보 | [`../07_ZERO_DAY/scan_targets.md`](../07_ZERO_DAY/scan_targets.md) | 향후 우선 탐색 대상 (Fiducia Supplicans 등) | 🔄 진행 중 |

> ⚠️ **탐지기 한계 안내**: char n-gram 기반 유사도 탐지는 부정어를 완전히 구분하지 못합니다. `auto_conflict_results.csv`의 49건도 "사람의 신학적 재검토가 필요한 1차 후보"이며, 최종 확정 판단은 `06_COLLISION_CARDS/confirmed/`처럼 수작업 검증을 거친 카드를 우선 신뢰하십시오. 자세한 내용은 `catholic_error_report.md` 부록 §1 참조.

---

## 🗄️ 이하는 CVCAP 1.0 시기(2026-07-05) 수작업 전투 기록 — 역사적 참고용 (Archived)

> 아래 "3차전 작전 지도"는 `05_DOCTRINE_DB` 자동화 파이프라인 도입 **이전**, CVCAP 1.0 단계에서 실전 댓글 논쟁을 분석하며 작성된 기록입니다. 실전 화법·논증 패턴 참고 자료로는 여전히 유효하지만, 현재 진행 상황을 반영하지는 않습니다.

---

## 🗺️ 보고서 전략 지도

```
[1차전] 기초 포격 — 성경 원문으로 가톨릭 교리 타격
[2차전] 교부 전선 — 피격 후 반격 준비 (요 6:63 미사용 확인)
[3차전] 내부 붕괴 — 가톨릭 문헌으로 가톨릭을 법정에 세움  ← 현재 위치
```

---

## ✅ Track 1: 성경 법정 (BVCAP) — 완성 보고서

> 위치: `../../the-scripture-audit/05_REPORT(전과보고서)/catholic/`

| # | 파일명 | 주제 | 핵심 타격 포인트 | 상태 |
|:---:|:---|:---|:---|:---:|
| 1 | [REPORT_가톨릭이_예수님을_구원자로_시인하지_못하는_이유.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_가톨릭이_예수님을_구원자로_시인하지_못하는_이유.md) | 구원론 핵심 질문 | "예/아니오" 함정 — 어느 쪽 선택해도 가톨릭 구원론 붕괴 | ✅ 완성 |
| 2 | [REPORT_가톨릭이_예수님을_구원자로_시인하지_못하는_이유_노트북LM용.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_가톨릭이_예수님을_구원자로_시인하지_못하는_이유_노트북LM용.md) | 구원론 (영상용) | 위 문서의 영상 스크립트 최적화본 | ✅ 영상 준비 |
| 3 | [REPORT_가톨릭_3대탈출구_봉쇄_SolaScriptura.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_가톨릭_3대탈출구_봉쇄_SolaScriptura.md) | Sola Scriptura | 성경+전통 이중권위 / ex cathedra / 예방적 구원 3대 탈출구 완전 봉쇄 | ✅ 완성 |
| 4 | [REPORT_교황수위권_베드로반석_오류감사.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_교황수위권_베드로반석_오류감사.md) | 교황 수위권 | 마 16:18 "반석" = 베드로인가? 원어 Petros vs Petra 구분 | ✅ 완성 |
| 5 | [REPORT_마리아_무염시태_승천_오류감사.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_마리아_무염시태_승천_오류감사.md) | 마리아 도그마 | 눅 2:22 정결 예식 결정타 / 성경 근거 전무 | ✅ 완성 |
| 6 | [REPORT_사도계승_역사전승_오류감사.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_사도계승_역사전승_오류감사.md) | 사도 계승 | 역사적 단절 증명 / 베드로 로마 주교설 타임라인 붕괴 | ✅ 완성 |
| 7 | [REPORT_카톨릭_성인전구교리_검증.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_카톨릭_성인전구교리_검증.md) | 성인 전구 | 딤전 2:5 "중보자는 오직 한 분" — 성인 전구 구조적 불가 | ✅ 완성 |
| 8 | [REPORT_유아세례_딜레마_7성사붕괴.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_유아세례_딜레마_7성사붕괴.md) | 유아세례·7성사 | 유아세례 딜레마로 7성사 연쇄 붕괴 유도 | ✅ **3차전 핵심 무기** |
| 9 | [REPORT_베드로_갈보리순교설.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_베드로_갈보리순교설.md) | 베드로 순교지 | 역사 포렌식 — 베드로 로마 순교설 검증 | ✅ 완성 |
| 10 | [REPORT_요한1서_콤마.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_요한1서_콤마.md) | 요한 콤마 | 불가타 사본 조작 의혹 — 삼위일체 구절 사본학 포렌식 | ✅ 완성 |
| 11 | [REPORT_WINE_포도주_술_진노_원어_포렌식.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_WINE_포도주_술_진노_원어_포렌식.md) | 성찬 포도주 | 화체설 vs 성경 원어 포렌식 | ✅ 완성 |
| 12 | [REPORT_카톨릭외전_대본분석.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_카톨릭외전_대본분석.md) | 외전·외경 | 외경의 정경성 주장 해체 | ✅ 완성 |

---

## ⚔️ Track 2: 문헌 법정 (QVCAP) — 실전 전투 기록

| # | 파일명 | 전투 유형 | 결과 | 3차전 교훈 |
|:---:|:---|:---|:---:|:---|
| 1 | [카톨릭_댓글.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭_댓글.md) | 실전 댓글 전투 | 기록 | 실전 패턴 분석용 |
| 2 | [카톨릭2차전.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭2차전.md) | 화체설·교부 논쟁 | ⚠️ 피격 | **요 6:63 미사용 — 3차전 반드시 선제 투입** |
| 3 | [카톨릭_법정.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭_법정.md) | 법정 모의 | 분석 | 논증 구조 참고 |
| 4 | [카톨릭_변증.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭_변증.md) | 변증 기록 | 분석 | 방어 패턴 파악용 |

---

## 🚨 3차전 최우선 타격 포인트 (미사용 무기)

> 2차전 BVCAP 감사에서 확인된 **양측 모두 회피한 결정적 구절**

### 🎯 1순위: 요한복음 6:63
```
"살리는 것은 영이니 육은 무익하니라.
 내가 너희에게 이른 말은 영이요 생명이라." (요 6:63 KJV)
```
- 53-55절의 "살(σάρξ)"과 63절의 "육(σάρξ)"이 **동일 단어**
- 화체설(물리적 살과 피)을 취하면 63절이 자기모순
- 홍군(가톨릭)이 2차전 내내 **단 한 번도 건드리지 않은 이유**: 반박 불가

### 🎯 2순위: 아우구스티누스 역체리피킹
```
요한복음 강해 25편: "그분을 믿는 것이 곧 살아있는 빵을 먹는 것이다.
                    믿는 자가 먹는다."
```
- 홍군이 설교 272번 체리피킹 지적 → 역으로 이 구절로 반격
- 같은 아우구스티누스, 같은 논리

### 🎯 3순위: 호노리우스 1세 파문 (Track 2 핵폭탄)
```
680년 제3차 콘스탄티노폴리스 공의회:
무류한 교황(호노리우스 1세)을 무류한 공의회가 이단으로 파문
→ 무류성 교리 자체가 논리적 자기모순
```

---

## 📢 3차전 공개 콘텐츠 전략

| 콘텐츠 | 기반 문서 | 형식 | 목적 |
|:---|:---|:---:|:---|
| **"가톨릭이 예수님을 구원자로 시인하지 못하는 이유"** | 노트북LM용.md | 영상 | 핵심 질문으로 시청자 주목 |
| **"유아세례 딜레마와 7성사 붕괴"** | REPORT_유아세례_딜레마 | 영상 | 가톨릭 성사 구조 전체 흔들기 |
| **"교황은 왜 무류할 수 없는가"** | CVCAP Track 2 | 문서/영상 | 무류성 내부 붕괴 선언 |

---

*Generated by CVCAP 1.0 — 3차전 작전 지도 (ARCHIVED — 역사적 참고용)*
*최초 작성: 2026-07-05 | STATUS: ARCHIVED — 최신 현황은 이 문서 상단 "현재 가동 중인 산출물" 섹션 참조*
