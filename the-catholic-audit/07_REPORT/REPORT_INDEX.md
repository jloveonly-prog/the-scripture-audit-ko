# 📁 CVCAP 마스터피스 보고서 인덱스
## — 문헌 법정 (가톨릭 내부 문헌 전용) 전과 기록 —

> **STATUS**: CVCAP 3.0 자동화 파이프라인 가동 중 | **엔진**: CVCAP 3.0 (내부 문헌 단일 트랙 + 자동화 계층)
> **작전 목표**: 가톨릭 교도권·무류성의 내부 붕괴(Implosion) 확정
> **최종 갱신**: 2026-07-07 (교리 DB 중복 정리 후 전체 재실행)

---

## 🆕 현재 가동 중인 산출물 (CVCAP 3.0 — 04_DOCTRINE_DB 기반 자동 탐지)

> 아래는 `04_DOCTRINE_DB/`(교리 카드 72장, 중복 정리 완료)를 입력으로 `scripts/conflict_detector.py`가
> 자동 색인하고, 사람이 종합 정리한 **현재 활성 보고서**입니다.

| 산출물 | 위치 | 내용 | 상태 |
|:---|:---|:---|:---:|
| 종합 감사 보고서 | [catholic_error_report.md](./catholic_error_report.md) | 개별 검증 완료된 **16대 모순** (구원론·무류성·성사론·마리아론·윤리 교리 등) | ✅ 최신 |
| 자동 탐지 후보 (임베딩) | [auto_conflict_results.csv](./auto_conflict_results.csv) | Sentence-Transformers 유사도 ≥0.60 + cross-claim 필터 통과 후보 **2,235건** (미확정) | ✅ 최신 |
| 자동 탐지 제외 사례 (투명성 공개) | [auto_conflict_excluded_self_negation.csv](./auto_conflict_excluded_self_negation.csv) | 오탐(동일 입장)으로 판정되어 제외된 **1,683건** (제외 사유별 구분 표기) | ✅ 최신 |
| 콤보 필터 태깅 | [cvcap_combo_results.csv](./cvcap_combo_results.csv) | CVCAP 3.0 다중 필터에 동시 적발된 **662건** (키워드 태깅 — 미확정 후보) | ✅ 최신 |
| LLM 2차 심사 (YES만) | [llm_verified_conflicts.csv](./llm_verified_conflicts.csv) | `scripts/llm_judge.py` — claude CLI 헤드리스 심사 (API 키 불필요). **984/2,232건 심사 완료, YES 21건** (수작업 재검증: 진짜 12건 → 카드 반영 / 방향 오류 오탐 9건 → 탐지기 제외 목록 등록) | 🔄 단계 진행 |
| LLM 심사 전체 로그 | [llm_judge_full_log.csv](./llm_judge_full_log.csv) | 전체 판정(YES/NO/ERROR) + 근거. **잔여 1,248건** — 사용량 한도에 맞춰 단계별 재개: `python scripts/llm_judge.py next 100` (자동으로 미심사분만 이어서 심사, 몇 번이든 반복 가능) | 🔄 단계 진행 |
| 충돌 네트워크 시각화 | [conflict_network.html](./conflict_network.html) | Vis.js 인터랙티브 그래프 — 유사도 **상위 150건** (Chrome으로 열기) | ✅ 최신 |
| 확정 콜리전 카드 | [`../05_COLLISION_CARDS/confirmed/`](../05_COLLISION_CARDS/confirmed/) | COL-001~011, 수작업 정밀 검증 완료 (009~011은 자동 탐지→LLM 심사→원문 대조 3단계 통과 신규 발굴) | ✅ 최신 |
| 후보 카드 | [`../05_COLLISION_CARDS/candidates/`](../05_COLLISION_CARDS/candidates/) | CAND-001 (교회법 844 vs 라테란4 — 실천적 모순, OODA 법정 승격 대기) | 🔄 검토 대기 |
| 콤보 카드 (확정) | [`../05_COLLISION_CARDS/combos/`](../05_COLLISION_CARDS/combos/) | COMBO-01~05 — 마리아론·무류성·구원론·연옥/대사·동성 축복 연쇄 붕괴 카드 | ✅ 최신 |
| 제로데이 스캔 후보 | [`../06_ZERO_DAY/scan_targets.md`](../06_ZERO_DAY/scan_targets.md) | 향후 우선 탐색 대상 (Fiducia Supplicans 등) | 🔄 진행 중 |

> ⚠️ **탐지기 한계 안내 (신뢰 계층)**:
> ① 임베딩 유사도는 '주제 인접'과 '논리 모순'을 완전히 구분하지 못하므로, `auto_conflict_results.csv`의
> 2,235건은 전부 **"사람/LLM의 신학적 재검토가 필요한 1차 후보"**입니다.
> ② `cvcap_combo_results.csv`의 662건은 **키워드 필터 히트 건수**이지 확정 모순 수가 아닙니다.
> ③ 최종 확정 판단은 `catholic_error_report.md`의 16대 모순, `05_COLLISION_CARDS/confirmed/`,
> `combos/`처럼 **개별 검증을 거친 카드만** 신뢰하십시오.
> ④ 초기 char n-gram 시절 자동 후보 49건 중 57%가 오탐으로 판명된 전례가 있으며(원문 대조로 확인),
> 그 교훈에 따라 같은 문서를 가리키던 중복 카드 8장을 2026-07-07 DB에서 제거했습니다 (80→72장).

