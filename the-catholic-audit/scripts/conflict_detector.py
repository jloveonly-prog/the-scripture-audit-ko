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
#
# 그러나 cross-claim 유사도가 negate 매칭 점수보다 "근소하게" 낮은 경계 사례가 다수 실측되었고
# (예: VAT1-PASTOR-AETERNUS vs CCC-888_892는 0.318 vs 0.317로 사실상 동점),
# 그 원인을 직접 05_DOCTRINE_DB 원문을 읽어 확인한 결과 두 가지 유형으로 나뉜다:
#   (1) 문헌 DB 자체에 같은 문서를 가리키는 카드가 2장 존재 — 예) DIGNITATIS-HUMANAE와 VATICAN2-DH는
#       둘 다 1965년 종교 자유 선언 원문이고, PAPAL-FIDUCIA와 FIDUCIA-SUPPLICANS는 둘 다 2023년
#       피두치아 수플리칸스 선언 원문이며, TRENT-S13(회기 요약)과 TRENT-S13-C01(동일 회기의 개별 조항),
#       CCC-1322_1419(범위 요약)와 CCC-1376(그 범위 안의 개별 항), CCC-1471_1479(범위 요약)와
#       CCC-1471(그 범위 안의 개별 항)도 각각 동일 출처의 요약 카드/세부 카드 쌍이다.
#   (2) 서로 다른 두 문헌이 우연히 같은 교리를 긍정 — 예) VAT1-PASTOR-AETERNUS와 CCC-888_892는 둘 다
#       "교황이 사도좌에서 선언하면 무류하다"를 긍정하고, TRENT-S07-C05와 CCC-1257은 둘 다
#       "세례는 통상적 수단으로서 구원에 필수"라는 동일 입장(예외 가능성까지 포함)을 취한다.
# char n-gram 유사도의 노이즈만으로는 이 경계를 안정적으로 가르지 못하므로, 위 원문 대조로 직접
# 검증한 쌍은 negate 매칭 점수와 무관하게 강제로 "동일 입장"으로 분류한다. 임의의 숫자 마진을
# 적용하지 않는 이유는, 마진을 넉넉히 잡으면 CCC-1861 vs AMORIS-LAETITIA-CH8(대죄 성립 요건 vs
# 사목적 식별)처럼 실제로는 신학적 긴장이 남아있는 정당한 후보까지 함께 제외되기 때문이다.
KNOWN_SAME_POSITION_PAIRS = {
    frozenset({'VAT1-PASTOR-AETERNUS', 'CCC-888_892'}),
    frozenset({'VATICAN2-DH', 'DIGNITATIS-HUMANAE'}),
    frozenset({'COUNCIL-LATERAN_IV', 'TRENT-S13-C01'}),
    frozenset({'TRENT-S13', 'CCC-1322_1419'}),
    frozenset({'TRENT-S07-C05', 'CCC-1257'}),
    frozenset({'TRENT-S13', 'CCC-1376'}),
    frozenset({'COUNCIL-LATERAN_IV', 'CCC-1376'}),
    frozenset({'FIDUCIA-SUPPLICANS', 'PAPAL-FIDUCIA'}),
    frozenset({'COUNCIL-LATERAN_IV', 'CCC-1322_1419'}),
    frozenset({'CCC-1471', 'CCC-1471_1479'}),
    frozenset({'TRENT-S13-C01', 'CCC-1322_1419'}),
    frozenset({'CCC-1376', 'CCC-1322_1419'}),
    frozenset({'UNAM-SANCTAM', 'PAPAL-UNAM'}),  # 둘 다 1302년 교서 Unam Sanctam 원문 (batch 카드 vs 개별 카드 중복)
    frozenset({'NOSTRA-AETATE', 'VATICAN2-NA'}),  # 둘 다 1965년 선언 Nostra Aetate 원문 (batch 카드 vs 개별 카드 중복)
    # 아래 4쌍은 상위 스코어(0.30~0.39) 항목을 원문까지 대조해 개별 검증한 결과다.
    # TRENT-S06 vs CCC-1987_2016: CCC-1987_2016 자신의 claim #1("칭의는 죄의 사면과 내적 성화를
    # 모두 포괄")이 TRENT-S06의 주장과 같은 내용이며, negate #1("이신칭의")은 둘 다 함께 배격하는
    # 견해다 — cross-claim 점수(0.069)가 낮게 나온 것은 두 카드의 "주장" 문구 표현이 서로 달라서일
    # 뿐, negate 항목이 상대 주장을 거의 그대로 미러링해 적혀 있어 negate 매칭 점수만 우연히 높다.
    frozenset({'TRENT-S06', 'CCC-1987_2016'}),
    # TRENT-S07-C05 vs CCC-2181: "세례는 의무" 대 "미사 참여는 선택"이라는 서로 다른 주제를
    # "~은 선택이 아니라 의무다"라는 문장 구조 유사성만으로 잘못 엮은 사례. 게다가 CCC-2181
    # 자신의 claim #1이 이미 "미사 참여는 의무"라고 명시해 negate 항목과 정반대이므로, 애초
    # CCC-2181도 "의무성"이라는 원칙 자체에는 동의한다.
    frozenset({'TRENT-S07-C05', 'CCC-2181'}),
    # TRENT-S06-CH04 vs CCC-0847: TRENT-S06-CH04의 "세례의 열망(votum)으로 의화 가능"이라는
    # 주장은, CCC-0847이 negate로 배격하는 "세례 없이는 어떤 경우에도 구원 불가"라는 절대론과
    # 정확히 반대말이다. 즉 CCC-0847도 그 절대론을 스스로 거부하고 있으므로 TRENT-S06-CH04와
    # 같은 입장(예외적 구원 가능성 인정)이다 — negate 매칭은 어휘가 겹치는 반대 문장끼리
    # 비교된 것일 뿐 실제 입장 차이가 아니다.
    frozenset({'TRENT-S06-CH04', 'CCC-0847'}),
    # CCC-402_412 vs CCC-1452: 원죄/세례(CCC-402_412)와 대죄/고해성사(CCC-1452)는 완전히 다른
    # 죄·성사 범주인데, "~을 통해서만 용서/세척될 수 있다"는 문장 구조만 겹쳐 오분류된 사례.
    frozenset({'CCC-402_412', 'CCC-1452'}),
    # TRENT-S06-C32 vs TRENT-S06-C09: 같은 공의회 같은 회기(제6차, 의화 교령)의 두 캐논이다.
    # C09의 negate는 "협력 불필요"이고 C32의 claim은 "협력이 결합된 결과"이므로, C09도 협력의
    # 필요성 자체는 인정한다 — 애초 같은 문서 내에서 서로 보완하는 캐논이지 대립하는 캐논이 아니다.
    frozenset({'TRENT-S06-C32', 'TRENT-S06-C09'}),
    # COUNCIL-LATERAN_IV vs UNAM-SANCTAM: UNAM-SANCTAM의 negate("교회 밖 구원 가능")는 UNAM-SANCTAM
    # 스스로도 배격하는 명제이므로, Lateran IV와 마찬가지로 엄격한 EENS 입장을 취한다 — 둘 다
    # 바티칸2 이전의 배타적 해석을 공유하는 동일 입장이다.
    frozenset({'COUNCIL-LATERAN_IV', 'UNAM-SANCTAM'}),
    # CCC-1471 vs CCC-1498: 면죄부의 '조건'(1471)과 '죽은 자에게도 적용 가능'(1498)은 같은 교리의
    # 서로 다른 측면을 다룰 뿐 상호 배타적이지 않다. 1471은 "산 자만" 된다고 주장한 적이 없다.
    frozenset({'CCC-1471', 'CCC-1498'}),
    # CCC-402_412 vs CCC-1257_1261: CCC-1257_1261은 CCC-1257과 동일 주제(세례의 필수성, batch
    # 카드/개별 카드 중복 계열)이며, "세례는 구원의 통상적 수단"이라는 같은 뉘앙스를 공유한다.
    frozenset({'CCC-402_412', 'CCC-1257_1261'}),
    # CCC-1030 vs CCC-161_165: 연옥에 있는 영혼(이미 은총 안에서 죽은 자)의 구원 보장과, 살아있는
    # 자가 믿음을 저버려 구원을 잃을 수 있다는 명제는 서로 다른 대상(죽은 자 vs 산 자)에 관한
    # 것이라 논리적으로 상충하지 않는다 — "구원/상실"이라는 어휘만 겹치는 범주 오류.
    frozenset({'CCC-1030', 'CCC-161_165'}),
    # CCC-1452 vs CCC-1996: "하느님에 대한 사랑에서 비롯된 통회"와 "인간의 행위에서 비롯된 칭의"는
    # 같은 명제가 아니다 — 완전한 통회는 은총이 촉발한 사랑의 반응이지 CCC-1996이 배격하는 자율적
    # "인간의 행위"(펠라기우스주의)가 아니므로, 어휘 구조("~에서 비롯된다")만 겹치는 오분류다.
    frozenset({'CCC-1452', 'CCC-1996'}),
}

