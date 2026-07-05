import os
import re
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_DIR = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\05_DOCTRINE_DB"
REPORT_FILE = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\auto_conflict_results.csv"

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
    
    conflicts = []
    THRESHOLD = 0.20 # 유사도 임계값
    
    for i, c_item in enumerate(claims_list):
        for j, n_item in enumerate(negates_list):
            card_a = c_item[0]
            card_b = n_item[0]
            
            # 자기 자신 카드 내의 충돌은 제외 (외부 충돌만 탐지)
            if card_a == card_b:
                continue
                
            sim_score = similarity_matrix[i, j]
            if sim_score > THRESHOLD:
                conflicts.append({
                    'Score': round(sim_score, 3),
                    'Card_A_Claiming': card_a,
                    'Card_B_Negating': card_b,
                    'Claim_Text': c_item[1],
                    'Negate_Text': n_item[1]
                })
                
    conflicts.sort(key=lambda x: x['Score'], reverse=True)
    
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Score', 'Card_A_Claiming', 'Card_B_Negating', 'Claim_Text', 'Negate_Text'])
        writer.writeheader()
        writer.writerows(conflicts)
        
    print(f"분석 완료! 총 {len(conflicts)}건의 논리적 충돌(A Not A) 의심 사례가 발견되었습니다.")
    print(f"상세 결과가 CSV 형식으로 저장되었습니다: {REPORT_FILE}\n")
    
    print("🔥 [엔진이 찾아낸 충돌 유사도 상위 3건] 🔥")
    for idx, c in enumerate(conflicts[:3]):
        print(f"#{idx+1} [유사도 {c['Score']}] {c['Card_A_Claiming']} vs {c['Card_B_Negating']}")
        print(f"   [A의 주장] {c['Claim_Text']}")
        print(f"   [B가 부정함] {c['Negate_Text']}\n")

if __name__ == '__main__':
    main()
