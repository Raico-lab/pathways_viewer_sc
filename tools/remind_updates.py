"""出典の取り直しの時期が来たら、docs/TODO.md の「## 次にやる」の先頭に項目を足す（macOS の通知も出す）。

出典（SGD・BioGRID・YEASTRACT+ など）は更新されるので、3 か月ごと（1・4・7・10 月の 1 日）にまとめて取り直す。
1 回だけの確認（ONCE）も置ける。同じ項目がすでにあれば（済みでも）足さない。毎日動かしてよい
（launchd: ~/Library/LaunchAgents/com.rai.pathways-remind.plist、毎日 9 時とログイン時）。

使い方: python3 tools/remind_updates.py
"""
import datetime
import subprocess
from pathlib import Path

TODO = Path(__file__).resolve().parent.parent / "docs" / "TODO.md"
HEADING = "## 次にやる\n"
QUARTER_MONTHS = (1, 4, 7, 10)
FIRST_QUARTER = datetime.date(2027, 1, 1)   # 2026-10 は 10-01〜04 に取ったので、次は 2027-01
# 1 回だけの確認: (期日, 項目の見出し, 本文)
ONCE = [
    (datetime.date(2026, 10, 22), "YEASTRACT+ のダウンロード（2026-10-22）",
     "2026 年版のダウンロードの欄（種ごとの .tsv.gz、論文付き）ができたか確かめる。できていれば、それで取り直して元の論文（PMID）も取り込む"),
]


def due_items(today: datetime.date) -> list[tuple[str, str]]:
    items = [(title, body) for day, title, body in ONCE if day <= today]
    if today >= FIRST_QUARTER:
        month = max(m for m in QUARTER_MONTHS if m <= today.month)
        items.append((f"出典の取り直し（{today.year}-{month:02d}）",
                      "各出典の新しい版を確かめてまとめて取り直す → DB を作り直して前の版と比べる"
                      "（経路タブの関係が消えた・向きが変わったものは文献で確かめる）→ data/sources.json の retrieved を直し、"
                      "論文の一覧（tools/fetch_paper_list.py）を作り直して公開する"))
    return items


def main() -> None:
    text = TODO.read_text(encoding="utf-8")
    new = [(t, b) for t, b in due_items(datetime.date.today()) if t not in text]
    if not new or HEADING not in text:
        return
    lines = "".join(f"- [ ] **{t}**: {b}\n" for t, b in new)
    TODO.write_text(text.replace(HEADING, HEADING + lines, 1), encoding="utf-8")
    for t, _ in new:
        print(f"TODO に足した: {t}")
        subprocess.run(["osascript", "-e", f'display notification "{t}" with title "Pathways: TODO に足しました"'],
                       check=False)


if __name__ == "__main__":
    main()
