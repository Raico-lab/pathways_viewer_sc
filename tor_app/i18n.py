"""画面の言語（日本語・英語）。

- 言語は user_data_dir()/settings.json の "language"（"ja" / "en"）に保存する。初めて起動したときは選んでもらう
  （main.py・ブラウザ版の webmain.py が、画面を作る前に ask_language_if_needed を呼ぶ）。
- 画面の文字は日本語を元にして tr("…") で包む。英語のときは訳の辞書（data/i18n/en/*.json。{日本語: 英語}）を引き、
  訳がなければ日本語のまま出す。差し込む値は tr("遺伝子 {n} 個", n=5) のように名前で渡す（訳の側で順番を変えられる）。
- 多くの文字はモジュールを読み込むときに決まるので、言語を変えたら再起動（ブラウザ版は再読み込み）して反映する。
- 用語の訳は data/i18n/GLOSSARY.md にそろえる。
"""
import json
import sys
from pathlib import Path

from .paths import resource_path, user_data_dir

LANGUAGES = {"ja": "日本語", "en": "English"}
_SETTINGS = user_data_dir() / "settings.json"
_language: str | None = None
_catalog: dict[str, str] | None = None


def _read_settings() -> dict:
    try:
        data = json.loads(_SETTINGS.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def saved_language() -> str | None:
    """保存した言語（まだ選んでいなければ None）。"""
    lang = _read_settings().get("language")
    return lang if lang in LANGUAGES else None


def language() -> str:
    """今の画面の言語（"ja" / "en"）。選んでいなければ日本語。"""
    global _language
    if _language is None:
        _language = saved_language() or "ja"
    return _language


def is_en() -> bool:
    return language() == "en"


def set_language(lang: str) -> None:
    """言語を保存する（画面に反映するのは次に起動したとき。restart を呼ぶとすぐ）。"""
    if lang not in LANGUAGES:
        return
    data = _read_settings()
    data["language"] = lang
    _SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    if on_web():
        # ブラウザ版: 次の起動画面（Python が動く前）も同じ言語で出せるよう、ブラウザにも残す（webapp/boot.js が読む）
        try:
            import js   # ブラウザ版だけにあるモジュール
            js.localStorage.setItem("pv-lang", lang)
        except Exception:
            pass


def _load_catalog() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(Path(resource_path("data", "i18n", "en")).glob("*.json")):
        try:
            out.update({k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items() if v})
        except (OSError, ValueError):
            continue
    return out


def catalog() -> dict[str, str]:
    """日本語 → 英語の訳の辞書（英語のときだけ読む）。"""
    global _catalog
    if _catalog is None:
        _catalog = _load_catalog() if is_en() else {}
    return _catalog


def tr(text: str, **values) -> str:
    """画面の文字。英語なら訳の辞書の訳（なければ元の日本語）。values は {名前} に差し込む。"""
    if is_en():
        text = catalog().get(text, text)
    return text.format(**values) if values else text


def pick(ja: str, en: str) -> str:
    """その場で両方を書くとき（長い HTML など、辞書に入れにくいもの）。"""
    return en if is_en() else ja


def on_web() -> bool:
    return sys.platform == "emscripten"


def restart() -> None:
    """言語を変えたあと、アプリを起動し直す（ブラウザ版はページを再読み込み。設定を保存し終えてから）。"""
    if on_web():
        import js   # ブラウザ版だけにあるモジュール
        from pyodide.ffi import create_proxy
        js.pvPyodide.FS.syncfs(False, create_proxy(lambda _err=None: js.location.reload()))
        return
    from PyQt6.QtCore import QProcess
    from PyQt6.QtWidgets import QApplication
    args = sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv
    QProcess.startDetached(sys.executable, args)
    QApplication.quit()


def ask_language_if_needed(then, parent=None) -> None:
    """初めて起動したとき（言語をまだ選んでいないとき）、日本語か英語かを尋ねて保存し、then() を呼ぶ（選んであればすぐ呼ぶ）。
    ブラウザ版は画面を止めて答えを待てないので、押したときに then を呼ぶ形にしている。"""
    if saved_language() is not None:
        then()
        return
    from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
    dialog = QDialog(parent)
    dialog.setWindowTitle("言語 / Language")
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("表示する言語を選んでください。\nChoose the display language."))
    row = QHBoxLayout()

    def choose(lang: str) -> None:
        global _language, _catalog
        set_language(lang)
        _language, _catalog = lang, None
        dialog.accept()
        then()

    for lang, label in LANGUAGES.items():
        button = QPushButton(label)
        button.clicked.connect(lambda _=False, lang=lang: choose(lang))
        row.addWidget(button)
    layout.addLayout(row)
    _keep_dialog.append(dialog)
    if on_web():
        dialog.show()
    else:
        dialog.exec()


_keep_dialog: list = []   # ブラウザ版で、選ぶまでダイアログを消さないように持っておく
