import csv
import re
import os
import sys

# Windows 콘솔 기본 코드페이지(cp949)는 이모지를 인코딩하지 못해 print에서 죽는 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 실행 위치와 무관하게 동작하도록 스크립트 위치 기준으로 경로를 고정한다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "07_REPORT", "auto_conflict_results.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "07_REPORT", "cvcap_combo_results.csv")

# Regex Rules for CVCAP 3.0 Filters
FILTERS = {
    "F1_REDUCTIO": re.compile(r"(원죄|무염|사망|죽음|마리아)", re.IGNORECASE),
    "F2_RUPTURE": re.compile(r"(TRENT|Florence|피렌체|LG-16|CCC-0847|바티칸|Vatican)", re.IGNORECASE),
    "F3_TOLLENS": re.compile(r"(완전한 통회|사제|필수|고해성사|CCC-1452)", re.IGNORECASE),
    "F4_ACTION_DOC": re.compile(r"(축복|Fiducia|본질적 악|동성|행위)", re.IGNORECASE),
    "F5_GOALPOST": re.compile(r"(림보|Limbo|가설|고성소|무류성|조건)", re.IGNORECASE),
    "F6_RETORSION": re.compile(r"(무류|해석|분열|Amoris|평신도|사제)", re.IGNORECASE),
    "F7_FALSE_DICH": re.compile(r"(단일|혼란|개신교|교도권)", re.IGNORECASE),
    "F8_SILENCE": re.compile(r"(승천|마리아|MUNIFICENTISSIMUS)", re.IGNORECASE)
}

def analyze():
    print("🚀 CVCAP 3.0 COMBO Engine Started...")
    
    # conflict_detector.py가 utf-8-sig(BOM)로 쓰므로 반드시 utf-8-sig로 읽는다
    # (utf-8로 읽으면 첫 컬럼명이 '﻿Score'가 되어 출력 CSV 헤더가 오염된다)
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['Hit_Filters', 'Combo_Name']
        rows = list(reader)

    combo_hits = []
    stats = {"COMBO-01_MARIOLOGY": 0, "COMBO-02_PAPACY": 0, "COMBO-03_SALVATION": 0}

    for row in rows:
        combined_text = f"{row.get('Title_A','')} {row.get('Title_B','')} {row.get('Claim_Text','')} {row.get('Negate_Text','')} {row.get('Card_A_Claiming','')} {row.get('Card_B_Negating','')}"
        
        hits = []
        for f_name, pattern in FILTERS.items():
            if pattern.search(combined_text):
                hits.append(f_name)
                
        combo_name = None
        # Combo 1: Mariology (F1 + F8 + F5) or at least two of them relating to Mary
        if "F1_REDUCTIO" in hits and "F8_SILENCE" in hits:
            combo_name = "COMBO-01_MARIOLOGY"
            stats[combo_name] += 1
            
        # Combo 2: Papacy (F6 + F7 + F2)
        elif "F6_RETORSION" in hits and "F7_FALSE_DICH" in hits:
            combo_name = "COMBO-02_PAPACY"
            stats[combo_name] += 1
            
        # Combo 3: Salvation (F2 + F3)
        elif "F2_RUPTURE" in hits and "F3_TOLLENS" in hits:
            combo_name = "COMBO-03_SALVATION"
            stats[combo_name] += 1
            
        # Combo 4: Purgatory/Merit (F1 + F4 + F8)
        elif "F1_REDUCTIO" in hits and "F4_ACTION_DOC" in hits:
            if "공로" in combined_text or "대사" in combined_text or "면죄부" in combined_text or "연옥" in combined_text or "CCC-1471" in combined_text:
                combo_name = "COMBO-04_PURGATORY"
                if "COMBO-04_PURGATORY" not in stats: stats["COMBO-04_PURGATORY"] = 0
                stats[combo_name] += 1

        # Combo 5: Moral Absolute/Fiducia (F2 + F4 + F5)
        elif "F4_ACTION_DOC" in hits and ("F2_RUPTURE" in hits or "F5_GOALPOST" in hits):
            if "Fiducia" in combined_text or "축복" in combined_text or "동성" in combined_text:
                combo_name = "COMBO-05_MORAL_COLLAPSE"
                if "COMBO-05_MORAL_COLLAPSE" not in stats: stats["COMBO-05_MORAL_COLLAPSE"] = 0
                stats[combo_name] += 1

        if combo_name:
            row['Hit_Filters'] = " | ".join(hits)
            row['Combo_Name'] = combo_name
            combo_hits.append(row)

    with open(OUTPUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combo_hits)

    # 주의: 아래 수치는 "키워드 필터 히트 건수"다. 논리적으로 확정된 모순 수가 아니며,
    # 확정은 LLM 심사/수작업 검증을 거쳐 05_COLLISION_CARDS에 카드로 등록해야 한다.
    print(f"✅ Total COMBO filter hits: {len(combo_hits)} (키워드 태깅 — 미확정 후보)")
    print("💥 Breakdown:")
    for k, v in stats.items():
        print(f"   - {k}: {v} rows tagged")

if __name__ == "__main__":
    analyze()