---

## ⚔️ 성경 법정 (BVCAP — 별도 엔진) 연동 보고서

> CVCAP 3.0은 가톨릭 **내부 문헌만** 검증합니다. 같은 교리의 **성경 원문 검증**은
> `../../the-scripture-audit/`(BVCAP)가 담당하며, 아래 보고서들이 **최종 콘텐츠 병합 대상**입니다.
> 양측 모두 붕괴 확정 시 통합 보고서에서 🔴 CHECKMATE 선언 (→ `CVCAP_GHQ.md` 통합 인터페이스 참조).

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
| 8 | [REPORT_유아세례_딜레마_7성사붕괴.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_유아세례_딜레마_7성사붕괴.md) | 유아세례·7성사 | 유아세례 딜레마로 7성사 연쇄 붕괴 유도 | ✅ 핵심 무기 |
| 9 | [REPORT_베드로_갈보리순교설.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_베드로_갈보리순교설.md) | 베드로 순교지 | 역사 포렌식 — 베드로 로마 순교설 검증 | ✅ 완성 |
| 10 | [REPORT_요한1서_콤마.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_요한1서_콤마.md) | 요한 콤마 | 불가타 사본 조작 의혹 — 삼위일체 구절 사본학 포렌식 | ✅ 완성 |
| 11 | [REPORT_WINE_포도주_술_진노_원어_포렌식.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_WINE_포도주_술_진노_원어_포렌식.md) | 성찬 포도주 | 화체설 vs 성경 원어 포렌식 | ✅ 완성 |
| 12 | [REPORT_카톨릭외전_대본분석.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/REPORT_카톨릭외전_대본분석.md) | 외전·외경 | 외경의 정경성 주장 해체 | ✅ 완성 |

> 가톨릭 특화 성경 무기 카드: [`../03_QUIVER/CATHOLIC_TARGETED_WEAPONS.md`](../03_QUIVER/CATHOLIC_TARGETED_WEAPONS.md) (성경 법정/BVCAP 관할 — 병합 단계 전용)

---

## 🗄️ 실전 전투 기록 아카이브 (CVCAP 1.0 시기, 2026-07-05) — 역사적 참고용

> 자동화 파이프라인 도입 **이전** 실전 댓글 논쟁 기록. 실전 화법·논증 패턴 참고 자료로는 여전히 유효.

| # | 파일명 | 전투 유형 | 결과 | 교훈 |
|:---:|:---|:---|:---:|:---|
| 1 | [카톨릭_댓글.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭_댓글.md) | 실전 댓글 전투 | 기록 | 실전 패턴 분석용 |
| 2 | [카톨릭2차전.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭2차전.md) | 화체설·교부 논쟁 | ⚠️ 피격 | 요 6:63 미사용 — 이후 BVCAP 무기 카드 A로 상비화 |
| 3 | [카톨릭_법정.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭_법정.md) | 법정 모의 | 분석 | 논증 구조 참고 |
| 4 | [카톨릭_변증.md](../../the-scripture-audit/05_REPORT(전과보고서)/catholic/카톨릭_변증.md) | 변증 기록 | 분석 | 방어 패턴 파악용 |

### 🎯 상비 핵심 무기 (전투 기록에서 검증됨)
- **호노리우스 1세 파문** (문헌 법정 핵폭탄) → `03_QUIVER/QVCAP_WEAPONS.md` 파탄 카드 1
- **아우구스티누스 역체리피킹** (교부 법정) → `03_QUIVER/QVCAP_WEAPONS.md` 파탄 카드 6
- **요 6:63 sarx 동일 단어** (성경 법정 — BVCAP 관할) → `CATHOLIC_TARGETED_WEAPONS.md` 카드 A

---

## 📢 공개 콘텐츠 전략

| 콘텐츠 | 기반 문서 | 형식 | 목적 |
|:---|:---|:---:|:---|
| **"가톨릭이 예수님을 구원자로 시인하지 못하는 이유"** | BVCAP 노트북LM용.md | 영상 | 핵심 질문으로 시청자 주목 |
| **"유아세례 딜레마와 7성사 붕괴"** | BVCAP REPORT_유아세례_딜레마 | 영상 | 가톨릭 성사 구조 전체 흔들기 |
| **"교황은 왜 무류할 수 없는가"** | CVCAP catholic_error_report 7부·10부 | 문서/영상 | 무류성 내부 붕괴 선언 |
| **"16대 모순 시리즈"** | CVCAP catholic_error_report 1~16부 | 시리즈 | 내부 문헌 자가당착 전수 공개 |

---

*Generated by CVCAP 3.0 — 문헌 법정 전과 기록*
*최초 작성: 2026-07-05 | 최종 개정: 2026-07-07 (v3.0 내부 문헌 전용 전환 + DB 정리 + 전체 재실행)*
