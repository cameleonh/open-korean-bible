#!/usr/bin/env python3
"""
DB → data/ 디렉토리 하위 JSON / CSV / SQLite 내보내기
사용: python3 scripts/export.py
"""
import sqlite3
import json
import csv
import shutil
import os
from pathlib import Path

SRC_DB = Path(__file__).parent.parent.parent / "bible" / "bible.db"
OUT_DIR = Path(__file__).parent.parent / "data"
VERSION_FILE = Path(__file__).parent.parent / "VERSION"

TESTAMENT = {
    range(1, 40): "구약",
    range(40, 67): "신약",
}


def get_testament(book_number: int) -> str:
    for r, name in TESTAMENT.items():
        if book_number in r:
            return name
    return "기타"


def load_all(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT book_number, book FROM verses "
        "WHERE is_translated=1 ORDER BY book_number"
    )
    books = cur.fetchall()

    all_data = []
    for book_number, book_name in books:
        cur.execute(
            "SELECT chapter, verse, text_original, text_modern FROM verses "
            "WHERE book_number=? AND is_translated=1 ORDER BY chapter, verse",
            (book_number,),
        )
        rows = cur.fetchall()

        chapters = {}
        for chapter, verse, original, modern in rows:
            chapters.setdefault(chapter, []).append({
                "verse": verse,
                "original": original,
                "modern": modern,
            })

        all_data.append({
            "book_number": book_number,
            "book": book_name,
            "testament": get_testament(book_number),
            "chapters": [
                {"chapter": ch, "verses": verses}
                for ch, verses in sorted(chapters.items())
            ],
        })

    return all_data


def export_json_per_book(all_data: list, version: str):
    json_dir = OUT_DIR / "json"
    json_dir.mkdir(parents=True, exist_ok=True)

    # 기존 파일 정리
    for f in json_dir.glob("*.json"):
        f.unlink()

    for book in all_data:
        payload = {"version": version, **book}
        filename = f"{book['book_number']:02d}_{book['book']}.json"
        with open(json_dir / filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"  JSON (per-book): {len(all_data)}개 파일 → data/json/")


def export_json_all(all_data: list, version: str):
    payload = {
        "version": version,
        "books": all_data,
    }
    out = OUT_DIR / "bible_all.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"  JSON (합본): data/bible_all.json ({size_mb:.1f} MB)")


def export_csv(all_data: list):
    out = OUT_DIR / "bible.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["testament", "book_number", "book", "chapter", "verse", "original", "modern"])
        for book in all_data:
            for ch_data in book["chapters"]:
                for v in ch_data["verses"]:
                    writer.writerow([
                        book["testament"],
                        book["book_number"],
                        book["book"],
                        ch_data["chapter"],
                        v["verse"],
                        v["original"],
                        v["modern"],
                    ])

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"  CSV: data/bible.csv ({size_mb:.1f} MB)")


def export_sqlite(src_path: Path):
    out = OUT_DIR / "bible.db"
    shutil.copy2(src_path, out)

    # 불필요한 컬럼 제거한 새 DB 생성
    conn = sqlite3.connect(out)
    conn.execute("PRAGMA journal_mode=DELETE")
    # is_translated 컬럼은 배포용 DB에선 의미없으므로 뷰 대신 내보낸 테이블 재구성
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bible (
            testament TEXT,
            book_number INTEGER,
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            original TEXT,
            modern TEXT
        )
    """)
    conn.execute("DELETE FROM bible")
    conn.execute("""
        INSERT INTO bible (testament, book_number, book, chapter, verse, original, modern)
        SELECT
            CASE WHEN book_number < 40 THEN '구약' ELSE '신약' END,
            book_number, book, chapter, verse, text_original, text_modern
        FROM verses
        WHERE is_translated = 1
        ORDER BY book_number, chapter, verse
    """)
    conn.execute("DROP TABLE IF EXISTS verses")
    conn.execute("ALTER TABLE bible RENAME TO verses")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_book_ch ON verses (book_number, chapter)")
    conn.commit()
    conn.close()
    conn2 = sqlite3.connect(out)
    conn2.execute("VACUUM")
    conn2.close()

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"  SQLite: data/bible.db ({size_mb:.1f} MB)")


def main():
    if not SRC_DB.exists():
        print(f"오류: 소스 DB를 찾을 수 없습니다 — {SRC_DB}")
        return

    version = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "1.0.0"
    print(f"내보내기 시작 (version: {version})")

    conn = sqlite3.connect(SRC_DB)
    all_data = load_all(conn)
    conn.close()

    total_verses = sum(
        len(ch["verses"])
        for book in all_data
        for ch in book["chapters"]
    )
    print(f"  로드 완료: {len(all_data)}권, {total_verses:,}절")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    export_json_per_book(all_data, version)
    export_json_all(all_data, version)
    export_csv(all_data)
    export_sqlite(SRC_DB)

    print("완료.")


if __name__ == "__main__":
    main()
