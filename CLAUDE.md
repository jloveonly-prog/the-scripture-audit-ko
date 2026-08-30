# CLAUDE.md

이 파일은 Claude Code가 이 디렉토리에서 작업할 때 항상 따라야 하는 규칙을 담습니다.

## Backup 폴더 정책 (생태계 공통 규칙)

- `backup/` 폴더 및 그 하위의 모든 파일/폴더는 **git으로 절대 커밋하지 않는다.**
  - `.gitignore`에 `**/backup/` 규칙이 있는지 먼저 확인하고 없으면 추가한다. (이 저장소는 이미 반영되어 있음)
- `backup/` 하위 내용은 **어떤 공개 채널(웹사이트, 배포, Keep 등)에도 절대 노출하지 않는다.**
- 공개하고 싶은 문서는 애초에 `backup/`에 두지 않는다.
- 이 정책은 `D:\00.TheScriptureMaster` 생태계(00~06, 99) 전체에 공통 적용된다.

## 이 디렉토리 (01.TheScriptureAudit_ko — KO, 원본)

- QVCAP 감사 엔진(한글판). `the-scripture-audit`, `the-catholic-audit`, `the-sermon-audit` 세 하위 유닛을 포함.
- **이 저장소가 원본(source of truth)**입니다. 여기서 작성/검증된 문서를 영문으로 번역해서 `01.TheScriptureAudit`(EN)로 이관합니다.
- 검증 완료된 `REPORT` 폴더의 문서만 `02.TheScriptureSynagogue`로 이관됩니다. 이 저장소에서 `04.TheScriptureKeep`으로 직접 배포하지 않습니다.
- 문서 관리: 관리 대상 문서는 파일 맨 첫 줄에 `<!-- doc_no: YYYYMMDD_NNNN | ver: YYYYMMDD_HHmm -->` 한 줄만 남긴다 (예전의 긴 YAML frontmatter 블록은 폐기). `doc_no`는 KO/EN 쌍이 공유하는 유일한 매칭 키(영문·숫자만, 한글 파일명으로 매칭하지 않음), `ver`는 파일별 마지막 수정 시각. `Master_Index.md`는 `scripts/rebuild_master_index.py`가 두 저장소를 스캔해 생성하는 **생성 파일**이다 — 손으로 고치지 말고 스크립트를 다시 실행해서 갱신한다.
- **git에서 제외된 폴더는 번역·이관 대상이 아니다**: `backup/`, `_INBOX`(로 시작하는 폴더), `검토필요/`, `_back`으로 끝나는 폴더, `the-catholic-audit/04_DOCTRINE_DB/_SOURCE/`는 KO→EN 번역/복사 작업에서 항상 제외한다. 이런 폴더는 원자료·미검토 초안이지 배포 대상 문서가 아니므로, 새 문서를 찾아 번역하는 어떤 도구·스킬도 이 폴더들은 스캔 대상에서 빼야 한다.
  - 특히 `_SOURCE/`는 **이 저장소(KO) 안에 있지만 내용물은 영문**이다 — 바티칸 공식 사이트에서 받은 제3자 원문(가톨릭 교리서·공의회 문헌 등)으로, 한국어 교리 카드의 인용을 교차언어 대조 검증하는 데만 쓴다. KO/EN 번역쌍(doc_no) 체계의 일부가 아니며, EN 저장소로 이관하지도 않는다.
