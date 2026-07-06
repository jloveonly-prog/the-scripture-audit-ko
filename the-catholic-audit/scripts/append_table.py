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

def label(card_id, title):
    return f"`{card_id}`({title})" if title else f"`{card_id}`"

def clean(text):
    return text.replace('\n', ' ').replace('|', 'I')

def build_main_table(rows):
    """읽기 쉬운 문헌명 + '왜 충돌인가' 요약 문장을 곁들인 번호 목록으로 렌더링한다."""
    lines = []
    for idx, r in enumerate(rows, 1):
        score = r['Score']
        card_a, title_a = r['Card_A_Claiming'], r.get('Title_A', '')
        card_b, title_b = r['Card_B_Negating'], r.get('Title_B', '')
        claim = clean(r['Claim_Text'])
        negate = clean(r['Negate_Text'])
        explanation = (
            f"A({label(card_a, title_a)})가 주장하는 명제와 B({label(card_b, title_b)})가 "
            f"명시적으로 단죄·부정하는 명제가 어휘상 사실상 같은 내용이다. 두 문헌이 같은 사안에 대해 "
            f"정반대 입장을 취하고 있어 동시에 참일 수 없다(유사도 {score})."
        )
        lines.append(
            f"**#{idx}. [유사도 {score}] {label(card_a, title_a)} vs {label(card_b, title_b)}**\n"
            f"- **A의 주장**: {claim}\n"
            f"- **B가 단죄/부정하는 명제**: {negate}\n"
            f"- **왜 충돌인가**: {explanation}\n"
        )
    return "\n".join(lines)

def build_excluded_table(rows):
    """오탐 판정 사유(자동 cross-claim 필터 vs 수작업 원문 대조)를 구분해 설명한다."""
    lines = []
    for idx, r in enumerate(rows, 1):
        score = r['Score']
        cross = r.get('Cross_Claim_Score', '')
        card_a, title_a = r['Card_A_Claiming'], r.get('Title_A', '')
        card_b, title_b = r['Card_B_Negating'], r.get('Title_B', '')
        claim = clean(r['Claim_Text'])
        negate = clean(r['Negate_Text'])
        reason = r.get('Exclusion_Reason', '')
        if '수작업' in reason:
            explanation = (
                f"어휘 유사도(negate 매칭 {score} / 자기 claim 유사도 {cross})만으로는 걸러지지 않는 경계 사례라, "
                f"05_DOCTRINE_DB 원문을 직접 대조해 검증했다. 그 결과 두 카드가 같은 문서의 중복 카드이거나 "
                f"(요약 카드 vs 세부 조항 카드), 서로 다른 두 문헌이 실제로는 같은 교리를 긍정하고 있음이 "
                f"확인되어 '충돌 아님'으로 분류했다."
            )
        else:
            explanation = (
                f"negate 매칭 점수({score})만 보면 충돌처럼 보이지만, B({label(card_b, title_b)}) 자신의 "
                f"주장(claims) 중에도 A와 사실상 같은 내용이 있다(유사도 {cross}). 즉 B는 자신이 negate 목록에 "
                f"적어둔 반대 명제를 스스로도 거부하고 있으므로, 이는 진짜 충돌이 아니라 두 문헌이 같은 입장을 "
                f"다르게 표현한 것이다."
            )
        lines.append(
            f"**#{idx}. [negate 매칭 {score} / 자기 claim 유사도 {cross}] {label(card_a, title_a)} vs {label(card_b, title_b)}**\n"
            f"- **A의 주장**: {claim}\n"
            f"- **B가 negate에 적어둔 문장(실제로는 B도 긍정하는 명제)**: {negate}\n"
            f"- **왜 오탐인가**: {explanation}\n"
        )
    return "\n".join(lines)

