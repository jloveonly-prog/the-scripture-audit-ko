# -*- coding: utf-8 -*-
"""CVCAP 3.0 — 1차 사료(원문) 수집기

04_DOCTRINE_DB/의 교리 카드가 인용한 문헌의 **원문**을 내려받아
04_DOCTRINE_DB/_SOURCE/ 에 저장한다. 이 원문이 있어야 verify_citations.py가
"카드의 인용문이 실제 원문과 일치하는가"를 기계적으로 검사할 수 있다.

BVCAP(the-scripture-audit)의 fetch_kjv_ko.py에 대응하는 CVCAP 버전이다.

⚖️ 저작권: CCC·바티칸2차·현대 교황 문서는 Libreria Editrice Vaticana 저작권 대상이다.
   _SOURCE/ 는 .gitignore로 제외되어 있으며, 로컬 검증 용도로만 보관한다.
   (KJV_KO_표준.json을 다루는 방식과 동일)
   트렌트·중세 공의회·19세기 교황 문서는 퍼블릭 도메인이다.

사용법:
    python scripts/fetch_sources.py          # 없는 것만 받음
    python scripts/fetch_sources.py --force  # 전부 다시 받음
"""
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE, '04_DOCTRINE_DB', '_SOURCE')
HEADERS = {'User-Agent': 'Mozilla/5.0 (CVCAP research; contact: local use only)'}
DELAY = 0.3  # 서버 예의상 요청 간 대기

FORCE = '--force' in sys.argv

