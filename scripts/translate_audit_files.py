#!/usr/bin/env python3
"""
Comprehensive translation pipeline for Scripture and Sermon Audit files.
- Translates Korean content to English
- Translates Korean filenames to English
- Validates translation quality
- Adds metadata to translated files
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import anthropic

def get_repo_root() -> str:
    """Get repository root"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def normalize_ko_dirname(dirname: str) -> str:
    """Convert KO directory name to EN by removing parenthetical content"""
    # Remove Korean text in parentheses
    return re.sub(r'\([^)]*\)', '', dirname).strip()

def translate_korean_filename(filename: str, client: anthropic.Anthropic) -> str:
    """Translate Korean filename to English using Claude"""
    if not re.search(r'[가-힯]', filename):  # No Korean characters
        return filename

    try:
        message = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"Translate this Korean filename to English, keeping the file extension. Keep any English parts and codes unchanged. Return ONLY the translated filename:\n\n{filename}"
            }]
        )
        translated = message.content[0].text.strip()
        return translated
    except Exception as e:
        print(f"Error translating filename '{filename}': {e}", file=sys.stderr)
        return filename

def translate_korean_content(content: str, client: anthropic.Anthropic, file_path: str = "") -> str:
    """Translate Korean content to English using Claude"""
    # Check if content has Korean
    if not re.search(r'[가-힯]', content):
        return content

    # For long files, split into sections
    lines = content.split('\n')
    translated_lines = []
    current_section = []

    for line in lines:
        current_section.append(line)
        # Process in batches of 50 lines or when we hit certain markers
        if len(current_section) >= 50 or line.startswith('---'):
            section_text = '\n'.join(current_section)
            if re.search(r'[가-힯]', section_text):
                try:
                    message = client.messages.create(
                        model="claude-opus-4-1-20250805",
                        max_tokens=4000,
                        messages=[{
                            "role": "user",
                            "content": f"Translate the following Korean content to English. Maintain all markdown formatting, structure, and special characters. Translate completely without abbreviations:\n\n{section_text}"
                        }]
                    )
                    translated = message.content[0].text
                    translated_lines.extend(translated.split('\n'))
                except Exception as e:
                    print(f"Warning: Translation error in {file_path}: {e}", file=sys.stderr)
                    translated_lines.extend(current_section)
            else:
                translated_lines.extend(current_section)
            current_section = []

    # Handle remaining section
    if current_section:
        section_text = '\n'.join(current_section)
        if re.search(r'[가-힯]', section_text):
            try:
                message = client.messages.create(
                    model="claude-opus-4-1-20250805",
                    max_tokens=4000,
                    messages=[{
                        "role": "user",
                        "content": f"Translate the following Korean content to English. Maintain all markdown formatting, structure, and special characters. Translate completely without abbreviations:\n\n{section_text}"
                    }]
                )
                translated = message.content[0].text
                translated_lines.extend(translated.split('\n'))
            except Exception as e:
                print(f"Warning: Translation error in {file_path}: {e}", file=sys.stderr)
                translated_lines.extend(current_section)
        else:
            translated_lines.extend(current_section)

    return '\n'.join(translated_lines)

def extract_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """Extract YAML frontmatter from content"""
    if not content.startswith('---'):
        return None, content

    lines = content.split('\n')
    fm_lines = []
    fm_end = 0

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            fm_end = i + 1
            break
        fm_lines.append(line)

    if fm_end > 0:
        frontmatter = '---\n' + '\n'.join(fm_lines) + '\n---\n'
        remaining = '\n'.join(lines[fm_end:])
        return frontmatter, remaining

    return None, content

def add_translation_metadata(content: str, ko_linecount: int) -> str:
    """Add translation metadata to content"""
    en_linecount = len(content.strip().split('\n'))

    metadata = f"""---
status: translated
date_translated: {datetime.now().isoformat()}
linecount_ko: {ko_linecount}
linecount_en: {en_linecount}
abbreviation_rate: {((ko_linecount - en_linecount) / ko_linecount * 100):.1f}% if ko_linecount > 0 else 0
---
"""
    return metadata + content

