import os
import csv
import time
from google import genai
from google.genai import types

# 파일 경로 설정
CSV_PATH = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\auto_conflict_results.csv"
OUTPUT_PATH = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\llm_verified_conflicts.csv"
FULL_LOG_PATH = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\llm_judge_full_log.csv"
TOP_N = 100 # 상위 100개만 우선 검사 (전체 후보는 수천 건 — 필요 시 상향)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("에러: GEMINI_API_KEY 환경 변수가 설정되어 있지 않습니다.")
        print("터미널에서 'set GEMINI_API_KEY=당신의_API_키' 를 입력하신 후 다시 실행해주세요.")
        return

    client = genai.Client(api_key=api_key)
    
    if not os.path.exists(CSV_PATH):
        print(f"파일이 존재하지 않습니다: {CSV_PATH}")
        return

    candidates = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(row)

    # 유사도(Score) 순으로 이미 정렬되어 있다고 가정하고 상위 N개 추출
    candidates = candidates[:TOP_N]
    
    print(f"총 {len(candidates)}개의 후보에 대해 LLM 정밀 심사(LLM-as-a-Judge)를 시작합니다...")

    verified_conflicts = []
    judged_rows = []  # YES/NO/ERROR 전체 기록 (감사 추적용)

    for idx, row in enumerate(candidates):
        claim = row['Claim_Text']
        negate = row['Negate_Text']
        card_a = row['Card_A_Claiming']
        card_b = row['Card_B_Negating']
        
        prompt = f"""당신은 가톨릭 신학 및 교리 논리 분석 전문가입니다.
아래 두 명제를 읽고, 가톨릭 신학의 맥락에서 두 문서가 논리적으로 정면 충돌(모순)하는지 엄격하게 판단하세요.

문서 A({card_a})의 공식 주장: "{claim}"
문서 B({card_b})가 '단죄(부정)'하는 이단적 명제: "{negate}"

[판단 기준]
- 문서 A가 '옳다'고 가르치는 내용이, 문서 B가 '틀렸다'고 단죄하는 명제와 사실상 완전히 동일합니까?
- 만약 두 문장이 단순히 같은 주제(예: 은총, 세례)를 다룰 뿐, 주장하는 바가 다르다면 '아니오'입니다.
- 역사적으로 이미 해결되었거나, 예외 조항(적용 대상의 차이)으로 양립 가능한 경우도 '아니오'로 판단하되 그 이유를 쓰세요.

[답변 형식]
첫 줄에는 반드시 '예' 또는 '아니오' 중 하나만 작성하세요.
두 번째 줄에는 1~3문장으로 그 이유를 간결하게 설명하세요.
"""
        
        try:
            print(f"[{idx+1}/{TOP_N}] 분석 중: {card_a} vs {card_b}")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0, # 논리적 일관성을 위해 0으로 설정
                )
            )
            
            result_text = response.text.strip().split('\n')
            decision = result_text[0].strip().replace('*', '') # 마크다운 별표 제거
            reason = ' '.join(result_text[1:]).strip()
            
            if '예' in decision and '아니오' not in decision:
                print(f"  🔥 [진짜 충돌 발견!] {card_a} vs {card_b}")
                print(f"  이유: {reason}\n")
                row['LLM_Decision'] = 'YES'
                row['LLM_Reason'] = reason
                verified_conflicts.append(row)
            else:
                print(f"  ❌ [오탐 패스] {reason}\n")
                row['LLM_Decision'] = 'NO'
                row['LLM_Reason'] = reason
            judged_rows.append(row)

            # API Rate Limit 방지용 대기
            time.sleep(2)

        except Exception as e:
            # 에러 건을 조용히 버리지 않고 ERROR로 기록해 재심사 대상을 추적 가능하게 남긴다
            print(f"API 호출 중 에러 발생: {e}")
            row['LLM_Decision'] = 'ERROR'
            row['LLM_Reason'] = str(e)
            judged_rows.append(row)
            time.sleep(5)

    error_count = sum(1 for r in judged_rows if r.get('LLM_Decision') == 'ERROR')
    print(f"\n심사 완료! {len(candidates)}건 중 진짜 모순 판정 {len(verified_conflicts)}건, 에러 {error_count}건.")

    # 0건이어도 항상 파일을 기록한다 — "실행 안 됨"과 "실행했으나 0건"을 구분하기 위함.
    fieldnames = list(candidates[0].keys()) + ['LLM_Decision', 'LLM_Reason'] if candidates else ['LLM_Decision', 'LLM_Reason']
    with open(OUTPUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(verified_conflicts)
    with open(FULL_LOG_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(judged_rows)
    print(f"최종 결과(YES만): {OUTPUT_PATH}")
    print(f"전체 심사 로그(YES/NO/ERROR): {FULL_LOG_PATH}")

if __name__ == '__main__':
    main()