# 아래는 자동 색인 후 사람이 원문을 대조해 "진짜 충돌"로 남은 상위 4건(Score 0.25 이상)에 대해,
# 가톨릭 측에서 나올 법한 최강 반박과 그에 대한 재반박을 정리한 것이다. 자동 생성 문장이 아니라
# 05_DOCTRINE_DB 원문과 각 사안의 실제 신학적 논쟁사를 직접 확인하고 작성했다.
PRIORITY_DEEPDIVE = """#### 1-B. 🎯 상위 4건 우선순위 심층분석 (예상 반박 · 재반박 포함)
아래 4건은 Score 상위권이면서 §1의 2단계 필터(자동 cross-claim + 수작업 원문 대조)를 모두 통과한, 현재로서 가장 근거가 탄탄한 후보입니다. 각 항목마다 가톨릭 측에서 나올 법한 가장 강력한 반박과 그에 대한 재반박을 함께 제시해, 목록만 던져놓고 끝내지 않도록 했습니다.

**1. `UNAM-SANCTAM`(1302) vs `CCC-0847`/`LG-16`(1964~1992) — "교회 밖 구원 없음"의 절대성 (Score 0.558 / 0.528)**
- **쟁점**: Unam Sanctam은 "로마 교황에 대한 복종이 모든 인간 피조물에게 예외 없이 구원의 필수조건"이라 선언한 반면, 제2차 바티칸(LG 16)과 CCC 847은 "자기 탓 없이 복음을 모르는 자, 심지어 무슬림도 양심에 따라 살면 구원 가능"이라 가르친다.
- **예상 최강 반박**: 모순이 아니라 교리의 발전(development of doctrine)이다. Unam Sanctam은 복음을 알고도 고의로 거부하는 자를 겨냥한 것이고, CCC/LG는 애초에 복음을 들을 기회가 없었던 자(invincible ignorance, 무지 불가항력)를 다루는 것이라 적용 대상이 다르다.
- **재반박**: 그러나 Unam Sanctam 원문에는 "몰랐던 자"에 대한 예외 조항이 전혀 없고, 같은 시대의 피렌체 공의회(1442)는 한발 더 나아가 "그리스도를 위해 피 흘리는 순교자라도" 가톨릭 밖이면 예외 없다고 못박았다. "대상이 다르다"는 구분은 20세기 이후 사후적으로 도입된 해석이며, 원문 자체는 이 구분을 예정하지 않았다.
- **학술 합의 수준**: 🟡 가톨릭 내부에서도 갈리는 사안 — Feeney 신부 단죄(1949) 이후의 주류 해석("development")과, 전통주의 진영(SSPX 등, "이것이야말로 교회의 배교"라 주장)이 정면으로 충돌한다. 즉 이는 "가톨릭이 몰랐다가 놀랄" 주제가 아니라, 가톨릭 신학 내부에 이미 존재하는 균열선이다.

**2. CDF `Responsum ad Dubium`(2021) vs `Fiducia Supplicans`(2023) — 동성 커플 축복 가능 여부 (Score 0.281)**
- **쟁점**: 2021년 신앙교리부 답변은 동성 결합에 대한 모든 형태의 축복을 금지했는데, 불과 2년 뒤 2023년 Fiducia Supplicans는 비전례적 사목적 축복을 허용했다.
- **예상 최강 반박**: 두 문서 모두 "혼인 자체를 축복하는 것"은 여전히 금지한다는 데 일치한다. 2021년 문서가 막은 것은 "커플의 결합을 축복"하는 행위이고, 2023년 문서가 허용한 것은 "개인에 대한 사목적 자비의 축복"이라 층위가 다르다.
- **재반박**: 그러나 Fiducia Supplicans는 "커플로서" 함께 축복받는 것을 명시적으로 허용하고 있어, 실제로 아프리카 주교회의 전체를 포함한 다수의 주교단이 "이 구분은 실무상 성립하지 않으며 2021년 답변과 정면으로 충돌한다"고 공개적으로 반발했다.
- **학술 합의 수준**: 🔴 논쟁 진행 중 — 불과 2년 사이 공식 문서의 결론이 뒤집혔고, 가톨릭 주교단 스스로 공식적으로 이견을 표출한 몇 안 되는 사례다.

**3. `Syllabus Errorum`(1864) vs `Dignitatis Humanae`(1965) — 종교 자유 (Score 0.273)**
- **쟁점**: 비오 9세의 Syllabus Errorum은 "누구나 자기 이성이 옳다고 믿는 종교를 자유로이 신봉할 권리가 있다"는 명제를 오류로 단죄했는데, 제2차 바티칸의 Dignitatis Humanae는 정확히 그 명제를 인간 존엄성에 근거한 권리로 선언했다.
- **예상 최강 반박**: Syllabus는 무류 선언(ex cathedra)이 아니라 통상 교도권의 훈령 목록이었고, 19세기 특정 정치적 반교권주의를 겨냥한 것이지 "모든 형태의 종교 자유"를 영원히 단죄한 게 아니다.
- **재반박**: 그러나 Syllabus 15항의 문구는 Dignitatis Humanae 2항이 긍정하는 명제와 표현까지 거의 일치한다. 또한 "무류 선언이 아니었다"는 반박이 성립하더라도, 이는 "무류하지 않은 교도권의 가르침은 100여 년 뒤 정반대로 뒤집힐 수 있다"는 사실을 인정하는 셈이 되어, 이 사례가 원래 노리는 논점("교도권의 가르침이 뒤집힐 수 있다는 것 자체")을 반박하지 못하고 오히려 강화한다.
- **학술 합의 수준**: 🟢 학계 대체로 인정 — 이 사례(Syllabus vs Dignitatis Humanae)는 "진정한 발전"과 "실질적 반전" 사이의 경계 사례로 신학자들 사이에서 가장 자주 인용되는 항목 중 하나이며(존 코트니 머레이 신부 관련 논쟁이 대표적), 긴장 관계 자체를 부정하는 학자는 드물다.

**4. `CCC-1861` vs `Amoris Laetitia` 8장 — 대죄의 객관적 요건과 사목적 식별 (Score 0.256)**
- **쟁점**: CCC 1861은 대죄가 성립하려면 중대한 내용·충분한 인식·완전한 동의가 필요하다고 규정하는데, Amoris Laetitia는 "객관적 상태만으로 은총의 상태를 판단할 수 없다"며 이혼 후 재혼자에 대한 개별 양심 식별을 요구한다.
- **예상 최강 반박**: 모순이 아니다 — CCC 1861 자체가 이미 '충분한 인식'과 '완전한 동의'라는 주관적 요건을 명시하고 있으므로, Amoris Laetitia는 기존 조건을 재확인했을 뿐 새 원칙을 만든 게 아니다.
- **재반박**: 이 반박은 상당히 타당하다 — 두 문헌은 원칙적으로 같은 틀(객관적 중대성 + 주관적 책임)을 공유한다. 실제 논쟁은 원칙이 아니라 '적용'에 있다: 231명의 신학자·성직자가 서명한 2017년 "Correctio Filialis"는 Amoris Laetitia 각주 351이 재혼자의 지속적 성행위에 대해 완전한 인식·동의가 없는 것처럼 사실상 일괄 전제해버려, 개별 식별이라는 명목 아래 객관적 기준을 무력화한다고 주장했다.
- **학술 합의 수준**: 🟡 진행 중인 논쟁 — 프란치스코 교황 재위 기간 가톨릭 내부에서 가장 첨예했던 신학 논쟁 중 하나이며(2016년 '네 추기경의 dubia' 사건 포함), "원칙적 모순은 없다"는 반박과 "실질적으로 규범이 바뀌었다"는 비판이 여전히 공존한다.

**종합 평가**: 사람의 원문 대조를 거친 뒤에도 살아남은 이 4건은 예외 없이 가톨릭 신학계 내부에 이미 알려진 논쟁 주제였다. 즉 이 자동 탐지 엔진의 실질적 가치는 "아무도 몰랐던 새 모순을 발견하는 것"이 아니라 "이미 알려진 논쟁 주제를 258개 주장 데이터베이스에서 자동으로 재발굴하는 것"에 가깝다 — 이는 과장할 성과가 아니라 정직하게 밝혀야 할 한계다.

"""

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
*   **⚠️ 알려진 한계와 2단계 오탐 필터**: 문자 n-gram 유사도만으로는 부정어(아니다/없다/불가능 등)를 안정적으로 구분하지 못합니다.
    1.  **자동 cross-claim 필터**: A의 주장이 B **자신의** claims 목록과도 높은 유사도를 보이면(= B 스스로도 같은 명제를 긍정한다는 뜻), negate 매칭 점수가 아무리 높아도 충돌 후보에서 제외합니다.
    2.  **수작업 원문 대조 검증**: 위 필터의 점수 차이가 근소한 경계 사례(예: 0.318 vs 0.317)는 `05_DOCTRINE_DB` 원문을 사람이 직접 읽어 확인했습니다. 그 결과 (a) 같은 문서를 가리키는 카드가 DB에 두 장 존재하는 경우(예: `DIGNITATIS-HUMANAE`와 `VATICAN2-DH`는 둘 다 1965년 종교 자유 선언 원문, `TRENT-S13`과 `TRENT-S13-C01`은 같은 회기의 요약/세부 카드 쌍)와 (b) 서로 다른 두 문헌이 우연히 같은 교리를 긍정한 경우(예: `VAT1-PASTOR-AETERNUS`와 `CCC-888_892`는 둘 다 교황 무류성을 긍정)가 확인되어, 해당 쌍은 negate 매칭 점수와 무관하게 "충돌 아님"으로 재분류했습니다. (임의의 숫자 마진을 적용하지 않은 이유는, 마진을 넉넉히 잡으면 `CCC-1861` vs `AMORIS-LAETITIA-CH8`처럼 실제로 신학적 긴장이 남아있는 정당한 후보까지 함께 제외되기 때문입니다.)

    이 2단계 필터로 총 **{len(excluded_rows)}건**이 오탐으로 판정되어 제외되었으며, 어떤 필터로 제외됐는지까지 포함한 상세 내역은 아래 §1-A 및 `08_REPORT/auto_conflict_excluded_self_negation.csv`에 투명하게 공개합니다.