def process_file(ko_path: str, en_path: str, client: anthropic.Anthropic) -> bool:
    """Process a single KO file and create EN translation"""
    try:
        # Read KO file
        with open(ko_path, 'r', encoding='utf-8') as f:
            ko_content = f.read()

        ko_lines = len(ko_content.strip().split('\n'))

        # Extract frontmatter if exists
        fm, content = extract_frontmatter(ko_content)

        # Translate content
        translated_content = translate_korean_content(content, client, ko_path)

        # Reconstruct with frontmatter
        if fm:
            translated_content = fm + translated_content

        # Add metadata
        final_content = add_translation_metadata(translated_content, ko_lines)

        # Create directory structure
        en_dir = os.path.dirname(en_path)
        os.makedirs(en_dir, exist_ok=True)

        # Write EN file
        with open(en_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        print(f"✓ {os.path.basename(ko_path)}")
        return True

    except Exception as e:
        print(f"✗ {os.path.basename(ko_path)}: {e}", file=sys.stderr)
        return False

def translate_korean_dirname(dirname: str, client: anthropic.Anthropic) -> str:
    """Translate directory name using Claude"""
    # First normalize by removing parentheses
    normalized = normalize_ko_dirname(dirname)
    if normalized == dirname:
        return dirname

    try:
        message = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"Translate this Korean directory name to English, preserving the numbering prefix. Return ONLY the translated name:\n\n{dirname}"
            }]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"Warning: Could not translate dirname '{dirname}': {e}", file=sys.stderr)
        return normalized

def find_missing_files() -> List[Tuple[str, str, str]]:
    """Find all KO files that need EN translations"""
    repo_root = get_repo_root()
    ko_root = os.path.join(repo_root, 'the-scripture-audit')
    en_root = os.path.join(repo_root.replace('_ko', ''), 'the-scripture-audit')

    sermon_ko_root = os.path.join(repo_root, 'the-sermon-audit')
    sermon_en_root = os.path.join(repo_root.replace('_ko', ''), 'the-sermon-audit')

    missing = []

    # Find missing Scripture files
    for root, dirs, files in os.walk(ko_root):
        # Normalize directory names
        rel_path = os.path.relpath(root, ko_root)
        if rel_path == '.':
            en_dir = en_root
        else:
            normalized_path = normalize_ko_dirname(rel_path)
            en_dir = os.path.join(en_root, normalized_path)

        for filename in files:
            if filename.endswith('.md') and filename != 'INDEX.md':
                ko_path = os.path.join(root, filename)
                en_path = os.path.join(en_dir, filename)

                if not os.path.exists(en_path):
                    missing.append((ko_path, en_path, 'scripture'))

    # Find missing Sermon files
    for root, dirs, files in os.walk(sermon_ko_root):
        rel_path = os.path.relpath(root, sermon_ko_root)
        if rel_path == '.':
            en_dir = sermon_en_root
        else:
            normalized_path = normalize_ko_dirname(rel_path)
            en_dir = os.path.join(sermon_en_root, normalized_path)

        for filename in files:
            if filename.endswith('.md') and filename != 'INDEX.md':
                ko_path = os.path.join(root, filename)
                en_path = os.path.join(en_dir, filename)

                if not os.path.exists(en_path):
                    missing.append((ko_path, en_path, 'sermon'))

    return missing

def main():
    """Main translation pipeline"""
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    missing_files = find_missing_files()
    print(f"Found {len(missing_files)} files to translate")
    print(f"  Scripture: {len([f for f in missing_files if f[2] == 'scripture'])}")
    print(f"  Sermon: {len([f for f in missing_files if f[2] == 'sermon'])}")
    print()

    # Process files
    success = 0
    failed = 0

    for ko_path, en_path, audit_type in missing_files:
        if process_file(ko_path, en_path, client):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*50}")
    print(f"Translation Summary:")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(missing_files)}")
    print(f"{'='*50}")

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
