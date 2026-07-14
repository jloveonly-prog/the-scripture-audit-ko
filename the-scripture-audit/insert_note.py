import os

root_dir = r"D:\01.TheScriptureAudit_ko\the-scripture-audit\05_REPORT(전과보고서)\bible_believer"

files_to_update = {
    "REPORT_TheScriptureOrg_VS_연구원.md": "> [!WARNING]",
    "REPORT_TheScriptureOrg_VS_연구원v2.md": "# TheScriptureBeliever",
    "REPORT_TheScriptureOrg_VS_연구원v3.md": "---",
    "REPORT_순서도비교_IFB_vs_TheScriptureOrg.md": "---"
}

note_text = """> [!NOTE]
> **※ 일러두기 (TheScriptureBeliever의 의미)**
> 본 문서에서 화자로 등장하는 **'TheScriptureBeliever'**는 기존 교계에서 쓰이는 'Bible Believer(성경 신자)'와는 다른 뚜렷한 정체성을 가집니다.
> 전통적으로 사용하는 'Bible'이라는 단어는 KJV 성경 66권 원문을 통틀어 단 한 번도 등장하지 않는 인간이 만든 호칭입니다. 반면, 예수님과 바울이 하나님의 절대적인 말씀을 지칭할 때 성령님께서 직접 사용하신 단어는 오직 **"The Scripture"**(요 5:39, 딤후 3:16)입니다. 
> 본 화자는 성경 원문에 없는 단어를 내세우는 전통 교리(Bible Believer)와 스스로를 구별하며, 오직 기록된 진리의 원어(The Scripture) 그 자체만을 믿고 변증하는 자임을 밝힙니다.

"""

for filename, target_string in files_to_update.items():
    filepath = os.path.join(root_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 중복 방지
        if "TheScriptureBeliever의 의미" not in content:
            if target_string in content:
                content = content.replace(target_string, note_text + target_string, 1)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Added disclaimer to {filename}")
            else:
                print(f"Could not find target string in {filename}")
    else:
        print(f"File not found: {filename}")

print("Insertion complete.")
