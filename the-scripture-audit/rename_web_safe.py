import os
import shutil

root_dir = r"D:\01.TheScriptureAudit_ko\the-scripture-audit"
bible_believer_dir = os.path.join(root_dir, "05_REPORT(전과보고서)", "bible_believer")

rename_map = {
    "REPORT_TheScripture.org_VS_연구원.md": "REPORT_TheScriptureOrg_VS_연구원.md",
    "REPORT_TheScripture.org_VS_연구원v2.md": "REPORT_TheScriptureOrg_VS_연구원v2.md",
    "REPORT_TheScripture.org_VS_연구원v3.md": "REPORT_TheScriptureOrg_VS_연구원v3.md",
    "REPORT_순서도비교_IFB_vs_TheScripture.org.md": "REPORT_순서도비교_IFB_vs_TheScriptureOrg.md"
}

# 1. Update internal links inside ALL md files
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
                
                # Replace the filenames inside the text
                for old_name, new_name in rename_map.items():
                    content = content.replace(old_name, new_name)
                    
                    # Also replace without .md for pure text references
                    old_base = old_name.replace(".md", "")
                    new_base = new_name.replace(".md", "")
                    content = content.replace(old_base, new_base)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated links in: {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

# 2. Rename the actual files
for old_name, new_name in rename_map.items():
    old_path = os.path.join(bible_believer_dir, old_name)
    new_path = os.path.join(bible_believer_dir, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Renamed file: {old_name} -> {new_name}")
    else:
        print(f"File not found for renaming (already renamed?): {old_name}")

print("File renaming and link update complete.")
