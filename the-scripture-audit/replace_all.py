import os

root_dir = r"D:\01.TheScriptureAudit_ko\the-scripture-audit"

for dirpath, dirnames, filenames in os.walk(root_dir):
    if ".git" in dirpath:
        continue
    for filename in filenames:
        if filename.endswith(".md"):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue
            
            original_content = content
            
            # 1. 모든 TheScriptureMaster를 TheScripture.org로 변경
            content = content.replace("TheScriptureMaster", "TheScripture.org")
            
            # 2. 파일명 및 링크 복구 (파일 제목/링크는 유지)
            content = content.replace("REPORT_TheScripture.orgVS", "REPORT_TheScriptureMasterVS")
            content = content.replace("REPORT_순서도비교_IFB_vs_TheScripture.org", "REPORT_순서도비교_IFB_vs_TheScriptureMaster")
            content = content.replace("TheScripture.orgVS연구원", "TheScriptureMasterVS연구원")
            
            if content != original_content:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated: {filepath}")
                except Exception as e:
                    print(f"Error writing {filepath}: {e}")

print("Global replacement complete.")
