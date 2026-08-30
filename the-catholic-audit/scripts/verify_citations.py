# -*- coding: utf-8 -*-
"""CVCAP 3.0 — 교리 카드 인용문 ↔ 1차 사료 대조 검증기

04_DOCTRINE_DB/의 각 교리 카드가 인용한 "원문 (요약)"이 실제 원문
(04_DOCTRINE_DB/_SOURCE/, fetch_sources.py 수집분)과 실제로 일치하는지
기계적으로 검사한다.

카드는 한국어, 원문은 영어이므로 단순 문자열 비교가 불가능하다. 따라서
conflict_detector.py가 이미 쓰는 다국어 임베딩 모델을 재사용해
**교차언어 의미 유사도**로 대조한다.

⚠️ 모델 선택 이력 (중요):
  최초에는 conflict_detector.py와 같은 `paraphrase-multilingual-MiniLM-L12-v2`를
  썼으나, 한국어↔영어 교차 대조에서 신뢰할 수 없음이 실측으로 드러났다.
  (예: 카드 CCC-1996의 한국어 인용문 대 실제 CCC 1996 영문 = 0.580 인데,
   전혀 무관한 CCC 2786("주님의 기도"의 '우리') = 0.698 로 더 높게 나옴.)
  따라서 본 검증기는 교차언어 문장 정합 전용으로 학습된 **LaBSE**를 쓴다.
  같은 예시에서 LaBSE는 CCC 1996 = 0.740 > CCC 2786 = 0.517 로 올바르게 정렬한다.
  ※ conflict_detector.py는 한국어 카드끼리(단일 언어) 비교하므로 기존 모델 유지가 맞다.

판정 기준 (LaBSE 척도):
  ✅ VERIFIED  (≥ 0.65)  원문에 대응 구절이 확실히 존재
  🟡 WEAK      (0.50~0.65) 대응 구절로 보이나 요약·의역 폭이 큼 — 사람 확인 권장
  ❌ SUSPECT   (< 0.50)   원문에서 대응 구절을 찾지 못함 — 환각 의심, 최우선 검토
  📍 MISLOCATED          내용은 원문에 있으나 카드 ID가 가리키는 위치가 아님

사용법:
    python scripts/verify_citations.py            # 전체 검증
    python scripts/verify_citations.py --json     # 결과를 JSON으로도 저장
"""
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'scripts'))

DB_DIR = os.path.join(BASE, '04_DOCTRINE_DB')
SRC_DIR = os.path.join(DB_DIR, '_SOURCE')
OUT_JSON = os.path.join(BASE, '07_REPORT', 'citation_verification.json')

VERIFIED_T = 0.65
WEAK_T = 0.50
MODEL_NAME = 'sentence-transformers/LaBSE'  # 교차언어 전용 (상단 주석 참조)

