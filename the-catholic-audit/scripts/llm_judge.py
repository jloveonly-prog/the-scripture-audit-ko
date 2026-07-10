import os
import csv
import json
import re
import sys
import time
import shutil
import subprocess

# Windows 콘솔 기본 코드페이지(cp949)는 이모지를 인코딩하지 못해 print에서 죽는 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ──────────────────────────────────────────────────────────────────────────
# LLM-as-a-Judge — Claude Code CLI 헤드리스 모드 사용 (별도 API 키 불필요)
#   - 로그인된 Claude Code CLI(`claude -p`)를 서브프로세스로 호출하므로
#     GEMINI_API_KEY 같은 환경 변수 설정이 필요 없다.
#   - CLI 호출 1회당 기동 비용이 있으므로 후보를 BATCH_SIZE개씩 묶어 심사한다.
# ──────────────────────────────────────────────────────────────────────────
CSV_PATH = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\auto_conflict_results.csv"
OUTPUT_PATH = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\llm_verified_conflicts.csv"
FULL_LOG_PATH = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\llm_judge_full_log.csv"

# 사용법:
#   python llm_judge.py next [N]   — 아직 심사하지 않은 후보 중 순위 상위 N건만 심사 (기본 100)
#                                    ★ 비용 분할용 권장 모드: 몇 번을 나눠 실행해도 이어서 진행됨
#   python llm_judge.py [N] [START] — 순위 START부터 N건 심사 (수동 구간 지정)
NEXT_MODE = len(sys.argv) > 1 and sys.argv[1].lower() == 'next'
if NEXT_MODE:
    TOP_N = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    START = 1  # next 모드에서는 미사용
else:
    TOP_N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    START = int(sys.argv[2]) if len(sys.argv) > 2 else 1
BATCH_SIZE = 10          # CLI 호출 1회당 심사 건수
MODEL = "haiku"          # 예/아니오 판정용 — 빠르고 저렴. 정밀 재심사 시 "sonnet"으로 상향
TIMEOUT_SEC = 600        # 배치 1회 호출 제한 시간


def row_key(r):
    """카드 쌍 + 명제 텍스트로 후보를 식별 (재실행 시 행 번호가 변해도 병합 가능)"""
    return (r.get('Card_A_Claiming', ''), r.get('Card_B_Negating', ''),
            r.get('Claim_Text', ''), r.get('Negate_Text', ''))


def build_prompt(batch):
    """batch: [(전역 인덱스, row), ...] — 한 번의 CLI 호출로 묶어 심사할 프롬프트 생성"""
    items = "\n\n".join(
        f"[{i}]\n"
        f"문서 A({r['Card_A_Claiming']})의 공식 주장: \"{r['Claim_Text']}\"\n"
        f"문서 B({r['Card_B_Negating']})가 '단죄(부정)'하는 이단적 명제: \"{r['Negate_Text']}\""
        for i, r in batch
    )
    return f"""당신은 가톨릭 신학 및 교리 논리 분석 전문가입니다.
아래 각 항목의 두 명제를 읽고, 가톨릭 신학의 맥락에서 두 문서가 논리적으로 정면 충돌(모순)하는지 엄격하게 판단하세요.

[판단 기준]
- "예"의 유일한 조건: 문서 A가 '옳다'고 주장하는 명제가, 문서 B가 '틀렸다'고 단죄하는 명제와 **사실상 동일**할 때 (= A가 주장하는 바로 그것을 B가 단죄함).
- ⚠️ 방향 주의: A의 주장이 B의 단죄 명제와 **모순·반대**된다면, 그것은 A와 B가 그 명제를 **함께 배격하는 동일 입장**이라는 뜻이므로 반드시 "아니오".
  (예: A가 "계명 준수는 구원에 필수"라고 주장하고 B가 "죄를 지어도 구원을 잃지 않는다"를 단죄한다면,
   둘 다 같은 것을 배격하는 같은 편이므로 "아니오"다.)
- 두 문장이 단순히 같은 주제(예: 은총, 세례)를 다룰 뿐 주장하는 바가 다르면 "아니오".
- 역사적으로 이미 해결되었거나, 예외 조항(적용 대상의 차이)으로 양립 가능한 경우도 "아니오".

[검토 항목]
{items}

[출력 형식 — 반드시 준수]
다른 설명 없이 아래 형식의 JSON 배열 하나만 출력하세요. 모든 항목 번호를 빠짐없이 포함하세요.
[{{"idx": <항목 번호>, "verdict": "예" 또는 "아니오", "reason": "1~2문장 근거"}}, ...]"""


