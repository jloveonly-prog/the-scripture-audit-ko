import os
import re
import csv
import sys
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Windows 콘솔 기본 코드페이지(cp949)는 이모지(🔥 등)를 인코딩하지 못해
# 정상 실행 후 print 단계에서 UnicodeEncodeError로 죽는 문제가 있어 utf-8로 고정한다.
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DB_DIR = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\04_DOCTRINE_DB"
REPORT_FILE = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\auto_conflict_results.csv"
import json as _json
with open(os.path.join(os.path.dirname(DB_DIR), 'config.json'), encoding='utf-8') as _f:
    _CFG = _json.load(_f)

EXCLUDED_FILE = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\auto_conflict_excluded_self_negation.csv"

# [오탐 필터 이력 및 원리]
# 초기 버전은 TF-IDF char n-gram(임계값 0.20)을 사용했고, 현재는 Sentence-Transformers
# 다국어 임베딩(임계값 0.60)을 사용한다. 임베딩도 "주제 인접"과 "논리 모순"을 완전히
# 구분하지 못하므로 아래 두 겹의 오탐 필터를 유지한다:
#
# ① Cross-claim 자동 필터: A의 주장(claim)을 B의 negate 항목뿐 아니라 B "자신의" claims
#    목록과도 비교한다. B 스스로도 A의 주장과 거의 동일한 내용을 자기 claims에 갖고 있다면
#    (=B도 그 명제를 긍정), negate 매칭 점수가 아무리 높아도 "충돌"이 아니라 "동일 입장"이다.
#
# ② 수작업 원문 대조 목록(KNOWN_SAME_POSITION_PAIRS): cross-claim 점수가 negate 매칭 점수보다
#    근소하게 낮아 자동 필터를 통과하는 경계 사례를 04_DOCTRINE_DB 원문까지 직접 읽어
#    "서로 다른 두 문헌이 같은 교리를 긍정" 또는 "범위 요약 카드/개별 조항 카드의 부분 중첩"으로
#    확인한 쌍. 점수와 무관하게 강제로 "동일 입장"으로 분류한다. 임의의 숫자 마진을 적용하지
#    않는 이유는, 마진을 넉넉히 잡으면 CCC-1861 vs AMORIS-LAETITIA-CH8(대죄 성립 요건 vs
#    사목적 식별)처럼 실제로는 신학적 긴장이 남아있는 정당한 후보까지 함께 제외되기 때문이다.
#
# ※ 2026-07-07 DB 정리: 같은 문서가 batch 카드와 개별 카드로 "완전 중복" 등록되어 있던 사례
#    (VATICAN2-DH/DIGNITATIS-HUMANAE, PAPAL-FIDUCIA/FIDUCIA-SUPPLICANS, PAPAL-UNAM/UNAM-SANCTAM,
#    VATICAN2-NA/NOSTRA-AETATE, VATICAN1-PA/VAT1-PASTOR-AETERNUS, VATICAN2-LG/LG-16,
#    PAPAL-AMORIS/AMORIS-LAETITIA-CH8, CCC-2068 동일 ID 중복)는 DB에서 batch 쪽 카드를 삭제하여
#    원천 해결했다. 아래 목록에는 현존 카드 쌍만 남긴다. (범위 요약 ↔ 개별 조항 카드는 서로
#    다른 범위를 다루므로 카드 자체는 유지하고, 여기서 동일 입장으로만 처리한다.)
# [오탐 제외 목록 — 데이터 파일로 분리됨]
# 수작업 원문 대조로 "동일 입장(충돌 아님)"이 확정된 카드 쌍과 각 쌍의 판정 근거 주석은
# 04_DOCTRINE_DB/same_position_pairs.txt 로 이관했다 (2026-08-30 구조 개선).
# 데이터를 코드에 하드코딩하지 않기 위함 — 쌍 추가/삭제는 그 파일만 수정하면 된다.
def _load_same_position_pairs():
    path = os.path.join(DB_DIR, 'same_position_pairs.txt')
    pairs = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()  # 행 끝 주석 제거
            if not line:
                continue
            a, _, b = line.partition('|')
            a, b = a.strip(), b.strip()
            if a and b:
                pairs.add(frozenset({a, b}))
    return pairs

KNOWN_SAME_POSITION_PAIRS = _load_same_position_pairs()

