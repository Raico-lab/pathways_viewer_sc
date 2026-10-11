"""メインウィンドウ（3 タブ構成）。"""
import subprocess
import sys
import threading

from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QTabWidget,
                             QVBoxLayout, QWidget)

from .. import datastore, i18n, server
from ..db import Database
from ..paths import TITLE, TITLE_HTML, user_data_dir
from .db_tab import DatabaseTab
from . import help_text
from .network_tab import NetworkTab
from .sources_tab import SourcesTab

# メニューの「使い方」: Help ボタンと同じ説明（pathways_app/ui/help_text.py）に、データの保存場所を加える
HELP_TEXT = f"<h2>{TITLE_HTML}</h2>" + help_text.ALL + i18n.pick("""<h3>データ</h3>
<p>データベースはサーバー（公開しているブラウザ版の置き場）の版が正です。地図を軽く描くため、この PC にも写しを置いて使います。
起動するたびにサーバーの版と照らし、新しい版があれば自動で入れ替えます（状態の帯に知らせます）。
「ファイル &gt; 最新データを確認」でいつでも確かめられ、「ヘルプ &gt; データの情報」で今のデータの版と取得元が分かります。
サーバーにつながらないときは、この PC の写しでそのまま使えます。情報源タブの論文・サイトの情報も、サーバーから取ります。</p>""", """<h3>Data</h3>
<p>The database on the server (where the browser version is published) is the reference copy. To draw maps quickly, the app keeps a
local copy on this PC. Each time it starts, it compares the local copy with the server and replaces it automatically when a newer
version is available (shown in the status bar). Use "File &gt; Check for data updates" to check at any time, and
"Help &gt; Data information" to see the current data version and where it came from.
Without a server connection, the local copy is used as is. Paper and website details in the Sources tab also come from the server.</p>""")


class _Done(QObject):
    """裏のスレッドの結果を画面のスレッドに渡す。"""
    update_checked = pyqtSignal(object, bool)   # (server.UpdateStatus, 手動で確認したか)
    downloaded = pyqtSignal(object)             # バックアップのパス、または失敗した例外


# 「ヘルプ > このアプリについて」: 著作権・ライセンス・保証がないこと・ソースの場所（GPLv3 の第 5 条 d が求める表示）
SOURCE_URL = "https://github.com/Raico-lab/signal-pathway-viewer"
CONTACT = "25wm2519@student.gs.chiba-u.jp"   # 連絡先（作者）
MANUAL_URL = SOURCE_URL + "/blob/main/docs/MANUAL.md"   # 画像付きの操作ガイド（docs/MANUAL.md）
MANUAL_URL_EN = SOURCE_URL + "/blob/main/docs/MANUAL.en.md"   # 英語版（docs/MANUAL.en.md）


def manual_url() -> str:
    """今の言語の操作ガイドの URL。"""
    return MANUAL_URL_EN if i18n.is_en() else MANUAL_URL



