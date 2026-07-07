# 교리 카드 스키마 (Doctrine Card Schema)

> 모든 교리 카드는 이 형식을 따릅니다. 각 카드는 독립적인 .md 파일입니다.

---

## 필드 정의

| 필드 | 타입 | 필수 | 설명 |
|:---|:---|:---:|:---|
| `id` | string | ✅ | 고유 식별자 (예: CCC-1257, TRENT-S06-C09) |
| `title` | string | ✅ | 교리 제목 (한글) |
| `source` | string | ✅ | 출처 문헌명 |
| `section` | string | ✅ | 조항/Canon 번호 |
| `authority` | enum | ✅ | De Fide / Sententia Certa / Sententia Communis / Opinió / Pastoral |
| `anathema` | bool | ✅ | 파문 조항 여부 |
| `year` | int | ✅ | 제정/발표 년도 |
| `text_ko` | string | ✅ | 핵심 내용 (한글 요약) |
| `text_la` | string | | 라틴어 원문 (있을 경우) |
| `tags` | list | ✅ | 주제 태그 |
| `claims` | list | ✅ | 이 교리가 주장하는 명제들 |
| `negates` | list | ✅ | 이 교리가 부정하는 명제들 |
| `collisions` | list | | 충돌하는 다른 교리 카드 ID |

## 태그 체계

### 주제 태그
구원론, 성사론, 교회론, 교황론, 마리아론, 종말론,
세례, 성체, 고해, 견진, 혼인, 서품, 병자성사,
은총, 공로, 칭의, 성화, 연옥, 면죄부, 림보,
무류성, 수위권, 교도권, 공의회, 전통, 계시

### 논리 태그
필수, 금지, 허용, 조건부, 절대, 통상적, 사목적

### 교의 등급 태그
de_fide, sententia_certa, sententia_communis, opinió, pastoral

## 교리 카드 템플릿

```markdown
# [ID] — [제목]

| 항목 | 내용 |
|:---|:---|
| **ID** | |
| **출처** | |
| **조항** | |
| **교의 등급** | |
| **파문(Anathema)** | |
| **연도** | |

## 원문 (요약)
> 

## 태그
``, ``

## 주장 (Claims)
1. 
2. 

## 부정 (Negates)
1. 
2. 

## 관련 충돌
- → [COL-000]
```
