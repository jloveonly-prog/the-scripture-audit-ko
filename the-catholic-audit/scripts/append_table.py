import csv
import re
import os

csv_path = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\auto_conflict_results.csv"
md_path = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\catholic_error_report.md"

def update_report():
    if not os.path.exists(csv_path):
        print("CSV file not found.")
        return

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    table_md = "#### 🔥 AI 엔진이 자동 색인한 전체 교리 충돌(A Not A) 전수 리스트\n"
    table_md += "아래는 파이썬 NLP 알고리즘이 찾아낸 교도권 내부의 모순 전수 리스트입니다. 유사도(Score)가 높을수록 논리적으로 완벽하게 정면 충돌함을 의미합니다.\n\n"
    table_md += "| 유사도(Score) | A 문헌 (주장) | B 문헌 (부정) | A의 주장 원문 (Claim) | B가 단죄/부정하는 명제 (Negate) |\n"
    table_md += "| :--- | :--- | :--- | :--- | :--- |\n"

    for r in rows:
        score = r['Score']
        card_a = r['Card_A_Claiming']
        card_b = r['Card_B_Negating']
        claim = r['Claim_Text'].replace('\n', ' ').replace('|', 'I')
        negate = r['Negate_Text'].replace('\n', ' ').replace('|', 'I')
        table_md += f"| **{score}** | `{card_a}` | `{card_b}` | {claim} | {negate} |\n"

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 정규식으로 기존 요약 섹션을 날리고 전체 표로 덮어쓰기
    pattern = r'#### 🔥 AI 엔진이 찾아낸 충돌 상위\(Top\) 사례 분석.*?(?=### 2\. 인터랙티브 교리 붕괴 네트워크)'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, table_md + '\n', content, flags=re.DOTALL)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"보고서에 총 {len(rows)}건의 충돌 리스트 전체를 성공적으로 삽입했습니다.")
    else:
        print("정규식 매칭 실패. 문서 구조를 확인하세요.")

if __name__ == '__main__':
    update_report()