# 잔여 범위 중첩 계열(CCC-1030_1032↔CCC-1030, CCC-1257_1261↔CCC-1257, TRENT 세션 요약↔개별
# 조항)은 "같은 문서의 완전 중복"이 아니라 범위가 다른 카드이므로 DB에 유지한다. 새 충돌 후보가
# 이 계열에서 높은 점수로 올라오면 원문 대조 후 위 목록에 추가하는 방식으로 관리한다.

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
                    body = re.sub(r'^\d+\.\s*', '', line).strip()
                    if body:  # 빈 항목(템플릿의 "1. " 등)은 유령 명제가 되므로 배제
                        claims.append(body)

        negates = []
        negates_match = re.search(r'## 부정 \(Negates\).*?(?=\n## |\n---|\Z)', sec, re.DOTALL)
        if negates_match:
            negates_text = negates_match.group(0)
            for line in negates_text.split('\n'):
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    body = re.sub(r'^\d+\.\s*', '', line).strip()
                    if body:
                        negates.append(body)

        # ── 교의 등급 → 심각도 tier (Level 자동 산출용, 2026-08-30 신설) ──
        # BUILD_PROMPT.md 등급표 기준: ☢️무류=4 / CCC·Sententia Certa=3 / 교회법·Communis=2 / 사목=1
        tier = 2
        gm = re.search(r'\|\s*\*\*교의 등급\*\*\s*\|\s*([^|]+)\|', sec)
        grade = gm.group(1).strip() if gm else ''
        if grade.startswith('De Fide'):
            # 'CCC 본문 자체는 무류 아님' 승계 표기가 있으면 CCC 본문 기준(3), 아니면 원 교의(4)
            tier = 3 if '무류 아님' in grade else 4
        elif 'Sententia Certa' in grade:
            tier = 3
        elif 'Sententia Communis' in grade:
            tier = 2
        elif 'Pastoral' in grade or '사목' in grade:
            tier = 1
        if card_id.upper().startswith('CANON'):
            tier = min(tier, 2)  # 교회법은 무류 아님 (BUILD_PROMPT 등급표)

        # "TRENT-S06-C32 — 선한 행위가 공로 없다 하면 파문" 형식의 제목에서
        # ID와 " — "/" " 구분자를 뗀 사람이 읽기 쉬운 이름만 남긴다.
        readable_title = re.sub(r'^\S+\s*[—-]?\s*', '', title).strip()
        if not readable_title:
            readable_title = title

        if card_id != "UNKNOWN" and card_id.strip() and (claims or negates):
            cards.append({
                'id': card_id,
                'title': readable_title,
                'file': os.path.basename(file_path),
                'claims': claims,
                'negates': negates,
                'tier': tier,
            })

    return cards

def main():
    print("가톨릭 교리 충돌 자동 탐지 엔진 (The Catholic Audit Engine) 실행 중...")

    all_cards = []
    for root, dirs, files in os.walk(DB_DIR):
        for file in files:
            if file.endswith('.md') and file != 'schema.md':  # schema.md의 카드 템플릿이 유령 카드로 파싱되는 것 방지
                all_cards.extend(parse_markdown(os.path.join(root, file)))

    if not all_cards:
        print("Error: 교리 카드(.md)를 찾을 수 없습니다.")
        return

    print(f"총 {len(all_cards)}개의 교리 카드를 파싱했습니다.")

    title_map = {card['id']: card['title'] for card in all_cards}
    tier_map = {card['id']: card.get('tier', 2) for card in all_cards}
    # BUILD_PROMPT '충돌 등급 매트릭스' — 두 카드 tier 조합 → Level 1~5
    _LEVEL = {(4,4):5,(4,3):4,(4,2):3,(4,1):2,(3,3):3,(3,2):3,(3,1):2,(2,2):2,(2,1):1,(1,1):1}
    def pair_level(a, b):
        ta, tb = tier_map.get(a, 2), tier_map.get(b, 2)
        return _LEVEL[(max(ta,tb), min(ta,tb))]

    claims_list = [] # (card_id, claim_text)
    negates_list = [] # (card_id, negate_text)

    for card in all_cards:
        for c in card['claims']:
            claims_list.append((card['id'], c))
        for n in card['negates']:
            negates_list.append((card['id'], n))

    print(f"추출 완료: 주장(Claims) {len(claims_list)}개, 부정(Negates) {len(negates_list)}개")
    print("의미론적 텍스트 유사도(Semantic Similarity) 분석 중...")

    print("다국어 의미론적 AI 임베딩(Sentence-Transformers) 모델을 로딩 중입니다...")
    print("(최초 실행 시 모델 다운로드에 1~2분 정도 소요될 수 있습니다.)")
    # 한국어 의미 파악에 뛰어난 다국어 모델 적용
    model = SentenceTransformer(_CFG['models']['embed_detect'])  # config.json

    print("텍스트의 진짜 의미를 벡터로 변환(Embedding)하고 있습니다...")
    claims_embeddings = model.encode([c[1] for c in claims_list], show_progress_bar=True)
    negates_embeddings = model.encode([n[1] for n in negates_list], show_progress_bar=True)

    similarity_matrix = cosine_similarity(claims_embeddings, negates_embeddings)
    claims_claims_matrix = cosine_similarity(claims_embeddings, claims_embeddings)

    # 카드별로 자기 자신의 claims 인덱스를 모아둔다 (cross-claim 재확인용)
    card_claim_indices = {}
    for idx, (cid, _) in enumerate(claims_list):
        card_claim_indices.setdefault(cid, []).append(idx)

    conflicts = []
    excluded = []
    # AI 임베딩은 문맥이 같으면 기본 유사도가 높게 나오므로 임계값을 0.60으로 상향 (기존 TF-IDF는 0.20)
    THRESHOLD = _CFG['thresholds']['detect_similarity']  # config.json

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
                'Level': pair_level(card_a, card_b),
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

    main_fields = ['Score', 'Level', 'Card_A_Claiming', 'Title_A', 'Card_B_Negating', 'Title_B', 'Claim_Text', 'Negate_Text']
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