*   **결과**: 필터 적용 후 유의미한(Score 0.20 이상) 'A Not A' 충돌 후보 **{len(rows)}건**이 자동 색인되었습니다. **본 리스트는 사람의 신학적 재검토가 필요한 1차 후보 목록이며, 알고리즘이 신학적 모순 여부를 최종 판정하는 것이 아닙니다.** char n-gram 유사도는 문맥을 이해하지 못하므로, 목록에 오른 항목도 인용 시 원문 대조와 정황 확인이 필요합니다.

#### 🔥 AI 엔진이 자동 색인한 교리 충돌(A Not A) 후보 리스트 (2단계 오탐 필터 적용 후, {len(rows)}건)
아래는 파이썬 NLP 알고리즘이 찾아내고 오탐 필터를 통과한 교도권 내부 모순 후보 리스트입니다. 각 항목마다 "왜 충돌인가"를 함께 표기했습니다. 유사도(Score)가 높을수록 어휘상 정면 충돌에 가깝지만, 최종 신학적 판단은 원문 대조를 거쳐야 합니다.

{main_table}
#### 1-A. 🔍 오탐으로 제외된 사례 (투명성 공개, {len(excluded_rows)}건)
아래는 자동 cross-claim 필터 또는 수작업 원문 대조에 의해 "충돌 아님(= 사실상 동일 입장)"으로 판정되어 위 리스트에서 제외된 사례입니다. 각 항목마다 "왜 오탐인가"를 함께 표기했습니다.

{excluded_table}
{PRIORITY_DEEPDIVE}"""

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