def call_claude_cli(claude_bin, prompt, retries=2):
    """claude -p 헤드리스 호출. stdout에서 JSON 배열을 추출해 반환한다.
    연속 고속 호출 시 일시적 실패(rate limit 등)가 실측되어, 실패 시 백오프 후 재시도한다."""
    last_err = None
    for attempt in range(retries + 1):
        if attempt > 0:
            wait = 30 * attempt  # 30초, 60초 백오프
            print(f"    ({attempt}차 재시도 — {wait}초 대기)")
            time.sleep(wait)
        try:
            result = subprocess.run(
                [claude_bin, "-p", prompt, "--model", MODEL],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=TIMEOUT_SEC,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"claude CLI 종료 코드 {result.returncode}: "
                    f"stderr={(result.stderr or '').strip()[:200]} stdout={(result.stdout or '').strip()[:200]}"
                )
            text = (result.stdout or "").strip()
            # ```json 펜스나 앞뒤 설명이 섞여도 첫 번째 JSON 배열만 뽑아낸다
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if not match:
                raise ValueError(f"응답에서 JSON 배열을 찾지 못함: {text[:200]}")
            return json.loads(match.group(0))
        except Exception as e:
            last_err = e
    raise last_err


def main():
    claude_bin = shutil.which("claude")
    if not claude_bin:
        print("에러: claude CLI를 찾을 수 없습니다. Claude Code가 설치·로그인되어 있어야 합니다.")
        return

    if not os.path.exists(CSV_PATH):
        print(f"파일이 존재하지 않습니다: {CSV_PATH}")
        return

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        all_candidates = list(csv.DictReader(f))

    if NEXT_MODE:
        # 이미 심사된 후보(YES/NO — ERROR는 재심사 대상)를 로그에서 읽어 건너뛴다
        done_keys = set()
        if os.path.exists(FULL_LOG_PATH):
            with open(FULL_LOG_PATH, 'r', encoding='utf-8-sig') as f:
                for r in csv.DictReader(f):
                    if r.get('LLM_Decision') in ('YES', 'NO'):
                        done_keys.add(row_key(r))
        pending = [(i, r) for i, r in enumerate(all_candidates, start=1) if row_key(r) not in done_keys]
        if not pending:
            print("🎉 전체 후보 심사 완료 — 미심사 잔여 0건입니다.")
            return
        if TOP_N <= 0:
            print(f"미심사 잔여 {len(pending)}건 / 전체 {len(all_candidates)}건 (N=0 — 현황만 표시하고 종료)")
            return
        print(f"미심사 잔여 {len(pending)}건 / 전체 {len(all_candidates)}건 — 이번 단계에서 상위 {min(TOP_N, len(pending))}건을 심사합니다.")
        indexed = pending[:TOP_N]
        candidates = [r for _, r in indexed]
    else:
        # 유사도(Score) 순으로 이미 정렬되어 있다고 가정하고 START~START+N-1 구간 추출
        candidates = all_candidates[START - 1:START - 1 + TOP_N]
        if not candidates:
            print(f"심사할 후보가 없습니다 (START={START}, N={TOP_N}).")
            return
        indexed = list(enumerate(candidates, start=START))

    print(f"{indexed[0][0]}~{indexed[-1][0]}위 범위의 후보 {len(candidates)}건을 {BATCH_SIZE}건씩 묶어 LLM 정밀 심사(LLM-as-a-Judge, claude CLI/{MODEL})를 시작합니다...")

    verified_conflicts = []
    judged_rows = []  # YES/NO/ERROR 전체 기록 (감사 추적용)
    for start in range(0, len(indexed), BATCH_SIZE):
        batch = indexed[start:start + BATCH_SIZE]
        first, last = batch[0][0], batch[-1][0]
        print(f"[진행 {start + len(batch)}/{len(candidates)} — 순위 {first}~{last}위] 배치 심사 중...", flush=True)
        try:
            verdicts = call_claude_cli(claude_bin, build_prompt(batch))
            verdict_map = {int(v.get("idx", -1)): v for v in verdicts if isinstance(v, dict)}
        except Exception as e:
            print(f"  ⚠️ 배치 호출 실패 — 해당 배치 전체를 ERROR로 기록: {e}")
            verdict_map = {}

        for i, row in batch:
            v = verdict_map.get(i)
            if v is None:
                row['LLM_Decision'] = 'ERROR'
                row['LLM_Reason'] = '응답 누락 또는 배치 호출 실패 — 재심사 필요'
            elif str(v.get("verdict", "")).strip().startswith("예"):
                row['LLM_Decision'] = 'YES'
                row['LLM_Reason'] = str(v.get("reason", "")).strip()
                verified_conflicts.append(row)
                print(f"  🔥 [진짜 충돌] #{i} {row['Card_A_Claiming']} vs {row['Card_B_Negating']}")
            else:
                row['LLM_Decision'] = 'NO'
                row['LLM_Reason'] = str(v.get("reason", "")).strip()
            judged_rows.append(row)

        time.sleep(3)  # 연속 고속 호출로 인한 일시적 제한 방지

    error_count = sum(1 for r in judged_rows if r.get('LLM_Decision') == 'ERROR')
    print(f"\n이번 구간 심사 완료! {len(candidates)}건 중 진짜 모순 판정 {len(verified_conflicts)}건, 오탐 {len(judged_rows) - len(verified_conflicts) - error_count}건, 에러 {error_count}건.")

    # 기존 전체 로그와 병합 — 구간을 나눠 여러 번 실행해도 판정이 누적된다.
    fieldnames = (list(candidates[0].keys()) + ['LLM_Decision', 'LLM_Reason']) if candidates else ['LLM_Decision', 'LLM_Reason']
    merged = {}
    if os.path.exists(FULL_LOG_PATH):
        with open(FULL_LOG_PATH, 'r', encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                merged[row_key(r)] = r
    for r in judged_rows:
        merged[row_key(r)] = r  # 같은 후보를 재심사하면 최신 판정으로 갱신
    merged_rows = sorted(merged.values(), key=lambda r: float(r.get('Score', 0) or 0), reverse=True)
    merged_yes = [r for r in merged_rows if r.get('LLM_Decision') == 'YES']

    # 0건이어도 항상 파일을 기록한다 — "실행 안 됨"과 "실행했으나 0건"을 구분하기 위함.
    with open(OUTPUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_yes)
    with open(FULL_LOG_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)
    judged_ok_keys = {row_key(r) for r in merged_rows if r.get('LLM_Decision') in ('YES', 'NO')}
    remaining = sum(1 for r in all_candidates if row_key(r) not in judged_ok_keys)
    print(f"누적 현황: 총 심사 {len(merged_rows)}건, 진짜 모순 판정 {len(merged_yes)}건")
    print(f"📋 미심사 잔여: {remaining}건 / 전체 {len(all_candidates)}건 — 다음 단계: python scripts/llm_judge.py next [건수]")
    print(f"최종 결과(YES만, 누적): {OUTPUT_PATH}")
    print(f"전체 심사 로그(YES/NO/ERROR, 누적): {FULL_LOG_PATH}")


if __name__ == '__main__':
    main()
