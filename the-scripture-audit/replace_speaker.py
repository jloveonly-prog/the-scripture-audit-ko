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
                
                original_content = content
                
                # 대소문자를 정확히 구분하여 교체
                # 파일명에 쓰인 'TheScriptureOrg'나 소문자 주소 'thescripture.org'는 건드리지 않음
                content = content.replace("TheScripture.org", "TheScriptureBeliever")
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated internal speaker name in: {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

print("Speaker name replacement complete.")