# 카드 ID 접두어 → 대조할 사료 파일(들)
# 값이 여러 개면 전부 뒤져 가장 높은 점수를 채택한다.
SOURCE_MAP = [
    (r'^CCC[-_]', ['ccc_en.json']),
    (r'^TRENT[-_]S0?5', ['trent_s05_original_sin.txt']),
    (r'^TRENT[-_]S0?6', ['trent_s06_justification.txt']),
    (r'^TRENT[-_]S0?7', ['trent_s07_sacraments_baptism.txt']),
    (r'^TRENT[-_]S13', ['trent_s13_eucharist.txt']),
    (r'^TRENT[-_]S14', ['trent_s14_penance.txt']),
    (r'^TRENT[-_]S22', ['trent_s22_mass.txt']),
    (r'^TRENT[-_]S24', ['trent_s24_marriage.txt']),
    (r'^TRENT[-_]S25', ['trent_s25_purgatory_indulgences.txt']),
    (r'^TRENT', ['trent_s06_justification.txt', 'trent_s07_sacraments_baptism.txt',
                 'trent_s13_eucharist.txt', 'trent_s14_penance.txt']),
    (r'^(COUNCIL[-_])?CONST_III|CONSTANTINOPLE', ['council_constantinople_iii_681.txt']),
    (r'NICAEA|CHALCEDON', ['council_nicaea_i_325.txt', 'council_chalcedon_451.txt']),
    (r'^(COUNCIL[-_])?LATERAN', ['council_lateran_iv_1215.txt']),
    (r'^(COUNCIL[-_])?CONSTANCE', ['council_constance_1415.txt']),
    (r'^(COUNCIL[-_])?FLORENCE', ['council_florence_1439.txt']),
    (r'^VAT1|PASTOR[-_]AETERNUS', ['vatican1_pastor_aeternus.txt']),
    (r'^(PAPAL[-_])?UNAM', ['papal_unam_sanctam_1302.txt']),
    (r'INEFFABILIS|PAPAL[-_]INEFF', ['papal_ineffabilis_deus_1854.txt']),
    (r'MUNIFICENTISSIMUS|PAPAL[-_]MUNIF', ['papal_munificentissimus_deus_1950.txt']),
    (r'SYLLABUS', ['papal_syllabus_errorum_1864.txt']),
    (r'^LG[-_]|LUMEN|VATICAN2[-_]LG', ['vatican2_lumen_gentium.txt']),
    (r'NOSTRA|VATICAN2[-_]NA', ['vatican2_nostra_aetate.txt']),
    (r'DIGNITATIS|VATICAN2[-_]DH', ['vatican2_dignitatis_humanae.txt']),
    (r'GAUDIUM|VATICAN2[-_]GS', ['vatican2_gaudium_et_spes.txt']),
    (r'AMORIS', ['papal_amoris_laetitia_2016.txt']),
    (r'FRATELLI', ['papal_fratelli_tutti_2020.txt']),
    (r'ITC|LIMBO', ['itc_unbaptised_infants_2007.txt']),
    (r'FIDUCIA', ['cdf_fiducia_supplicans_2023.txt']),
    (r'DOMINUS', ['cdf_dominus_iesus_2000.txt']),
    (r'^CANON[-_]PENAL', ['canon_law_bk6_penal_1311_1363.txt', 'canon_law_bk6_penal_1364_1399.txt']),
    (r'^CANON', ['canon_law_bk2_faithful_204_207.txt', 'canon_law_bk2_people_208_329.txt',
                 'canon_law_bk3_teaching_747_755.txt', 'canon_law_bk4_baptism.txt',
                 'canon_law_bk4_eucharist.txt', 'canon_law_bk6_penal_1311_1363.txt',
                 'canon_law_bk6_penal_1364_1399.txt', 'canon_law_bk4_marriage_998_1165.txt']),
    # DENZINGER는 원문 모음집 자체를 받지 못했다(저작권/미공개) — 개별 문서로 우회 대조
    (r'^DENZINGER[-_]FEENEY', ['__NO_SOURCE__']),
    (r'^DENZINGER', ['papal_syllabus_errorum_1864.txt']),
    (r'ORDINATIO', ['papal_ordinatio_sacerdotalis_1994.txt']),
    (r'RESPONSUM', ['cdf_responsum_dubium_2021.txt']),
    (r'^CDF', ['cdf_fiducia_supplicans_2023.txt', 'cdf_dominus_iesus_2000.txt',
               'cdf_responsum_dubium_2021.txt']),
]

CHUNK_MIN = 40

ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII',
         9: 'IX', 10: 'X', 11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV',
         16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX', 21: 'XXI',
         22: 'XXII', 23: 'XXIII', 24: 'XXIV', 25: 'XXV', 26: 'XXVI', 27: 'XXVII',
         28: 'XXVIII', 29: 'XXIX', 30: 'XXX', 31: 'XXXI', 32: 'XXXII', 33: 'XXXIII'}


def targeted_passages(card_id, cache):
    """카드 ID가 위치를 특정하면(CCC 항번호, 트렌트 캐논 번호) 해당 후보들을 집어온다.

    전역 최대 유사도 검색은 짧은 인용문에서 엉뚱한 곳에 걸리기 쉽다
    (예: CCC-1996이 CCC 2786에 매칭). 위치를 아는 카드는 그 자리를 직접 대조한다.

    ⚠️ 후보를 **리스트로** 반환하는 이유:
      ① 범위 카드(CCC-1030_1032)를 하나로 이어붙이면 관련 없는 항이 섞여 점수가
         희석된다 → 범위 내 각 항을 개별 후보로 넣고 최고점을 채택한다.
      ② 트렌트 한 회기 안에 같은 번호의 캐논이 여러 계열로 존재한다
         (7차 회기 = "성사 일반 CANON V" + "세례 CANON V"). 하나만 집으면
         엉뚱한 계열을 잡는다 → 같은 번호를 전부 후보로 넣는다.
    반환: [(위치표시, 원문), ...]
    """
    cid = card_id.upper().replace('_', '-')
    out = []

    # CCC-1996 / CCC-1257-1261(범위) / CCC-0847(0 패딩)
    m = re.match(r'^CCC-(\d{1,4})(?:-(\d{1,4}))?$', cid)
    if m and 'ccc_en.json' in cache:
        data = dict(cache['ccc_en.json'][2])  # {'CCC 1996': text}
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
        if end < start:
            end = start
        for n in range(start, min(end, start + 80) + 1):
            t = data.get(f'CCC {n}')
            if t:
                out.append((f'CCC {n}', t))
        if out:
            return out

    # TRENT-S06-C09 → 해당 세션 파일에서 "CANON IX"인 문단 전부
    m = re.match(r'^TRENT-S0?(\d{1,2})-C0?(\d{1,2})$', cid)
    if m:
        roman = ROMAN.get(int(m.group(2)))
        for fname, (chunks, _emb, _d) in cache.items():
            if not fname.startswith('trent_s') or f's{int(m.group(1)):02d}' not in fname:
                continue
            for _loc, text in chunks:
                if roman and re.search(rf'CANON\s+{roman}[\.\-— ]', text, re.I):
                    out.append((f'{fname} CANON {roman}', text))
    return out


