#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
표준킹제임스성경(KSKJB) 한영 대역 수집기  —  v2 (2026-08-18)

출처 : https://kingjamesbiblekorea.com
본문 : 표준킹제임스성경 (KSKJB) / Copyright (C) Biblebelievers Publication
라이선스: CC BY-NC-ND 4.0  →  비영리·출처표시·변경금지
          ※ 본 스크립트 산출물은 검색 편의를 위해 마크업을 부가하므로
            "변경(adapted)"에 해당한다. 따라서 **재배포 금지 / 로컬 전용**.

────────────────────────────────────────────────────────────────
v1 → v2 변경 사유 (중요)
────────────────────────────────────────────────────────────────
v1은 한글 강조 표시를 소괄호 ( ) 로 감쌌다. 그런데 KJV 본문 자체가
소괄호를 쓰는 절이 223개 있어(예: 창 10:14 "(out of whom came Philistim,)")
**표시 괄호와 본문 괄호가 구분 불가능**해졌다. 창 49:24처럼 본문 괄호 안에
표시 괄호가 중첩되는 사례까지 발생하여 사후 복원이 불가능하다.

또한 v1은 `font-g font-light` 표시를 통째로 버렸다(창 1장만 36건).
영문 대문자 정보(예: Day, Night)가 소실되었다.

v2는 두 가지를 모두 해결한다:
  · font-g font-semibold  →  < >   (굵은 표시)
  · font-g font-light     →  ‹ ›   (연한 표시)
  · 본문 소괄호 ( )        →  원문 그대로 보존
  · 영문 이탤릭            →  [ ]
  · 단락표 ¶               →  원문 그대로 보존