# ── 단일 페이지 문서 목록 ────────────────────────────────────
# (파일명, URL, 퍼블릭도메인 여부)
DOCUMENTS = [
    # 트렌트 공의회 (1545~1563) — 퍼블릭 도메인
    ('trent_s05_original_sin.txt', 'https://www.papalencyclicals.net/councils/trent/fifth-session.htm', True),
    ('trent_s06_justification.txt', 'https://www.papalencyclicals.net/councils/trent/sixth-session.htm', True),
    ('trent_s07_sacraments_baptism.txt', 'https://www.papalencyclicals.net/councils/trent/seventh-session.htm', True),
    ('trent_s13_eucharist.txt', 'https://www.papalencyclicals.net/councils/trent/thirteenth-session.htm', True),
    ('trent_s14_penance.txt', 'https://www.papalencyclicals.net/councils/trent/fourteenth-session.htm', True),
    ('trent_s22_mass.txt', 'https://www.papalencyclicals.net/councils/trent/twenty-second-session.htm', True),
    ('trent_s24_marriage.txt', 'https://www.papalencyclicals.net/councils/trent/twenty-fourth-session.htm', True),
    ('trent_s25_purgatory_indulgences.txt', 'https://www.papalencyclicals.net/councils/trent/twenty-fifth-session.htm', True),

    # 중세·초기 공의회 — 퍼블릭 도메인
    ('council_constantinople_iii_681.txt', 'https://www.papalencyclicals.net/councils/ecum06.htm', True),
    ('council_nicaea_i_325.txt', 'https://www.papalencyclicals.net/councils/ecum01.htm', True),
    ('council_chalcedon_451.txt', 'https://www.papalencyclicals.net/councils/ecum04.htm', True),
    ('council_lateran_iv_1215.txt', 'https://www.papalencyclicals.net/councils/ecum12.htm', True),
    ('council_constance_1415.txt', 'https://www.papalencyclicals.net/councils/ecum16.htm', True),
    ('council_florence_1439.txt', 'https://www.papalencyclicals.net/councils/ecum17.htm', True),

    # 바티칸 1차 (1870) — 퍼블릭 도메인
    ('vatican1_pastor_aeternus.txt', 'https://www.papalencyclicals.net/councils/ecum20.htm', True),

    # 교황 문서 (19세기 이전) — 퍼블릭 도메인
    ('papal_unam_sanctam_1302.txt', 'https://www.papalencyclicals.net/bon08/b8unam.htm', True),
    ('papal_ineffabilis_deus_1854.txt', 'https://www.papalencyclicals.net/pius09/p9ineff.htm', True),
    ('papal_syllabus_errorum_1864.txt', 'https://www.papalencyclicals.net/pius09/p9syll.htm', True),

    # 바티칸 2차 (1962~65) — LEV 저작권, vatican.va 무료 공개
    ('vatican2_lumen_gentium.txt', 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19641121_lumen-gentium_en.html', False),
    ('vatican2_nostra_aetate.txt', 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651028_nostra-aetate_en.html', False),
    ('vatican2_dignitatis_humanae.txt', 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651207_dignitatis-humanae_en.html', False),
    ('vatican2_gaudium_et_spes.txt', 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19651207_gaudium-et-spes_en.html', False),

    # 20세기 이후 교황 문서 — LEV 저작권
    ('papal_munificentissimus_deus_1950.txt', 'https://www.vatican.va/content/pius-xii/en/apost_constitutions/documents/hf_p-xii_apc_19501101_munificentissimus-deus.html', False),
    # Amoris Laetitia는 vatican.va HTML판이 프레임 껍데기만 반환하므로 공식 PDF를 사용한다
    ('papal_amoris_laetitia_2016.txt', 'https://www.vatican.va/content/dam/francesco/pdf/apost_exhortations/documents/papa-francesco_esortazione-ap_20160319_amoris-laetitia_en.pdf', False),
    ('cdf_fiducia_supplicans_2023.txt', 'https://www.vatican.va/roman_curia/congregations/cfaith/documents/rc_ddf_doc_20231218_fiducia-supplicans_en.html', False),
    ('cdf_dominus_iesus_2000.txt', 'https://www.vatican.va/roman_curia/congregations/cfaith/documents/rc_con_cfaith_doc_20000806_dominus-iesus_en.html', False),
    ('itc_unbaptised_infants_2007.txt', 'https://www.vatican.va/roman_curia/congregations/cfaith/cti_documents/rc_con_cfaith_doc_20070419_un-baptised-infants_en.html', False),
    ('papal_fratelli_tutti_2020.txt', 'https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20201003_enciclica-fratelli-tutti.html', False),
    ('cdf_responsum_dubium_2021.txt', 'https://www.vatican.va/roman_curia/congregations/cfaith/documents/rc_con_cfaith_doc_20210222_responsum-dubium-unioni_en.html', False),
    ('papal_ordinatio_sacerdotalis_1994.txt', 'https://www.vatican.va/content/john-paul-ii/en/apost_letters/1994/documents/hf_jp-ii_apl_19940522_ordinatio-sacerdotalis.html', False),

    # 교회법전 (1983) — LEV 저작권
    ('canon_law_bk2_faithful_204_207.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib2-cann204-207_en.html', False),
    ('canon_law_bk2_people_208_329.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib2-cann208-329_en.html', False),
    ('canon_law_bk3_teaching_747_755.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib3-cann747-755_en.html', False),
    ('canon_law_bk6_penal_1311_1363.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib6-cann1311-1363_en.html', False),
    ('canon_law_bk6_penal_1364_1399.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib6-cann1364-1399_en.html', False),
    ('canon_law_bk4_marriage_998_1165.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib4-cann998-1165_en.html', False),
    ('canon_law_bk4_baptism.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib4-cann834-878_en.html', False),
    ('canon_law_bk4_eucharist.txt', 'https://www.vatican.va/archive/cod-iuris-canonici/eng/documents/cic_lib4-cann879-958_en.html', False),
]


def get(url):
    r = requests.get(url, timeout=60, headers=HEADERS)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() == 'iso-8859-1':
        r.encoding = r.apparent_encoding or 'utf-8'
    return r.text


def get_pdf_text(url):
    """PDF 문서를 내려받아 텍스트로 변환한다 (Amoris Laetitia 등 HTML판이 없는 문서용)."""
    import io

    from pypdf import PdfReader
    r = requests.get(url, timeout=120, headers=HEADERS)
    r.raise_for_status()
    reader = PdfReader(io.BytesIO(r.content))
    pages = [(p.extract_text() or '') for p in reader.pages]
    text = '\n'.join(pages)
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text('\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return '\n'.join(line.rstrip() for line in text.split('\n')).strip()


def fetch_documents():
    ok, skipped, failed = 0, 0, []
    for fname, url, public in DOCUMENTS:
        path = os.path.join(SRC_DIR, fname)
        if os.path.exists(path) and not FORCE:
            skipped += 1
            continue
        try:
            text = get_pdf_text(url) if url.lower().endswith('.pdf') else html_to_text(get(url))
            if len(text) < 500:
                raise ValueError(f'본문이 너무 짧음({len(text)}자) — 페이지 구조 변경 의심')
            tag = 'PUBLIC DOMAIN' if public else 'COPYRIGHT: Libreria Editrice Vaticana (로컬 검증용)'
            header = f'# SOURCE: {url}\n# LICENSE: {tag}\n# FETCHED: {time.strftime("%Y-%m-%d %H:%M")}\n\n'
            with open(path, 'w', encoding='utf-8') as f:
                f.write(header + text)
            print(f'  OK   {fname}  ({len(text):,}자)')
            ok += 1
            time.sleep(DELAY)
        except Exception as e:
            print(f'  FAIL {fname}: {e}')
            failed.append((fname, url, str(e)))
    return ok, skipped, failed


def fetch_ccc():
    """가톨릭 교회 교리서(CCC) 전문을 항번호별 JSON으로 저장."""
    out_path = os.path.join(SRC_DIR, 'ccc_en.json')
    if os.path.exists(out_path) and not FORCE:
        with open(out_path, encoding='utf-8') as f:
            existing = json.load(f)
        print(f'  SKIP ccc_en.json (이미 존재, {len(existing):,}항)')
        return existing

    root = 'https://www.vatican.va/archive/ENG0015/'
    idx = get(root + '_INDEX.HTM')
    pages = sorted({
        a.get('href') for a in BeautifulSoup(idx, 'html.parser').find_all('a')
        if a.get('href') and re.match(r'^__P[0-9A-Z]+\.HTM$', a.get('href'), re.I)
    })
    print(f'  CCC 본문 페이지 {len(pages)}개 수집 시작...')

    paras = {}
    for i, page in enumerate(pages, 1):
        try:
            html = get(root + page)
        except Exception as e:
            print(f'    FAIL {page}: {e}')
            continue
        soup = BeautifulSoup(html, 'html.parser')
        # CCC 본문은 <p>번호 본문</p> 뒤에 번호 없는 <p>인용문</p>이 이어지는 구조다
        # (예: 847은 리드인 문장 + 다음 <p>의 LG16 인용문으로 구성).
        # 번호 없는 단락은 직전 항에 이어붙여야 인용 검증이 정확해진다.
        page_paras = {}
        current = None
        for p in soup.find_all('p'):
            txt = re.sub(r'\s+', ' ', p.get_text(' ', strip=False)).strip()
            if not txt:
                continue
            m = re.match(r'^(\d{1,4})\s+(\S.*)$', txt)
            if m and 1 <= int(m.group(1)) <= 2865 and len(m.group(2).strip()) >= 25:
                current = int(m.group(1))
                page_paras[current] = m.group(2).strip()
            elif current is not None and len(txt) >= 25 and not re.match(r'^\d{1,4}$', txt):
                # 번호 없는 후속 단락 = 직전 항의 인용문/연속 문단
                page_paras[current] += '\n' + txt
        for num, body in page_paras.items():
            # 같은 번호가 여러 페이지에 나오면 가장 긴 본문 채택(목차·상호참조 배제)
            if num not in paras or len(body) > len(paras[num]):
                paras[num] = body
        if i % 50 == 0:
            print(f'    ...{i}/{len(pages)} 페이지, 누적 {len(paras):,}항')
        time.sleep(DELAY)

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({str(k): v for k, v in sorted(paras.items())}, f,
                  ensure_ascii=False, indent=1)
    print(f'  OK   ccc_en.json  ({len(paras):,}항 / 전체 2865항 기준 {len(paras)/2865*100:.1f}%)')
    return paras


def check_gitignore_protection():
    """⚖️ 저작권 안전장치: _SOURCE가 gitignore로 보호되지 않으면 실행을 거부한다.

    이 스크립트는 LEV(교황청 출판사) 저작권 원문 전문을 내려받는다. 어느 저장소에
    복사되어 실행되든(KO/EN 무관), 받은 파일이 실수로 커밋·push되는 일을 코드
    수준에서 차단한다 — .gitignore 규칙에만 의존하지 않는 이중 방어다.
    """
    import subprocess
    probe = os.path.join(SRC_DIR, '__copyright_probe__.txt')
    try:
        r = subprocess.run(['git', 'check-ignore', '-q', probe],
                           cwd=BASE, capture_output=True)
    except FileNotFoundError:
        return  # git 자체가 없으면(저장소 밖 실행) 커밋 위험도 없음
    if r.returncode != 0:
        rel = os.path.relpath(SRC_DIR, BASE).replace('\\', '/')
        print('=' * 60)
        print('❌ 실행 중단 — 저작권 보호 실패')
        print(f'  {rel}/ 가 이 저장소의 .gitignore에 등록되어 있지 않습니다.')
        print('  이 스크립트가 받는 원문에는 LEV(교황청 출판사) 저작권 문헌이')
        print('  포함되므로, 보호 없이 받으면 커밋·push로 유출될 수 있습니다.')
        print('  .gitignore에 다음 한 줄을 추가한 뒤 다시 실행하십시오:')
        print(f'    {rel}/')
        print('=' * 60)
        sys.exit(2)


def main():
    check_gitignore_protection()
    os.makedirs(SRC_DIR, exist_ok=True)
    print('=' * 60)
    print('CVCAP 3.0 — 1차 사료 수집')
    print('=' * 60)

    print('\n[1] 단일 페이지 문서')
    ok, skipped, failed = fetch_documents()
    print(f'  → 신규 {ok}건 / 기존 {skipped}건 / 실패 {len(failed)}건')

    print('\n[2] 가톨릭 교회 교리서 (CCC)')
    ccc = fetch_ccc()

    print('\n' + '=' * 60)
    print(f'저장 위치: {SRC_DIR}')
    print(f'CCC 항목: {len(ccc):,}개')
    if failed:
        print(f'\n실패 {len(failed)}건 — 수동 확인 필요:')
        for fname, url, err in failed:
            print(f'  - {fname}\n    {url}\n    {err}')
    print('=' * 60)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