ABOUT_TEXT = (
    "<b>Pathways viewer for <i>Saccharomyces cerevisiae</i></b><br>"
    "Copyright (C) 2026 Rai Katsukawa<br>"
    + i18n.pick(
        f"連絡先: <a href='mailto:{CONTACT}'>{CONTACT}</a><br><br>"
        "このプログラムはフリーソフトウェアです。GNU General Public License version 3（GPLv3）の条件のもとで、"
        "再配布・改変ができます。<b>このプログラムは無保証です。</b>詳しくは同梱の LICENSE をご覧ください。<br><br>"
        f"ソース: <a href='{SOURCE_URL}'>{SOURCE_URL}</a><br>"
        "ほかの部品のライセンス: THIRD_PARTY_NOTICES.md（PyQt6・Qt・Cytoscape.js など）<br>"
        "データの利用条件: DATA_LICENSES.md（出典ごとの条件に従います。情報源タブに出典を並べています）<br>"
        "SGD・Gene Ontology・UniProt・Alliance of Genome Resources・Leutert et al. 2023（Zenodo のキナーゼと基質）のデータは CC BY 4.0、"
        "BioGRID と Leutert et al. 2023（リン酸化の変化。著者らの解析のリポジトリ）のデータは MIT、Complex Portal は CC0 で、"
        "このアプリのために選択・統合・要約して使っています",
        f"Contact: <a href='mailto:{CONTACT}'>{CONTACT}</a><br><br>"
        "This program is free software: you can redistribute it and/or modify it under the terms of the "
        "GNU General Public License version 3 (GPLv3). <b>This program comes with ABSOLUTELY NO WARRANTY.</b> "
        "See the bundled LICENSE for details.<br><br>"
        f"Source: <a href='{SOURCE_URL}'>{SOURCE_URL}</a><br>"
        "Licenses of other components: THIRD_PARTY_NOTICES.md (PyQt6, Qt, Cytoscape.js, etc.)<br>"
        "Data terms of use: DATA_LICENSES.md (each source's terms apply; the sources are listed in the Sources tab)<br>"
        "Data from SGD, Gene Ontology, UniProt, Alliance of Genome Resources and Leutert et al. 2023 (kinases and substrates on Zenodo) "
        "are CC BY 4.0; data from BioGRID and Leutert et al. 2023 (phosphorylation changes; the authors' analysis repository) are MIT; "
        "Complex Portal is CC0. They have been selected, integrated and summarized for this app.")
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db: Database | None = None
        self.setWindowTitle(TITLE)
        self.resize(1500, 900)

        self.db_tab = DatabaseTab()
        self.network_tab = NetworkTab()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.network_tab, i18n.tr("ネットワーク"))
        self.tabs.addTab(self.db_tab, i18n.tr("データベース"))
        self.sources_tab = SourcesTab()
        self.tabs.addTab(self.sources_tab, i18n.tr("情報源"))
        # タブの並びの右端: 画像付きの操作ガイド（GitHub の docs/MANUAL.md）を開く
        manual = QLabel(f"<a href='{manual_url()}'>{i18n.tr('操作ガイド')}</a>")
        manual.setOpenExternalLinks(True)
        manual.setContentsMargins(0, 0, 10, 0)
        manual.setToolTip(i18n.tr("初めて使う人向けの、画像付きの操作ガイドをブラウザで開きます"))
        self.tabs.setCornerWidget(manual)
        # 画面上部の案内（サーバーに新しいデータがあるときだけ出す）
        self.banner = QFrame()
        self.banner.setStyleSheet("QFrame { background: #fff8e1; border-bottom: 1px solid #ffe082; }")
        bar = QHBoxLayout(self.banner)
        bar.setContentsMargins(10, 4, 10, 4)
        self.banner_label = QLabel()
        self.banner_later = QPushButton(i18n.tr("閉じる"))
        self.banner_later.clicked.connect(self.banner.hide)
        bar.addWidget(self.banner_label, 1)
        bar.addWidget(self.banner_later)
        self.banner.hide()
        self._update_status: server.UpdateStatus | None = None
        self._done = _Done()
        self._done.update_checked.connect(self._on_update_checked)
        self._done.downloaded.connect(self._on_downloaded)
        central = QWidget()
        column = QVBoxLayout(central)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(self.banner)
        column.addWidget(self.tabs, 1)
        self.setCentralWidget(central)

        self.db_label = QLabel()
        self.statusBar().addPermanentWidget(self.db_label)
        self.db_tab.set_network(self.network_tab)
        self.network_tab.statusMessage.connect(lambda m: self.statusBar().showMessage(m, 6000))
        self._build_menu()

    def _build_menu(self):
        file_menu = self.menuBar().addMenu(i18n.tr("ファイル"))
        for text, slot in ((i18n.tr("最新データを確認"), lambda: self.check_update(manual=True)),
                           (i18n.tr("データの保存フォルダを開く"), self.open_data_folder)):
            action = QAction(text, self)
            action.triggered.connect(slot)
            file_menu.addAction(action)
        file_menu.addSeparator()
        quit_action = QAction(i18n.tr("終了"), self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        help_menu = self.menuBar().addMenu(i18n.tr("ヘルプ"))
        about = QAction(i18n.tr("使い方"), self)
        about.triggered.connect(lambda: QMessageBox.information(self, i18n.tr("使い方"), HELP_TEXT))
        help_menu.addAction(about)
        guide = QAction(i18n.tr("操作ガイド（画像付き）を開く"), self)
        guide.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(manual_url())))
        help_menu.addAction(guide)
        info = QAction(i18n.tr("データの情報"), self)
        info.triggered.connect(self.show_data_info)
        help_menu.addAction(info)
        license_action = QAction(i18n.tr("このアプリについて"), self)
        license_action.triggered.connect(lambda: QMessageBox.about(self, i18n.tr("このアプリについて"), ABOUT_TEXT))
        help_menu.addAction(license_action)
        # 言語の切り替え（どちらの言語でも見つけられるよう、名前は両方で書く）。選ぶと保存して起動し直す
        lang_menu = self.menuBar().addMenu("言語 / Language")
        for lang, label in i18n.LANGUAGES.items():
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(lang == i18n.language())
            action.triggered.connect(lambda _=False, lang=lang: self._change_language(lang))
            lang_menu.addAction(action)

    def _change_language(self, lang: str) -> None:
        """言語を変える: 保存して、アプリを起動し直す（ブラウザ版はページを読み直す）。画面の文字は読み込むときに決まるため。"""
        if lang == i18n.language():
            return
        i18n.set_language(lang)
        i18n.restart()

    # ---- DB を開く ----
    def start(self) -> bool:
        """起動時にローカル DB を用意して開く。DB はサーバーの版が正で、この PC には写しを置く（編集はしない）。
        サーバーから入れた写しがあればそれを使い、なければアプリに同梱の版を使う。そのあと裏でサーバーと照らし、
        新しい版があれば自動で入れ替える。"""
        try:
            if not datastore.LOCAL_DB.exists():
                datastore.install_bundled(backup=False)
            elif datastore.bundled_is_newer():
                if datastore.installed_info().get("source") == "server" and server.enabled():
                    datastore.keep_local()   # サーバーから入れた版のほうが新しいことがある（このあとサーバーと照らす）
                else:
                    datastore.install_bundled(backup=False)
        except OSError as e:
            QMessageBox.critical(self, i18n.tr("エラー"), i18n.tr("データを準備できませんでした。\n{error}", error=e))
            return False
        if not self.open_database():
            return False
        # サーバーがあれば、裏で新しいデータを確かめる（画面はサーバーの応答を待たない）
        if server.enabled():
            self.check_update(manual=False)
        return True

    # ---- サーバー（データの更新） ----
    def check_update(self, manual: bool) -> None:
        threading.Thread(target=lambda: self._done.update_checked.emit(server.check_update(), manual),
                         daemon=True).start()

    def _on_update_checked(self, status, manual: bool) -> None:
        self._update_status = status
        label = i18n.tr("{version}版", version=status.version) if status.version else ""
        if status.state == "new":
            self.download_update()   # サーバーの版が正なので、尋ねずに入れ替える
        elif status.state == "app_old":
            self.banner_label.setText(i18n.tr("新しいデータ {label} を使うには、アプリの更新が必要です（ブラウザ版の「デスクトップアプリ」タブ）", label=label))
            self.banner.show()
        elif status.state == "latest":
            self.statusBar().showMessage(i18n.tr("データ: {label} 最新です", label=label), 6000)
        elif status.state == "offline":
            self.statusBar().showMessage(i18n.tr("サーバーにつながりません。この PC の写しで表示しています"), 6000)
        if manual and status.state in ("off", "latest", "offline"):
            QMessageBox.information(self, i18n.tr("最新データを確認"), {
                "off": i18n.tr("データを配信するサーバーは、設定されていません。"),
                "latest": i18n.tr("この PC のデータは最新です: {label}", label=label),
                "offline": i18n.tr("サーバーにつながりませんでした。この PC の写しで表示しています。")}[status.state])

    def download_update(self) -> None:
        status = self._update_status
        if not status or not status.manifest:
            return
        label = i18n.tr("{version}版", version=status.version) if status.version else ""
        self.statusBar().showMessage(i18n.tr("新しいデータ {label} を取り込んでいます…", label=label) if label
                                     else i18n.tr("新しいデータを取り込んでいます…"))

        def work():
            try:
                self._done.downloaded.emit(server.fetch_update(status.manifest))
            except Exception as e:  # noqa: BLE001
                self._done.downloaded.emit(e)
        threading.Thread(target=work, daemon=True).start()

    def _on_downloaded(self, result) -> None:
        if not isinstance(result, Exception):
            # 置き換えは画面のスレッドで、DB を閉じてから行う
            if self.db:
                self.db.engine.dispose()
            try:
                server.install_update(*result, self._update_status.manifest)
            except OSError as e:
                result = e
        if isinstance(result, Exception):
            self.statusBar().showMessage(i18n.tr("新しいデータを取り込めませんでした。この PC の写しのままです: {error}", error=result), 10000)
            self.open_database()
            return
        if self.open_database():
            version = self._update_status.version if self._update_status else ""
            self.statusBar().showMessage(i18n.tr("データを最新（{version}版）に更新しました", version=version) if version
                                         else i18n.tr("データを最新に更新しました"), 10000)

    def show_data_info(self) -> None:
        info = datastore.installed_info()
        source = {"bundled": i18n.tr("アプリに同梱のデータ"), "server": i18n.tr("サーバーから取得したデータ")}.get(
            info.get("source"), i18n.tr("不明"))
        lines = [i18n.tr("取得元: {source}", source=source)]
        if info.get("version"):
            lines.append(i18n.tr("版: {version}", version=info['version']))
        if info.get("at"):
            lines.append(i18n.tr("取り込んだ日時: {at}", at=info['at']))
        lines.append(i18n.tr("保存場所: {path}", path=datastore.LOCAL_DB))
        lines.append(i18n.tr("サーバー: {url}", url=server.config().get("base_url") if server.enabled() else i18n.tr("未設定")))
        QMessageBox.information(self, i18n.tr("データの情報"), "\n".join(lines))

    def open_database(self) -> bool:
        if self.db:
            self.db.engine.dispose()
        try:
            db = Database(str(datastore.LOCAL_DB))
            db.proteins()  # 接続確認
        except Exception as e:  # noqa: BLE001 - 破損などを利用者に伝える
            QMessageBox.critical(self, i18n.tr("DB を開けません"),
                                 i18n.tr("{error}\n\n「ファイル > データの保存フォルダを開く」で pathways.db を消してから起動し直すと、同梱のデータに戻ります。", error=e))
            return False
        self.db = db
        self.db_tab.set_database(db)
        self.network_tab.set_database(db)
        self.sources_tab.set_database(db)
        self.db_label.setText(i18n.tr("データ: {path}", path=datastore.LOCAL_DB))
        return True

    def open_data_folder(self):
        folder = str(user_data_dir())
        if sys.platform == "darwin":
            subprocess.run(["open", folder], check=False)
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