"""

import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://kingjamesbiblekorea.com"
OUTPUT_JSON = "KJV_KO_표준.json"
SLEEP_SEC = 0.5           # 서버 부하 배려
TIMEOUT = 30
RETRY = 3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

# ─────────────────────────────────────────────────────────────
# 마크업 기호
#   본문 전수조사 결과 아래 기호는 성경 본문에 0건이므로 안전하다.
#   반대로 ( ) 3,726건 · [ ] 21,483건은 본문에 존재하므로
#   ( ) 를 마크업으로 쓰면 본문 괄호와 충돌한다(v1의 실패 원인).
# ─────────────────────────────────────────────────────────────
MARK = {
    # 한글 — 사이트 클래스 5종을 모두 보존
    "ko_black":    ("《", "》"),   # font-g font-black     : 주(LORD) 최상위
    "ko_semibold": ("<", ">"),     # font-g font-semibold  : 굵은 신명·칭호
    "ko_light":    ("‹", "›"),     # font-g font-light     : 연한 신명
    "ko_bold":     ("{", "}"),     # font-bold             : 일반 강조
    "ko_italic":   ("[", "]"),     # italic                : 번역자 보충어
    # 영문
    "en_italic":   ("[", "]"),     # italic                : 번역자 보충어
}

# 한글 span 클래스 → 마크업 키
KO_CLASS_MAP = [
    ("font-g font-black",    "ko_black"),
    ("font-g font-semibold", "ko_semibold"),
    ("font-g font-light",    "ko_light"),
    ("font-bold",            "ko_bold"),
    ("italic",               "ko_italic"),
]

# 인식하지 못한 클래스 수집 —  조용한 데이터 손실 방지
UNKNOWN = {}


def get(url):
    """재시도 포함 GET."""
    last = None
    for i in range(RETRY):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.text
            if r.status_code == 404:
                return None
            last = f"HTTP {r.status_code}"
        except Exception as e:                      # noqa: BLE001
            last = repr(e)
        time.sleep(1.5 * (i + 1))
    print(f"    [실패] {url} — {last}", file=sys.stderr)
    return None


def fetch_books():
    """66권 목록 (영문 키, 한글명)."""
    html = get(f"{BASE_URL}/p/Genesis/1")
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    menu = soup.find("div", id="books-menu")
    if not menu:
        return []
    books, seen = [], set()
    for a in menu.find_all("a"):
        href = a.get("href") or ""
        m = re.match(r"^/p/([^/]+)/1$", href)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            books.append({"en": m.group(1), "ko": a.get_text(strip=True)})
    return books


def render(p_tag, lang):
    """<p> 하나를 마크업 문자열로 변환.

    절 번호 span은 버리고, 강조 span만 기호로 감싼다.
    그 외 텍스트(본문 괄호·¶ 포함)는 **원문 그대로** 이어붙인다.
    """
    out = []
    for node in p_tag.children:
        name = getattr(node, "name", None)

        if name == "span":
            cls = node.get("class") or []
            cls_s = " ".join(cls)
            text = node.get_text()

            # 절 번호 제거
            if "mr-2" in cls or ("hidden" in cls and "lg:inline" in cls):
                continue
            if not text:
                continue

            if lang == "ko":
                key = None
                for pat, k in KO_CLASS_MAP:
                    if all(tok in cls for tok in pat.split()):
                        key = k
                        break
                if key:
                    o, c = MARK[key]
                    out.append(f"{o}{text}{c}")
                else:
                    # 미지의 클래스 — 텍스트는 살리되 반드시 기록한다
                    UNKNOWN[cls_s] = UNKNOWN.get(cls_s, 0) + 1
                    out.append(text)

            elif lang == "en":
                if "italic" in cls:
                    o, c = MARK["en_italic"]
                    out.append(f"{o}{text}{c}")
                else:
                    if cls_s:
                        UNKNOWN["EN:" + cls_s] = UNKNOWN.get("EN:" + cls_s, 0) + 1
                    out.append(text)
            else:
                out.append(text)

        elif name is None:
            out.append(str(node))
        else:
            out.append(node.get_text())

    return re.sub(r"\s+", " ", "".join(out)).strip()


def fetch_chapter(book_en, chapter):
    """한 장을 수집한다.

    반환: (verses, meta)

    ── 비본문 요소 자동 분리 ──────────────────────────────────
    이 사이트는 아래 3종을 본문 절과 같은 <div class="verse"> 로 담지만,
    **절 번호 span(mr-2)이 없다**는 점에서 확실히 구분된다.

      · 시편 표제        예) <다윗의 시편> / <A Psalm of David.>   → meta.title
      · 시119편 소제목   예) א 알레프 / ALEPH.                     → meta.sections
      · 바울서신 후기    예) ¶ The first epistle to the Corinthians… → meta.subscription

    v1은 이것들을 절로 세어 31,254절이 되었고 시편 116편의 절 번호가
    1씩 밀렸다. 여기서 분리하면 처음부터 표준 절 번호(31,102)와 일치한다.
    """
    html = get(f"{BASE_URL}/p/{book_en}/{chapter}")
    if not html:
        return None, None
    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all("div", class_="verse")
    if not divs:
        return None, None

    # 총 본문 절 수를 먼저 센다 — 후기 판정에 필요
    total_verses = sum(
        1 for dv in divs
        if len(dv.find_all("p")) >= 2
        and dv.find_all("p")[0].find("span", class_="mr-2") is not None
    )

    verses, meta = {}, {}
    n = 0

    for div in divs:
        ps = div.find_all("p")
        if len(ps) < 2:
            continue

        has_num = ps[0].find("span", class_="mr-2") is not None
        ko = render(ps[0], "ko")
        en = render(ps[1], "en")

        if has_num:                      # ── 본문 절
            n += 1
            verses[str(n)] = {"en": en, "ko": ko}
            continue

        # ── 비본문 요소 분류
        stripped = en.strip()

        # ① 표제 — 원문이 리터럴 < > 로 감싼다  예) <A Psalm of David.>
        if stripped.startswith("<") and stripped.endswith(">"):
            meta["title"] = {"en": en, "ko": ko}

        # ② 후기 — 마지막 절 뒤에 오고, 서신 후기 문구를 담는다
        #    ※ 위치 인덱스가 아니라 "모든 절을 지난 뒤인가"로 판정한다.
        #      로마서 16장은 후기 뒤에 빈 div가 하나 더 있어
        #      idx == last 규칙으로는 잡히지 않았다(2026-08-18 수정).
        elif n >= total_verses and re.search(
            r"\bwritten\b|기록되었|기록되어|보내는 .*서신", en + ko
        ):
            meta["subscription"] = {"en": en, "ko": ko}

        # ③ 그 외 — 단락 소제목 (시 119편 히브리 알파벳 등)
        else:
            meta.setdefault("sections", []).append(
                {"after_verse": n, "en": en, "ko": ko}
            )

    return (verses or None), meta


def main():
    print("책 목록 수집 중...")
    books = fetch_books()
    if len(books) != 66:
        print(f"경고: 책 수가 66이 아닙니다 ({len(books)})", file=sys.stderr)
    if not books:
        sys.exit("책 목록 수집 실패")

    data = {
        "_license": {
            "korean_text": "표준킹제임스성경 (KSKJB) — Korean Standard King James Bible",
            "copyright": "Copyright (C) Biblebelievers Publication",
            "license": "CC BY-NC-ND 4.0 (Attribution-NonCommercial-NoDerivatives)",
            "source": BASE_URL,
            "contact": "standardkjb@gmail.com / BibleBelievers.co.kr",
            "notice": (
                "비영리 연구 목적 로컬 사용. 본 파일은 검색 편의를 위해 마크업이 "
                "부가되었으므로 배포 시 ND(변경금지) 조항 위반. 재배포 금지."
            ),
            "markup": {
                "《...》": "한글 — font-g font-black : 주(LORD) 최상위 강조",
                "<...>": "한글 — font-g font-semibold : 굵은 신명·칭호",
                "‹...›": "한글 — font-g font-light : 연한 신명",
                "{...}": "한글 — font-bold : 일반 강조",
                "[...]": "한글·영문 — italic : 원어에 없는 번역자 보충어",
                "¶": "단락 표시 (원문 그대로)",
                "(...)": "본문 자체의 괄호 — 마크업이 아님. 절대 변환 금지",
            },
            "fetched": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    }

    total_ch = total_v = 0
    n_title = n_sec = n_sub = 0
    for n, b in enumerate(books, 1):
        en, ko = b["en"], b["ko"]
        data[en] = {"name_ko": ko, "chapters": {}}
        ch = 1
        while True:
            verses, meta = fetch_chapter(en, ch)
            if not verses:
                break
            data[en]["chapters"][str(ch)] = verses
            if meta:
                data[en].setdefault("chapter_meta", {})[str(ch)] = meta
                n_title += "title" in meta
                n_sub += "subscription" in meta
                n_sec += len(meta.get("sections", []))
            total_ch += 1
            total_v += len(verses)
            ch += 1
            time.sleep(SLEEP_SEC)
        print(f"[{n:2d}/66] {ko} ({en}) — {ch-1}장 / 누적 {total_v}절")

    data["_license"]["counts"] = {
        "books": len(books), "chapters": total_ch, "verses": total_v,
        "titles": n_title, "sections": n_sec, "subscriptions": n_sub,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {OUTPUT_JSON}")
    print(f"  책 {len(books)} / 장 {total_ch} / 절 {total_v}")

    if UNKNOWN:
        print("\n[경고] 인식하지 못한 span 클래스 — 마크업 없이 텍스트만 보존됨:")
        for k, v in sorted(UNKNOWN.items(), key=lambda x: -x[1]):
            print(f"    {k or '(클래스 없음)':<34} {v}건")
        print("  → MARK / KO_CLASS_MAP 에 규칙을 추가한 뒤 재수집을 검토할 것")
    else:
        print("\n[확인] 인식하지 못한 클래스 없음 — 데이터 손실 0")


if __name__ == "__main__":
    main()
