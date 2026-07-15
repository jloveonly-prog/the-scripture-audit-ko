# -*- coding: utf-8 -*-
"""
CVCAP 3.0 파이프라인 무결성 자가 점검 (verify_pipeline.py)

전 계층(입력 DB → 탐지 CSV → LLM 심사 로그 → 확정 카드 → 인덱스 문서)의
정합성을 기계적으로 검증한다. 새 교리 카드 추가·파이프라인 재실행 후
`python scripts/verify_pipeline.py` 한 줄로 상태를 확인할 것.

종료 코드: 0 = 전체 통과, 1 = 실패 항목 존재
"""
import os
import re
import csv
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'scripts'))
from conflict_detector import parse_markdown, KNOWN_SAME_POSITION_PAIRS  # noqa: E402

DB_DIR = os.path.join(BASE, '04_DOCTRINE_DB')
RESULTS = os.path.join(BASE, '07_REPORT', 'auto_conflict_results.csv')
EXCLUDED = os.path.join(BASE, '07_REPORT', 'auto_conflict_excluded_self_negation.csv')
FULL_LOG = os.path.join(BASE, '07_REPORT', 'llm_judge_full_log.csv')
VERIFIED = os.path.join(BASE, '07_REPORT', 'llm_verified_conflicts.csv')
COMBO = os.path.join(BASE, '07_REPORT', 'cvcap_combo_results.csv')
CONFIRMED_DIR = os.path.join(BASE, '05_COLLISION_CARDS', 'confirmed')
GRAPH = os.path.join(BASE, '07_REPORT', 'conflict_network.html')

checks = []  # (통과여부, 이름, 상세)


def check(ok, name, detail=""):
    checks.append((ok, name, detail))
    mark = "✅" if ok else "❌"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))


def row_key(r):
    return (r.get('Card_A_Claiming', ''), r.get('Card_B_Negating', ''),
            r.get('Claim_Text', ''), r.get('Negate_Text', ''))


def read_csv(path):
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


print("=" * 60)
print("CVCAP 3.0 파이프라인 무결성 점검")
print("=" * 60)

# ── ① 입력층: 교리 카드 DB ──────────────────────────────────
print("\n[① 입력층 — 04_DOCTRINE_DB]")
cards = []
for root, dirs, files in os.walk(DB_DIR):
    for fn in files:
        if fn.endswith('.md') and fn != 'schema.md':
            cards.extend(parse_markdown(os.path.join(root, fn)))
ids = [c['id'] for c in cards]
dup = {i for i in ids if ids.count(i) > 1}
check(len(cards) > 0, f"교리 카드 파싱: {len(cards)}장")
check(not dup, "카드 ID 중복 없음", f"중복: {sorted(dup)}" if dup else "")
no_claims = [c['id'] for c in cards if not c['claims']]
no_negates = [c['id'] for c in cards if not c['negates']]
check(not no_claims, "모든 카드에 claims 존재", f"누락: {no_claims[:5]}" if no_claims else "")
check(not no_negates, "모든 카드에 negates 존재", f"누락: {no_negates[:5]}" if no_negates else "")
card_ids = set(ids)

# ── ② 탐지층: 충돌 후보 CSV ─────────────────────────────────
print("\n[② 탐지층 — auto_conflict_results.csv]")
res = read_csv(RESULTS)
exc = read_csv(EXCLUDED)
check(len(res) > 0, f"충돌 후보: {len(res)}건 / 제외: {len(exc)}건")
# Score는 소수 3자리 반올림 표기이므로 0.6004 → '0.6'이 정상 (원점수 필터는 detector가 > 0.60로 수행)
bad_score = [r for r in res if float(r['Score']) < 0.60]
check(not bad_score, "전 후보 유사도 ≥ 0.60 (임계값 준수, 반올림 표기 허용)", f"위반 {len(bad_score)}건" if bad_score else "")
self_pairs = [r for r in res if r['Card_A_Claiming'] == r['Card_B_Negating']]
check(not self_pairs, "자기 자신 카드 쌍 없음", f"위반 {len(self_pairs)}건" if self_pairs else "")
leaked = [r for r in res if frozenset({r['Card_A_Claiming'], r['Card_B_Negating']}) in KNOWN_SAME_POSITION_PAIRS]
check(not leaked, f"수작업 제외 목록({len(KNOWN_SAME_POSITION_PAIRS)}쌍) 누출 없음",
      f"누출 {len(leaked)}건: {[(r['Card_A_Claiming'], r['Card_B_Negating']) for r in leaked[:3]]}" if leaked else "")
scores = [float(r['Score']) for r in res]
check(scores == sorted(scores, reverse=True), "결과 Score 내림차순 정렬")
unknown_ids = {r['Card_A_Claiming'] for r in res} | {r['Card_B_Negating'] for r in res}
unknown_ids -= card_ids
check(not unknown_ids, "후보 CSV의 모든 카드 ID가 DB에 실존", f"미존재: {sorted(unknown_ids)[:5]}" if unknown_ids else "")

