# 한국어 현대어 성경 (Korean Modern Bible)

개역한글 성경을 자연스러운 현대 한국어 구어체로 옮긴 데이터셋입니다.

- **구약 39권 + 신약 27권 = 66권, 31,102절**
- 라이선스: [CC BY 4.0](LICENSE) — 출처 표기 시 상업적 이용 포함 자유롭게 사용 가능
- 번역 규칙: 아래 [번역 원칙](#번역-원칙) 참고

---

## 데이터 포맷

| 파일 | 용도 |
|------|------|
| `data/json/01_창세기.json` … | 책별 JSON (앱·서비스 개발) |
| `data/bible_all.json` | 전체 합본 JSON |
| `data/bible.csv` | 스프레드시트·데이터 분석 |
| `data/bible.db` | SQLite (모바일·임베디드 앱) |

### JSON 구조 (per-book)

```json
{
  "version": "1.0.0",
  "book_number": 1,
  "book": "창세기",
  "testament": "구약",
  "chapters": [
    {
      "chapter": 1,
      "verses": [
        {
          "verse": 1,
          "original": "태초에 하나님이 천지를 창조하시니라",
          "modern": "태초에 하나님이 하늘과 땅을 만들었어."
        }
      ]
    }
  ]
}
```

### CSV 컬럼

```
testament, book_number, book, chapter, verse, original, modern
```

### SQLite 테이블

```sql
SELECT * FROM verses
WHERE book = '창세기' AND chapter = 1
ORDER BY verse;
```

### 고유명사 표기

지명·인명 등 고유명사는 `{{이름}}` 형식으로 표시됩니다.

```
"{{모세}}가 {{시내}} 산에 올라갔어."
```

파싱 예시 (JavaScript):
```js
text.replace(/\{\{([^}]+)\}\}/g, '<b>$1</b>')
```

---

## 번역 원칙

1. 자연스러운 현대 구어체 반말 (`~했다`, `~이었다`)
2. 고어·한자어 → 쉬운 현대 한국어
3. "여호와" → "하나님"으로 통일
4. 지명·인명 등 고유명사는 원문 유지, `{{}}` 표시
5. 의미는 원문에 충실하되 표현만 현대화

---

## 버전 관리

[CHANGELOG](CHANGELOG.md) 참고.

| 버전 변경 | 의미 |
|----------|------|
| **MAJOR** (2.0.0) | 번역 철학·규칙 변경 |
| **MINOR** (1.1.0) | 책 추가 또는 대규모 개정 |
| **PATCH** (1.0.1) | 오탈자·고유명사 표기 수정 |

GitHub Releases에서 각 버전의 스냅샷을 다운로드할 수 있습니다.

---

## 데이터 재생성

소스 DB(`bible.db`)로부터 모든 포맷을 다시 생성하려면:

```bash
python3 scripts/export.py
```

---

## 번역자

기완 — 개인 프로젝트로, 현대인이 읽기 쉬운 성경 텍스트 데이터를 만들기 위해 제작했습니다.

---

## 번역 품질 안내

이 데이터셋은 **AI 생성 번역**을 기반으로 합니다. 신학적 정확성이나 교단별 해석을 보증하지 않습니다. 예배·설교·교육 등 신앙적 목적보다는 **텍스트 데이터·자연어처리·앱 개발** 용도에 적합합니다.

오역 발견 시 Issue로 제보해 주세요.

---

## 사용 예시
<img width="782" height="495" alt="image" src="https://github.com/user-attachments/assets/4c8313b1-a14e-48d2-ba95-87958b459040" />



### Python

```python
import json

with open("data/bible_all.json") as f:
    bible = json.load(f)

# 창세기 1장 1절 현대어 번역 출력
genesis = next(b for b in bible["books"] if b["book"] == "창세기")
print(genesis["chapters"][0]["verses"][0]["modern"])
```

```python
import sqlite3

conn = sqlite3.connect("data/bible.db")
cursor = conn.cursor()

# 특정 구절 조회
cursor.execute("""
    SELECT modern FROM verses
    WHERE book = '요한복음' AND chapter = 3 AND verse = 16
""")
print(cursor.fetchone()[0])
```

```python
import pandas as pd

df = pd.read_csv("data/bible.csv")

# 신약 전체 현대어 텍스트
nt = df[df["testament"] == "신약"]["modern"]
print(nt.head())
```

### JavaScript

```js
const fs = require("fs");
const bible = JSON.parse(fs.readFileSync("data/bible_all.json", "utf8"));

// 고유명사 강조 표시
function highlight(text) {
  return text.replace(/\{\{([^}]+)\}\}/g, "<b>$1</b>");
}

const genesis = bible.books.find((b) => b.book === "창세기");
const verse = genesis.chapters[0].verses[0].modern;
console.log(highlight(verse));
```

### 출처 표기 예시 (CC BY 4.0)

```
한국어 현대어 성경 데이터셋, 기완 (https://github.com/korean-modern-bible/opensource-bible), CC BY 4.0
```

---

## 기여

오역·오탈자 제보는 Issue로 남겨주세요.
Pull Request도 환영합니다.
