import os

directory = r"D:\01.TheScriptureAudit_ko\the-scripture-audit\05_REPORT(전과보고서)\bible_believer"

for filename in os.listdir(directory):
    if filename.endswith(".md"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 모든 TheScriptureMaster를 TheScripture.org로 변경
        content = content.replace("TheScriptureMaster", "TheScripture.org")
        
        # 2. 파일명 및 링크 복구 (파일 제목/링크는 유지해달라고 하셨으므로)
        content = content.replace("REPORT_TheScripture.orgVS", "REPORT_TheScriptureMasterVS")
        content = content.replace("REPORT_순서도비교_IFB_vs_TheScripture.org", "REPORT_순서도비교_IFB_vs_TheScriptureMaster")
        content = content.replace("TheScripture.orgVS연구원", "TheScriptureMasterVS연구원")

        # 3. v2 파일의 인사말 특별 수정 (요청하신 문구로 정확히 대체)
        if "v2" in filename:
            content = content.replace("유튜브 채널 TheScripture.org를 운영하는 성경 신자입니다.", "thescripture.org를 운영하는 형제입니다.")
            content = content.replace("# TheScripture.org (성경 신자)의 첫 질문\n안녕하세요 연구원님.\nthescripture.org를 운영하는 형제입니다.", "# TheScripture.org의 첫 질문\n안녕하세요 연구원님.\nthescripture.org를 운영하는 형제입니다.")
            
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filename}")

print("Replacement complete.")
