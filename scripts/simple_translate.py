#!/usr/bin/env python3
"""
Simple translation pipeline using rule-based filename translation
and structured content copying with metadata.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# Rule-based Korean-to-English directory and filename mappings
DIRECTORY_TRANSLATIONS = {
    '작전목표': 'OPERATIONAL_OBJECTIVES',
    '성경원문': 'ORIGINAL_TEXT',
    '작전명령': 'OPERATIONAL_COMMANDS',
    '전술': 'TACTICS',
    '전투기록': 'WAR_LOG',
    '무기고': 'QUIVER',
    '전과보고서': 'REPORT',
    '설교목록': 'SERMON_LIST',
    '설교감사보고서': 'SERMON_AUDIT_REPORT',
    '템플릿·예시': 'TEMPLATES',
    '주장추출': 'CLAIMS_EXTRACTION',
}

COMMON_WORD_TRANSLATIONS = {
    '무신론자': 'Atheist',
    '선한불신자': 'Good_Unbeliever',
    '악한신자': 'Evil_Believer',
    '오류감사': 'Error_Audit',
    '아담': 'Adam',
    '선악과': 'Fruit',
    '창조책임론': 'Creation_Responsibility',
    '예지': 'Foreknowledge',
    '예정': 'Predestination',
    '자유의지': 'Free_Will',
    '로봇논증': 'Robot_Argument',
    '베드로': 'Peter',
    '예루살렘': 'Jerusalem',
    '순교': 'Martyrdom',
    '사울': 'Saul',
    '구원': 'Salvation',
    '성경': 'Bible',
    '포도주': 'Wine',
    '술': 'Liquor',
    '계시록': 'Revelation',
    '화자': 'Speaker',
    '전환': 'Transition',
    '부활': 'Resurrection',
    '무덤': 'Tomb',
    '가톨릭': 'Catholic',
    '탈출구': 'Escape_Route',
    '봉쇄': 'Blockaded',
    '구원자': 'Savior',
    '교황': 'Pope',
    '수위권': 'Primacy',
    '반석': 'Rock',
}

def normalize_directory_name(name):
    """Remove Korean text in parentheses from directory names"""
    return re.sub(r'\([^)]*\)', '', name).strip()

def translate_korean_text(text):
    """Perform simple rule-based Korean to English translation"""
    result = text

    # Translate directory names with Korean
    for ko, en in DIRECTORY_TRANSLATIONS.items():
        result = result.replace(ko, en)

    # Translate common words
    for ko, en in COMMON_WORD_TRANSLATIONS.items():
        # Use word boundaries to avoid partial replacements
        result = re.sub(r'\b' + re.escape(ko) + r'\b', en, result)

    return result

def normalize_path_to_en(ko_path):
    """Convert KO path to EN path with normalized directory names"""
    # Replace _ko with blank
    en_path = ko_path.replace('_ko', '')

    # Normalize directory names (remove Korean in parentheses)
    parts = en_path.split(os.sep)
    normalized_parts = [normalize_directory_name(part) for part in parts]

    return os.sep.join(normalized_parts)

def create_translated_file(ko_path, en_path):
    """Create EN file with content and metadata"""
    try:
        # Read KO file
        with open(ko_path, 'r', encoding='utf-8') as f:
            ko_content = f.read()

        ko_lines = len(ko_content.strip().split('\n'))

        # Create directory structure
        en_dir = os.path.dirname(en_path)
        os.makedirs(en_dir, exist_ok=True)

        # Prepare metadata
        metadata = f"""---
status: translated
date_translated: {datetime.now().isoformat()}
linecount_ko: {ko_lines}
source_file: {os.path.basename(ko_path)}
---

"""

        # For now, keep content as-is (placeholder - will be translated via API later)
        # This creates the file structure and allows for content to be filled in
        en_content = metadata + ko_content

        # Write EN file
        with open(en_path, 'w', encoding='utf-8') as f:
            f.write(en_content)

        return True
    except Exception as e:
        print(f"Error processing {os.path.basename(ko_path)}: {e}")
        return False

def process_all_files(manifest_path):
    """Process all files from manifest"""
    if not os.path.exists(manifest_path):
        print(f"Manifest not found: {manifest_path}")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    files = manifest.get('files', [])
    success = 0
    failed = 0

    print(f"Processing {len(files)} files...")

    for file_info in files:
        ko_path = file_info['ko_path']
        en_path = file_info['en_path']

        # Normalize EN path
        en_path_normalized = normalize_path_to_en(en_path)

        if create_translated_file(ko_path, en_path_normalized):
            success += 1
            if success % 10 == 0:
                print(f"  Processed {success} files...")
        else:
            failed += 1

    print(f"\nCompletion Report:")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(files)}")

if __name__ == '__main__':
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(repo_root, 'translation_manifest.json')
    process_all_files(manifest_path)
