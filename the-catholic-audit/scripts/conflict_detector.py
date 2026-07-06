import os
import re
import csv
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Windows 콘솔 기본 코드페이지(cp949)는 이모지(🔥 등)를 인코딩하지 못해
# 정상 실행 후 print 단계에서 UnicodeEncodeError로 죽는 문제가 있어 utf-8로 고정한다.
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_DIR = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\05_DOCTRINE_DB"
REPORT_FILE = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\auto_conflict_results.csv"
EXCLUDED_FILE = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\auto_conflict_excluded_self_negation.csv"

# char n-gram 코사인 유사도는 부정어(아니다/없다/불가능 등)를 사실상 구분하지 못하므로,
# "A가 주장하는 명제 P"가 "B가 negate에 적어둔 문장(실제로는 B 자신도 주장하는 P의 재진술)"과
# 표면적으로 비슷하다는 이유만으로 충돌로 오분류되는 사례가 실측 검증됨
# (예: CCC-1257 vs TRENT-S07-C05 — 둘 다 "세례는 구원에 필수" 라는 동일 입장인데 0.328로 매칭됨,
#      TRENT-S13-C01 vs CCC-1376 — 둘 다 화체설을 긍정하는 동일 교리인데 0.36으로 매칭됨).
#
# 검증된 판별법: A의 주장(claim)을 B의 negate 항목뿐 아니라 B "자신의" claims 목록과도 비교한다.
# 만약 B 스스로도 A의 주장과 거의 동일한 내용을 자기 claims에 갖고 있다면(=B도 그 명제를 긍정),
# negate 매칭 점수가 아무리 높아도 이는 "충돌"이 아니라 "동일 입장 확인"이다.
# (검증 데이터: 오탐 사례는 cross-claim 유사도가 negate 매칭 점수보다 항상 높았고,
#  실제 충돌 사례는 cross-claim 유사도가 negate 매칭 점수보다 항상 크게 낮았다.)

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    cards = []
    sections = re.split(r'\n# ', '\n' + content)[1:]

    for sec in sections:
        lines = sec.strip().split('\n')
        title = lines[0].strip()

        card_id = "UNKNOWN"
        id_match = re.search(r'\|\s*\*\*ID\*\*\s*\|\s*([^|]+)\s*\|', sec)
        if id_match:
            card_id = id_match.group(1).strip()
        elif len(title.split()) > 0:
            card_id = title.split()[0]

        claims = []
        claims_match = re.search(r'## 주장 \(Claims\).*?(?=\n## |\n---|\Z)', sec, re.DOTALL)
        if claims_match:
            claims_text = claims_match.group(0)
            for line in claims_text.split('\n'):
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    claims.append(re.sub(r'^\d+\.\s*', '', line))

        negates = []
        negates_match = re.search(r'## 부정 \(Negates\).*?(?=\n## |\n---|\Z)', sec, re.DOTALL)
        if negates_match:
            negates_text = negates_match.group(0)
            for line in negates_text.split('\n'):
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    negates.append(re.sub(r'^\d+\.\s*', '', line))

        if card_id != "UNKNOWN" and (claims or negates):
            cards.append({
                'id': card_id,
                'file': os.path.basename(file_path),
                'claims': claims,
                'negates': negates
            })

    return cards

