---
name: sync-translate
description: origin/main에 push된 KO 문서 중 아직 EN으로 번역 안 됐거나 KO가 더 최신인 문서를 찾아 Claude가 직접 번역해서 01.TheScriptureAudit(EN)에 반영하고 Master_Index.md를 갱신한다.
---

# KO → EN 번역 동기화 스킬

## 언제 쓰는가

사용자가 "번역 동기화해줘", "새 문서 번역해", `/sync-translate` 등을 요청할 때. **origin/main에 push된 내용만** 번역 대상으로 삼는다 — 로컬에만 있는 커밋되지 않았거나 push 안 된 작업은 절대 건드리지 않는다. 이건 의도된 안전장치다 (2026-08-29 설계 확정: "git에 add push 한 것만 번역해서 복사").

## 절대 하지 말 것

- `scripts/simple_translate.py`, `scripts/translate_audit_files.py` 같은 자동 번역 스크립트를 만들거나 되살리지 않는다. 이런 방식(줄 단위 기계적 청킹, 원문 복붙 후 "번역완료"로 위장)이 이 프로젝트에서 스텁 파일·잘라먹기·날조 버그의 반복적 원인이었다. **번역은 이 스킬을 실행하는 Claude가 원문을 직접 읽고 판단해서 번역한다.**
- `backup/`, `_INBOX`, `검토필요`, `*_back` 폴더를 위한 별도 제외 로직을 만들지 않는다 — 이미 `.gitignore`가 이 폴더들을 전부 덮고 있어서 origin에 push된 적이 없다. `git ls-tree`/`git show`로 origin만 보면 자동으로 제외된다.
- `Master_Index.md`를 EN 저장소로 복사하지 않는다. 이 파일은 KO 저장소에만 존재하는 생성 파일이다 (KO가 원본).
- EN 저장소에서 만든 로컬 커밋을 자동으로 push하지 않는다. push는 사용자에게 확인받는다.

## 절차

### 0. 경로

```
KO_ROOT = 이 스킬이 실행되는 저장소 루트 (D:\01.TheScriptureAudit_ko)
EN_ROOT = KO_ROOT에서 "_ko" 제거 (D:\01.TheScriptureAudit)
PROJECTS = the-scripture-audit, the-catholic-audit, the-sermon-audit
```

### 1. origin 최신화 + 대상 파일 목록 확보

```bash
git fetch origin
git ls-tree -r --name-only origin/main -- the-scripture-audit the-catholic-audit the-sermon-audit
```
결과 중 `.md` 파일만 사용한다. (gitignore된 backup/_INBOX/검토필요/*_back/04_DOCTRINE_DB/05_COLLISION_CARDS 등은 애초에 이 목록에 안 나온다.)

### 2. 번역 필요 파일 판별

`Master_Index.md`를 읽고 각 프로젝트 표의 `file_nm_ko` 컬럼(경로 매칭용으로는 실제 파일을 스캔해 `<!-- doc_no: ... -->` 헤더가 있는지로 판단하는 게 더 정확함 — 헤더가 없으면 인덱스에 없는 것과 동일 취급)을 확인한다.

- **신규**: 1단계 목록에 있는데, 로컬 KO 워킹트리의 해당 파일 맨 앞줄에 `<!-- doc_no: -->` 헤더가 없는 경우 → 번역 대상(신규)
- **갱신 필요**: 이미 `doc_no` 헤더가 있는데, 그 파일의 origin/main 마지막 커밋 시각이 헤더에 적힌 `ver`보다 최신인 경우:
  ```bash
  git log -1 --format=%cI origin/main -- "<ko relative path>"
  ```
  이 커밋 시각(을 `YYYYMMDD_HHmm`로 변환)이 파일에 적힌 KO `ver`보다 늦으면 → 번역 대상(갱신)

### 3. 원문 확보 (반드시 origin에서)

작업트리가 아니라 push된 버전을 원문으로 쓴다:
```bash
git show origin/main:"<ko relative path>"
```
이렇게 읽은 내용에서 기존 `<!-- doc_no -->` 헤더(있다면)는 제거하고 본문만 취한다.

### 4. doc_no 발급 / 재사용

- 신규 파일: 오늘 날짜 기준 `YYYYMMDD_NNNN` 중 그 프로젝트에서 아직 안 쓰인 다음 번호로 발급 (기존 Master_Index.md의 최대 번호 다음). doc_no는 **KO/EN 쌍이 공유하는 유일한 매칭 키** — 절대 파일명으로 매칭하지 않는다. 한 번 실행에서 같은 프로젝트에 신규 문서가 여러 개 나오면, 방금 배정한 번호를 그 자리에서 바로 다음 것으로 올려가며 하나씩 순차 배정한다 (동일 회차 내 doc_no 중복 배정 금지).
- 갱신 파일: 기존 doc_no 그대로 재사용, ver만 갱신.
- KO 쪽 ver: 2단계에서 구한 origin 커밋 시각(콘텐츠가 실제로 확정된 시점) 사용. "지금 시각"을 쓰지 않는다 — 나중에 KO/EN ver 비교가 부정확해짐.
- EN 쪽 ver: 이 번역 작업을 수행하는 지금 시각(`YYYYMMDD_HHmm`).

### 5. 번역 실행

3단계에서 확보한 원문을 Claude가 직접 읽고 신학 용어·KJV 어투를 살려 번역한다. 기계적 문자열 치환이나 외부 API 호출 금지 — 이 스킬을 실행하는 Claude 자신이 번역자다.

### 6. 파일 기록

- **KO 워킹트리**: `<!-- doc_no: {doc_no} | ver: {ko_ver} -->` 를 파일 맨 첫 줄에 기록 (신규면 새로 추가, 기존이면 ver만 갱신). 이건 원문 자체를 바꾸는 게 아니라 헤더 메타데이터만 다루는 것이므로 push 게이트 원칙과 충돌하지 않는다.
- **EN 저장소**: `EN_ROOT`의 동일 상대경로(프로젝트 폴더 이하 구조 동일)에 `<!-- doc_no: {doc_no} | ver: {en_ver} -->` + 번역 본문을 저장. 경로에 한글 폴더/파일명이 섞여 있으면 관례상 영문명으로 옮긴 하위폴더 구조를 따른다 (기존 EN 저장소의 대응 프로젝트 폴더 구조를 먼저 확인해서 맞춘다).

### 7. 인덱스 갱신

```bash
python scripts/rebuild_master_index.py
```

### 8. 커밋 (push는 안 함)

KO 저장소: 헤더만 바뀐 파일들을 커밋 (`chore: sync headers for N docs`).
EN 저장소: 새로 번역/갱신된 파일들을 커밋 (`feat: translate N docs from KO (pushed <date>)`).
두 저장소 다 **push는 사용자에게 명시적으로 물어보고** 승인받은 뒤에만 한다.

### 9. 보고

번역/갱신한 문서 수, 각 문서의 doc_no와 제목, 커밋 해시를 한글로 요약해서 보고한다. push 여부를 묻는다.
