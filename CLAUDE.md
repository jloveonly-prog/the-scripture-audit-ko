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
- 문서 관리: 각 REPORT 파일의 frontmatter에 `doc_no`(형식: `YYYYMMDD_NNNN`)를 부여하고, `Master_Index.md`는 `doc_no / file_nm / file_nm_ko / 번역유무 / 줄수 / 마지막_update` 6컬럼 표로 관리한다 (상세 메타데이터 중복 섹션은 두지 않는다).