def main():
    print("가톨릭 교리 충돌 자동 탐지 엔진 (The Catholic Audit Engine) 실행 중...")

    all_cards = []
    for root, dirs, files in os.walk(DB_DIR):
        for file in files:
            if file.endswith('.md'):
                all_cards.extend(parse_markdown(os.path.join(root, file)))

    if not all_cards:
        print("Error: 교리 카드(.md)를 찾을 수 없습니다.")
        return

    print(f"총 {len(all_cards)}개의 교리 카드를 파싱했습니다.")

    claims_list = [] # (card_id, claim_text)
    negates_list = [] # (card_id, negate_text)

    for card in all_cards:
        for c in card['claims']:
            claims_list.append((card['id'], c))
        for n in card['negates']:
            negates_list.append((card['id'], n))

    print(f"추출 완료: 주장(Claims) {len(claims_list)}개, 부정(Negates) {len(negates_list)}개")
    print("의미론적 텍스트 유사도(Semantic Similarity) 분석 중...")

    # 한국어 형태소 분석기 없이도 문자 단위 N-gram을 통해 의미/형태적 유사도를 포착합니다.
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))

    corpus = [c[1] for c in claims_list] + [n[1] for n in negates_list]
    vectorizer.fit(corpus)

    claims_tfidf = vectorizer.transform([c[1] for c in claims_list])
    negates_tfidf = vectorizer.transform([n[1] for n in negates_list])

    similarity_matrix = cosine_similarity(claims_tfidf, negates_tfidf)
    claims_claims_matrix = cosine_similarity(claims_tfidf, claims_tfidf)

    # 카드별로 자기 자신의 claims 인덱스를 모아둔다 (cross-claim 재확인용)
    card_claim_indices = {}
    for idx, (cid, _) in enumerate(claims_list):
        card_claim_indices.setdefault(cid, []).append(idx)

    conflicts = []
    excluded = []
    THRESHOLD = 0.20 # 유사도 임계값

    for i, c_item in enumerate(claims_list):
        for j, n_item in enumerate(negates_list):
            card_a = c_item[0]
            card_b = n_item[0]

            # 자기 자신 카드 내의 충돌은 제외 (외부 충돌만 탐지)
            if card_a == card_b:
                continue

            sim_score = similarity_matrix[i, j]
            if sim_score <= THRESHOLD:
                continue

            # ── Cross-claim 재확인 (오탐 필터) ──
            # A의 주장(claim i)이 B 자신의 claims 목록과도 높은 유사도를 보인다면,
            # B 스스로도 그 명제를 긍정하고 있다는 뜻이므로 negate 매칭은 오탐이다.
            b_claim_idxs = card_claim_indices.get(card_b, [])
            cross_claim_score = max(
                (claims_claims_matrix[i, k] for k in b_claim_idxs if k != i),
                default=0.0,
            )

            row = {
                'Score': round(sim_score, 3),
                'Card_A_Claiming': card_a,
                'Card_B_Negating': card_b,
                'Claim_Text': c_item[1],
                'Negate_Text': n_item[1],
            }

            if cross_claim_score >= sim_score:
                row['Cross_Claim_Score'] = round(cross_claim_score, 3)
                excluded.append(row)
            else:
                conflicts.append(row)

    conflicts.sort(key=lambda x: x['Score'], reverse=True)
    excluded.sort(key=lambda x: x['Score'], reverse=True)

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Score', 'Card_A_Claiming', 'Card_B_Negating', 'Claim_Text', 'Negate_Text'])
        writer.writeheader()
        writer.writerows(conflicts)

    with open(EXCLUDED_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Score', 'Cross_Claim_Score', 'Card_A_Claiming', 'Card_B_Negating', 'Claim_Text', 'Negate_Text'])
        writer.writeheader()
        writer.writerows(excluded)

    print(f"분석 완료! 총 {len(conflicts)}건의 논리적 충돌(A Not A) 의심 사례가 발견되었습니다.")
    print(f"Cross-claim 재확인으로 오탐 판정되어 제외된 사례: {len(excluded)}건 (검토용 별도 저장)")
    print(f"상세 결과가 CSV 형식으로 저장되었습니다: {REPORT_FILE}")
    print(f"제외 사례 목록: {EXCLUDED_FILE}\n")

    print("🔥 [엔진이 찾아낸 충돌 유사도 상위 3건] 🔥")
    for idx, c in enumerate(conflicts[:3]):
        print(f"#{idx+1} [유사도 {c['Score']}] {c['Card_A_Claiming']} vs {c['Card_B_Negating']}")
        print(f"   [A의 주장] {c['Claim_Text']}")
        print(f"   [B가 부정함] {c['Negate_Text']}\n")

    if excluded:
        print("⚠️ [Cross-claim 재확인으로 제외된 상위 3건 — 참고용] ⚠️")
        for idx, c in enumerate(excluded[:3]):
            print(f"#{idx+1} [negate 매칭 {c['Score']} / B 자신의 claim과 유사도 {c['Cross_Claim_Score']}] {c['Card_A_Claiming']} vs {c['Card_B_Negating']}")
            print(f"   [A의 주장] {c['Claim_Text']}")
            print(f"   [B가 negate에 적어둔 문장 — 그러나 B 자신도 사실상 같은 명제를 주장함] {c['Negate_Text']}\n")

if __name__ == '__main__':
    main()
