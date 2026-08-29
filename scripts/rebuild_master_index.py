#!/usr/bin/env python3
"""Regenerate Master_Index.md from the <!-- doc_no: ... | ver: ... --> header
that sits on the first line of every managed KO/EN document.

doc_no is the ONLY key used to match a KO file to its EN counterpart --
never the filename -- so Korean text never has to be compared or
transliterated to find the pair. This is the reusable, script-driven
replacement for hand-maintaining Master_Index.md (which used to go stale).

Usage:
    python scripts/rebuild_master_index.py

Run this any time doc_no headers are added/changed and you want
Master_Index.md to reflect the current state of both repos.
"""
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KO_ROOT = os.path.dirname(SCRIPT_DIR)              # D:\01.TheScriptureAudit_ko
EN_ROOT = KO_ROOT.replace('_ko', '')                # D:\01.TheScriptureAudit

PROJECTS = ['the-scripture-audit', 'the-catholic-audit', 'the-sermon-audit']
SKIP_DIR_NAMES = {'.git', 'backup', '검토필요', '_Legacy_Engines_back'}

HEADER_RE = re.compile(r'^<!--\s*doc_no:\s*(\S+)\s*\|\s*ver:\s*(\S+)\s*-->')


def in_scope(dirpath: str) -> bool:
    parts = dirpath.split(os.sep)
    for p in parts:
        if p in SKIP_DIR_NAMES or p.endswith('_back') or p.startswith('_INBOX'):
            return False
    return True


def scan(root: str):
    """Return {doc_no: {'path': ..., 'name': ..., 'ver': ..., 'lines': ...}}"""
    found = {}
    for proj in PROJECTS:
        proj_root = os.path.join(root, proj)
        if not os.path.isdir(proj_root):
            continue
        for dirpath, dirnames, filenames in os.walk(proj_root):
            if not in_scope(dirpath):
                dirnames[:] = []
                continue
            for fn in filenames:
                if not fn.endswith('.md'):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, encoding='utf-8-sig') as f:
                        content = f.read()
                except Exception:
                    continue
                m = HEADER_RE.match(content)
                if not m:
                    continue
                doc_no, ver = m.group(1), m.group(2)
                lines = len(content.splitlines())
                found[(proj, doc_no)] = {
                    'path': path, 'name': fn, 'ver': ver, 'lines': lines,
                }
    return found


def main():
    ko_docs = scan(KO_ROOT)
    en_docs = scan(EN_ROOT)

    all_keys = sorted(set(ko_docs.keys()) | set(en_docs.keys()), key=lambda k: (k[0], k[1]))

    by_project = {}
    orphans = []  # doc_no present on only one side
    for key in all_keys:
        proj, doc_no = key
        ko = ko_docs.get(key)
        en = en_docs.get(key)
        if not ko or not en:
            orphans.append((proj, doc_no, 'KO only' if ko else 'EN only'))
            continue
        by_project.setdefault(proj, []).append({
            'doc_no': doc_no,
            'file_en': en['name'],
            'file_ko': ko['name'],
            'lines_en': en['lines'],
            'ver': max(ko['ver'], en['ver']),
        })

    lines = []
    lines.append("# Master Index")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    total = sum(len(v) for v in by_project.values())
    lines.append(f"**Total Managed Documents**: {total}")
    lines.append(f"**KO Repository**: {KO_ROOT}\\")
    lines.append(f"**EN Repository**: {EN_ROOT}\\")
    lines.append("")
    lines.append("> Each document carries a single-line header "
                  "`<!-- doc_no: YYYYMMDD_NNNN | ver: YYYYMMDD_HHmm -->` at the very top "
                  "(KO and EN share the same `doc_no`; each side's `ver` is independent). "
                  "`doc_no` is the sole matching key between KO and EN -- never the filename.")
    lines.append("> This file is generated. To refresh it: `python scripts/rebuild_master_index.py`.")
    lines.append("")

    for proj in PROJECTS:
        rows = by_project.get(proj, [])
        if not rows:
            continue
        rows.sort(key=lambda r: r['doc_no'])
        lines.append(f"## {proj} ({len(rows)})")
        lines.append("")
        lines.append("| doc_no | file_nm | file_nm_ko | 번역유무 | 줄수 | 마지막update |")
        lines.append("|---|---|---|:---:|---:|---|")
        for r in rows:
            lines.append(f"| {r['doc_no']} | {r['file_en']} | {r['file_ko']} | Y | "
                          f"{r['lines_en']} | {r['ver']} |")
        lines.append("")

    if orphans:
        lines.append(f"## ⚠️ Orphaned doc_no (present on only one side) — {len(orphans)}")
        lines.append("")
        lines.append("> These have a doc_no header on one side but no matching pair on the other. "
                      "Check whether the EN translation is missing, or the doc_no was mistyped.")
        lines.append("")
        for proj, doc_no, which in orphans:
            lines.append(f"- `{doc_no}` ({proj}) — {which}")
        lines.append("")

    out_path = os.path.join(KO_ROOT, 'Master_Index.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"Wrote {out_path}")
    print(f"  Matched pairs: {total}")
    print(f"  Orphans: {len(orphans)}")


if __name__ == '__main__':
    main()