def pick_sources(card_id):
    cid = card_id.upper()
    for pat, files in SOURCE_MAP:
        if re.search(pat, cid):
            return files
    return []


def load_chunks(fname):
    """사료 파일을 대조 단위(문단)로 쪼갠다."""
    path = os.path.join(SRC_DIR, fname)
    if fname == 'ccc_en.json':
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return [(f'CCC {k}', v) for k, v in data.items() if len(v) >= CHUNK_MIN]
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'^#.*$', '', text, flags=re.M)  # 헤더 주석 제거
    chunks = []
    for para in re.split(r'\n\s*\n', text):
        para = re.sub(r'\s+', ' ', para).strip()
        if len(para) >= CHUNK_MIN:
            chunks.append((fname, para))
    return chunks


def extract_quote(section):
    """카드의 '## 원문 (요약)' 블록에서 인용문을 뽑는다."""
    m = re.search(r'## 원문 ?\(요약\)(.*?)(?=\n## |\Z)', section, re.S)
    if not m:
        return ''
    body = m.group(1)
    lines = [re.sub(r'^>\s?', '', ln).strip() for ln in body.split('\n')]
    return re.sub(r'\s+', ' ', ' '.join(l for l in lines if l)).strip()


def main():
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    from conflict_detector import parse_markdown

    if not os.path.isdir(SRC_DIR):
        print(f'에러: 사료 폴더가 없습니다 — 먼저 `python scripts/fetch_sources.py`를 실행하세요.\n  {SRC_DIR}')
        return 2

    # ── 카드 수집 (인용문 포함) ──
    cards = []
    for root, _, files in os.walk(DB_DIR):
        if '_SOURCE' in root:
            continue
        for fn in files:
            if not fn.endswith('.md') or fn == 'schema.md':
                continue
            path = os.path.join(root, fn)
            parsed = {c['id']: c for c in parse_markdown(path)}
            with open(path, encoding='utf-8') as f:
                content = f.read()
            for sec in re.split(r'\n# ', '\n' + content)[1:]:
                idm = re.search(r'\|\s*\*\*ID\*\*\s*\|\s*([^|]+)\|', sec)
                if not idm:
                    continue
                cid = idm.group(1).strip()
                if cid not in parsed:
                    continue
                cards.append({'id': cid, 'file': fn, 'quote': extract_quote(sec),
                              'title': parsed[cid]['title']})

    print('=' * 66)
    print('CVCAP 3.0 — 교리 카드 인용문 ↔ 1차 사료 대조 검증')
    print('=' * 66)
    print(f'카드 {len(cards)}장 / 사료 폴더 {SRC_DIR}\n')

    no_quote = [c for c in cards if not c['quote']]
    targets = [c for c in cards if c['quote']]
    if no_quote:
        print(f'⚠️ 인용문(## 원문 (요약)) 없는 카드 {len(no_quote)}장 — 대조 불가:')
        for c in no_quote[:10]:
            print(f'    {c["id"]} ({c["file"]})')
        print()

    print(f'교차언어 임베딩 모델 로딩 중... ({MODEL_NAME})')
    model = SentenceTransformer(MODEL_NAME)

    # 필요한 사료만 로딩·임베딩 (파일 단위 캐시)
    needed = set()
    for c in targets:
        needed.update(pick_sources(c['id']))
    needed.discard('__NO_SOURCE__')

    cache = {}
    for fname in sorted(needed):
        chunks = load_chunks(fname)
        if not chunks:
            print(f'  ⚠️ 사료 없음/비어있음: {fname}')
            continue
        print(f'  임베딩: {fname} ({len(chunks):,} 단락)')
        emb = model.encode([t for _, t in chunks], show_progress_bar=False,
                           batch_size=256)
        cache[fname] = (chunks, emb, chunks)

    print('\n카드 인용문 임베딩 및 대조 중...\n')
    q_emb = model.encode([c['quote'] for c in targets], show_progress_bar=False)

    results = []
    for i, c in enumerate(targets):
        # ① 위치 특정 대조 (CCC 항번호·트렌트 캐논 번호를 아는 경우) — 이 점수가 정답이다
        cands = targeted_passages(c['id'], cache)
        targeted = None
        if cands:
            t_emb = model.encode([t for _, t in cands], show_progress_bar=False)
            sims = cosine_similarity(q_emb[i:i + 1], t_emb)[0]
            k = int(sims.argmax())
            targeted = (float(sims[k]), cands[k][0], cands[k][1])

        # ② 전역 검색 — 카드가 실제로는 다른 위치를 인용한 것은 아닌지 확인
        glob = (0.0, None, None)
        for fname in pick_sources(c['id']):
            if fname not in cache:
                continue
            chunks, emb, _ = cache[fname]
            sims = cosine_similarity(q_emb[i:i + 1], emb)[0]
            j = int(sims.argmax())
            if sims[j] > glob[0]:
                glob = (float(sims[j]), chunks[j][0], chunks[j][1])

        # 위치를 특정할 수 있으면 그 점수를 채택한다. 전역 최고점이 지정 위치보다
        # 뚜렷하게(+0.08) 높으면 "내용은 맞는데 카드 ID가 가리키는 자리가 아니다"(MISLOCATED).
        mislocated = False
        if targeted:
            score, loc, passage = targeted
            if glob[0] > score + 0.08 and glob[1] != loc:
                mislocated = True
                alt_loc, alt_score = glob[1], glob[0]
        else:
            score, loc, passage = glob
        status = ('VERIFIED' if score >= VERIFIED_T
                  else 'WEAK' if score >= WEAK_T
                  else 'SUSPECT')
        if not pick_sources(c['id']) or all(f == '__NO_SOURCE__' for f in pick_sources(c['id'])):
            status = 'NO_SOURCE'
        elif mislocated and status != 'SUSPECT':
            status = 'MISLOCATED'
        row = {'id': c['id'], 'file': c['file'], 'title': c['title'],
               'score': round(score, 3), 'status': status,
               'matched_at': loc, 'quote': c['quote'],
               'source_passage': (passage or '')[:400]}
        if mislocated:
            row['better_match_at'] = alt_loc
            row['better_match_score'] = round(alt_score, 3)
        results.append(row)

    order = {'SUSPECT': 0, 'MISLOCATED': 1, 'NO_SOURCE': 2, 'WEAK': 3, 'VERIFIED': 4}
    results.sort(key=lambda r: (order[r['status']], r['score']))

    counts = {}
    for r in results:
        counts[r['status']] = counts.get(r['status'], 0) + 1

    icon = {'VERIFIED': '✅', 'WEAK': '🟡', 'SUSPECT': '❌', 'NO_SOURCE': '⬜', 'MISLOCATED': '📍'}
    for r in results:
        if r['status'] == 'VERIFIED':
            continue
        print(f'{icon[r["status"]]} [{r["score"]:.3f}] {r["id"]:24s} {r["title"][:34]}')
        if r.get('better_match_at'):
            print(f'      → 지정 위치({r["matched_at"]})보다 {r["better_match_at"]} 가 더 일치 ({r["better_match_score"]})')
        if r['status'] in ('SUSPECT', 'WEAK', 'MISLOCATED'):
            print(f'      카드: {r["quote"][:120]}')
            print(f'      원문({r["matched_at"]}): {r["source_passage"][:120]}')

    print('\n' + '=' * 66)
    total = len(results)
    for st in ['VERIFIED', 'WEAK', 'MISLOCATED', 'SUSPECT', 'NO_SOURCE']:
        n = counts.get(st, 0)
        if n:
            print(f'{icon[st]} {st:10s} {n:3d}장  ({n / total * 100:.1f}%)')
    print(f'   합계        {total:3d}장')
    print('=' * 66)

    if '--json' in sys.argv:
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        with open(OUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        print(f'\n상세 결과 저장: {OUT_JSON}')

    return 1 if counts.get('SUSPECT') else 0


if __name__ == '__main__':
    sys.exit(main())