# 위 12쌍은 애초 negate 매칭 점수가 우연히 높게 나온 경계 사례를 추적하다 발견된 것이고,
# 05_DOCTRINE_DB 전체를 (출처, 조항 범위) 기준으로 훑어보면 같은 문서가 "batchN_*.md" 요약 카드와
# 개별 카드로 이중 등록된 사례가 더 있다(예: VATICAN1-PA/VAT1-PASTOR-AETERNUS, VATICAN2-LG/LG-16,
# PAPAL-AMORIS/AMORIS-LAETITIA-CH8, CCC-1030_1032/CCC-1030, CCC-1257_1261/CCC-1257,
# TRENT-S06·S07·S14·S22·S24 각 세션 요약 카드와 그 개별 조항 카드들). 이들은 현재 임계값(0.20)을
# 넘는 매칭이 없어 결과에 영향을 주지 않으므로 위 목록에 넣지 않았지만, 데이터베이스 정합성 관점에서는
# 같은 문서를 가리키는 카드 쌍이 존재한다는 사실 자체가 별도로 정리가 필요한 이슈다.
# (참고: CCC-2068은 개별 카드와 batch 카드가 ID까지 완전히 동일하게 중복 등록되어 있다.)

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

        # "TRENT-S06-C32 — 선한 행위가 공로 없다 하면 파문" 형식의 제목에서
        # ID와 " — "/" " 구분자를 뗀 사람이 읽기 쉬운 이름만 남긴다.
        readable_title = re.sub(r'^\S+\s*[—-]?\s*', '', title).strip()
        if not readable_title:
            readable_title = title

        if card_id != "UNKNOWN" and (claims or negates):
            cards.append({
                'id': card_id,
                'title': readable_title,
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

    title_map = {card['id']: card['title'] for card in all_cards}

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
                'Title_A': title_map.get(card_a, ''),
                'Card_B_Negating': card_b,
                'Title_B': title_map.get(card_b, ''),
                'Claim_Text': c_item[1],
                'Negate_Text': n_item[1],
            }

            is_known_same_position = frozenset({card_a, card_b}) in KNOWN_SAME_POSITION_PAIRS

            if cross_claim_score >= sim_score or is_known_same_position:
                row['Cross_Claim_Score'] = round(cross_claim_score, 3)
                row['Exclusion_Reason'] = (
                    '수작업 원문 대조 검증 (문헌 DB 중복/두 문헌의 동일 입장 확인)'
                    if is_known_same_position
                    else 'cross-claim 자동 필터 (B 자신의 claims와 유사도가 negate 매칭 점수 이상)'
                )
                excluded.append(row)
            else:
                conflicts.append(row)

    conflicts.sort(key=lambda x: x['Score'], reverse=True)
    excluded.sort(key=lambda x: x['Score'], reverse=True)

    main_fields = ['Score', 'Card_A_Claiming', 'Title_A', 'Card_B_Negating', 'Title_B', 'Claim_Text', 'Negate_Text']
    excluded_fields = main_fields[:1] + ['Cross_Claim_Score'] + main_fields[1:] + ['Exclusion_Reason']

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=main_fields)
        writer.writeheader()
        writer.writerows(conflicts)

    with open(EXCLUDED_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=excluded_fields)
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