# ── ③ 심사층: LLM 판정 로그 ─────────────────────────────────
print("\n[③ 심사층 — llm_judge_full_log.csv]")
log = read_csv(FULL_LOG)
ver = read_csv(VERIFIED)
log_keys = {row_key(r): r for r in log}
res_keys = [row_key(r) for r in res]
uncovered = [k for k in res_keys if k not in log_keys]
check(not uncovered, f"전 후보({len(res)}건)에 판정 존재 (커버리지 100%)",
      f"미심사 {len(uncovered)}건" if uncovered else f"로그 {len(log)}건")
bad_dec = [r for r in log if r['LLM_Decision'] not in ('YES', 'NO')]
check(not bad_dec, "판정값 전부 YES/NO (ERROR 잔존 없음)", f"이상 {len(bad_dec)}건" if bad_dec else "")
log_yes = {row_key(r) for r in log if r['LLM_Decision'] == 'YES'}
ver_keys = {row_key(r) for r in ver}
check(log_yes == ver_keys, f"YES 목록 일치 (로그 {len(log_yes)}건 = 검증 CSV {len(ver)}건)",
      "" if log_yes == ver_keys else f"차이 {len(log_yes ^ ver_keys)}건")
no_reason = [r for r in log if r['LLM_Decision'] == 'YES' and not r.get('LLM_Reason', '').strip()]
check(not no_reason, "모든 YES 판정에 근거(LLM_Reason) 기록", f"누락 {len(no_reason)}건" if no_reason else "")

# ── ④ 카드층: 확정 충돌 카드 ────────────────────────────────
print("\n[④ 카드층 — 05_COLLISION_CARDS/confirmed]")
col_files = sorted(f for f in os.listdir(CONFIRMED_DIR) if re.match(r'COL_\d+\.md$', f))
nums = [int(re.search(r'\d+', f).group()) for f in col_files]
gaps = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
check(bool(col_files), f"확정 카드: {len(col_files)}장 (COL-001~{max(nums):03d})" if nums else "확정 카드 없음")
check(not gaps, "카드 번호 연속 (결번 없음)", f"결번: {gaps}" if gaps else "")
missing_refs = []
for f in col_files:
    body = open(os.path.join(CONFIRMED_DIR, f), encoding='utf-8').read()
    for cid in re.findall(r'\*\*문헌 [AB]\*\*: ([A-Z0-9_\-]+)', body):
        norm = cid.replace('_', '-')
        # 카드 파일들이 CCC_1257 표기와 CCC-1257 표기를 혼용하므로 둘 다 대조
        if cid not in card_ids and norm not in card_ids:
            missing_refs.append((f, cid))
check(not missing_refs, "카드가 인용한 문헌 ID가 DB에 실존(또는 구 표기)",
      f"미확인 {len(missing_refs)}건: {missing_refs[:4]}" if missing_refs else "")

# ── ⑤ 산출물·문서층 ────────────────────────────────────────
print("\n[⑤ 산출물·문서층]")
combo = read_csv(COMBO)
check(len(combo) > 0, f"콤보 태깅 CSV: {len(combo)}건")
combo_src = {row_key(r) for r in combo}
res_set = set(res_keys)
orphan_combo = [k for k in combo_src if k not in res_set]
check(not orphan_combo, "콤보 행이 전부 현행 후보 CSV의 부분집합", f"고아 {len(orphan_combo)}건" if orphan_combo else "")
graph_ok = os.path.exists(GRAPH) and os.path.getmtime(GRAPH) >= os.path.getmtime(RESULTS) - 3600
check(graph_ok, "네트워크 그래프가 후보 CSV 이후(±1h) 생성됨")
idx = open(os.path.join(BASE, '07_REPORT', 'REPORT_INDEX.md'), encoding='utf-8').read()
m = re.search(r'후보 \*\*([\d,]+)건\*\*', idx)
idx_n = int(m.group(1).replace(',', '')) if m else -1
check(idx_n == len(res), f"REPORT_INDEX 후보 수({idx_n}) = 실제 CSV({len(res)})")
m2 = re.search(r'COL-001~(\d+)', idx)
idx_col = int(m2.group(1)) if m2 else -1
check(nums and idx_col == max(nums), f"REPORT_INDEX 카드 범위(~{idx_col:03d}) = 실제 최대(COL-{max(nums):03d})" if nums else "카드 없음")

# ── 종합 ────────────────────────────────────────────────────
fails = [c for c in checks if not c[0]]
print("\n" + "=" * 60)
print(f"종합: {len(checks) - len(fails)}/{len(checks)} 통과" + ("" if not fails else f" — ❌ 실패 {len(fails)}건"))
for _, name, detail in fails:
    print(f"  ❌ {name}: {detail}")
print("=" * 60)
sys.exit(1 if fails else 0)
