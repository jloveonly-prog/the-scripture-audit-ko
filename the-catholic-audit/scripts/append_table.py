import csv
import re
import os

csv_path = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\auto_conflict_results.csv"
excluded_path = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\auto_conflict_excluded_self_negation.csv"
md_path = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\catholic_error_report.md"

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def build_main_table(rows):
    table = "| 유사도(Score) | A 문헌 (주장) | B 문헌 (부정) | A의 주장 원문 (Claim) | B가 단죄/부정하는 명제 (Negate) |\n"
    table += "| :--- | :--- | :--- | :--- | :--- |\n"
    for r in rows:
        score = r['Score']
        card_a = r['Card_A_Claiming']
        card_b = r['Card_B_Negating']
        claim = r['Claim_Text'].replace('\n', ' ').replace('|', 'I')
        negate = r['Negate_Text'].replace('\n', ' ').replace('|', 'I')
        table += f"| **{score}** | `{card_a}` | `{card_b}` | {claim} | {negate} |\n"
    return table

def build_excluded_table(rows):
    table = "| negate 매칭 점수 | B 자신의 claim과 유사도 | A 문헌 | B 문헌 | A의 주장 | B의 negate 원문 (실제로는 B도 긍정하는 명제) |\n"
    table += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for r in rows:
        score = r['Score']
        cross = r['Cross_Claim_Score']
        card_a = r['Card_A_Claiming']
        card_b = r['Card_B_Negating']
        claim = r['Claim_Text'].replace('\n', ' ').replace('|', 'I')
        negate = r['Negate_Text'].replace('\n', ' ').replace('|', 'I')
        table += f"| {score} | {cross} | `{card_a}` | `{card_b}` | {claim} | {negate} |\n"
    return table

def update_report():
    rows = read_csv(csv_path)
    excluded_rows = read_csv(excluded_path)

    if not rows:
        print("CSV file not found or empty.")
        return

    main_table = build_main_table(rows)
    excluded_table = build_excluded_table(excluded_rows) if excluded_rows else ""

    section = f"""### 1. 교리 충돌 자동 탐지 엔진 (Conflict Detector) 상세 작동 원리 및 한계
`scripts/conflict_detector.py`에 의해 구동되는 이 엔진은 아래 절차로 가톨릭 교리 문헌 간의 텍스트 유사도 기반 충돌 **후보**를 탐지합니다.

*   **자동 파싱 (Parsing)**: 엔진은 `05_DOCTRINE_DB` 내의 모든 교리 마크다운 카드를 순회하며 정규 표현식으로 `주장(Claims)`과 `부정(Negates)` 섹션을 분리 추출합니다. 현재 기준 총 258개의 주장과 202개의 부정이 데이터베이스로 적재되었습니다.
*   **텍스트 벡터화 (TF-IDF & N-gram)**: 추출된 텍스트는 `문자 단위 N-gram (2~4)` 기반의 TF-IDF(Term Frequency-Inverse Document Frequency) 벡터로 변환됩니다.
*   **코사인 유사도(Cosine Similarity) 측정**: A 문서의 '주장' 벡터와 B 문서의 '부정' 벡터가 기하학적으로 얼마나 일치하는지 0~1 사이의 점수(Score)로 계산합니다.
*   **⚠️ 알려진 한계와 오탐 필터 (Cross-Claim Verification)**: 문자 n-gram 유사도만으로는 부정어(아니다/없다/불가능 등)를 안정적으로 구분하지 못합니다. 실제 검증 과정에서 "TRENT-S13-C01(화체설 긍정)과 CCC-1376의 negate 항목(공재설 부정 = 화체설 긍정)"처럼, 두 문헌이 사실은 **동일한 입장**인데 negate 문구의 표면적 어휘 중복만으로 "충돌"로 오분류된 사례가 다수 확인되었습니다(예: 세례 필수성에 대해 완전히 같은 입장인 CCC-1257과 TRENT-S07-C05가 0.328 점수로 "충돌"로 잘못 표시됨). 이를 걸러내기 위해 **cross-claim 재확인 필터**를 추가했습니다 — A의 주장이 B **자신의** claims 목록과도 높은 유사도를 보이면(= B 스스로도 같은 명제를 긍정한다는 뜻) 해당 매칭을 충돌 후보에서 제외합니다. 이 필터로 총 **{len(excluded_rows)}건**이 오탐으로 판정되어 제외되었으며, 상세 내역은 아래 §1-A 및 `08_REPORT/auto_conflict_excluded_self_negation.csv`에 투명하게 공개합니다.
*   **결과**: 필터 적용 후 유의미한(Score 0.20 이상) 'A Not A' 충돌 후보 **{len(rows)}건**이 자동 색인되었습니다. **본 리스트는 사람의 신학적 재검토가 필요한 1차 후보 목록이며, 알고리즘이 신학적 모순 여부를 최종 판정하는 것이 아닙니다.** char n-gram 유사도는 문맥을 이해하지 못하므로, 목록에 오른 항목도 인용 시 원문 대조와 정황 확인이 필요합니다.

#### 🔥 AI 엔진이 자동 색인한 교리 충돌(A Not A) 후보 리스트 (Cross-claim 필터 적용 후, {len(rows)}건)
아래는 파이썬 NLP 알고리즘이 찾아내고 오탐 필터를 통과한 교도권 내부 모순 후보 리스트입니다. 유사도(Score)가 높을수록 어휘상 정면 충돌에 가깝지만, 최종 신학적 판단은 원문 대조를 거쳐야 합니다.

{main_table}
#### 1-A. 🔍 오탐으로 제외된 사례 (투명성 공개, {len(excluded_rows)}건)
아래는 cross-claim 재확인 필터에 의해 "충돌 아님(= 사실상 동일 입장)"으로 판정되어 위 리스트에서 제외된 사례입니다. "B 자신의 claim과 유사도"가 "negate 매칭 점수"보다 높거나 같다는 것은, B 문헌 스스로도 A와 같은 명제를 별도로 주장하고 있다는 뜻입니다.

{excluded_table}
"""

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 기존 섹션(구버전 요약 또는 이전 실행분 전체 표)을 통째로 새 섹션으로 교체
    pattern = r'### 1\. 교리 충돌 자동 탐지 엔진.*?(?=### 2\. 인터랙티브 교리 붕괴 네트워크)'

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, section, content, flags=re.DOTALL)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"보고서 갱신 완료: 충돌 후보 {len(rows)}건 + 제외 사례 {len(excluded_rows)}건 반영")
    else:
        print("정규식 매칭 실패. 문서 구조를 확인하세요.")

if __name__ == '__main__':
    update_report()
