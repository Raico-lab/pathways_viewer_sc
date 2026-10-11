"""左の「登録」タブ: 注目・拡張・選択・TFs・経路・条件・凡例の設定を、名前を付けて登録し、あとで呼び出す。

登録するときに、どの項目を含めるかを選べる。呼び出すと、登録した項目だけを操作中の表示枠（と全体の凡例）に当てはめる。
遺伝子は名前で保存するので、DB を作り直しても同じ遺伝子に戻せる（DB にない遺伝子は無視する）。
"""
import html
import json
from datetime import datetime

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMessageBox, QPushButton, QVBoxLayout, QWidget)

from .. import i18n
from ..db.vocab import type_label
from ..paths import user_data_dir
from ..roles import ROLE_INFO
from . import help_text

SAVE_FILE = user_data_dir() / "saved_views.json"

# 登録できる項目: キー → (表示名, 説明)
PARTS = {
    "focus": (i18n.tr("注目"), i18n.tr("注目している遺伝子・上流/下流の段数")),
    "grown": (i18n.tr("拡張"), i18n.tr("拡張と、それで加えた遺伝子・隠した段")),
    "picked": (i18n.tr("選択"), i18n.tr("地図で緑に選んでいる遺伝子")),
    "trf": ("TF", i18n.tr("左の TF 一覧でチェックした、マップの一番上の段に表示する転写因子")),
    "relation": (i18n.tr("経路"), i18n.tr("「経路」タブのチェックした遺伝子・表示経路・経路の段数・基準の遺伝子")),
    "conditions": (i18n.tr("条件"), i18n.tr("左の「条件」タブで外した条件と、最も上流の経路のチェック")),
    "legend": (i18n.tr("凡例"), i18n.tr("凡例の役割・制御の種類・作用のチェックと「表示」欄")),
}
EXPANSION_KEYS = ("extra", "uncapped", "excluded", "grown", "grown_info", "grown_order")
EFFECT_NAMES = {"activate": i18n.tr("促進"), "inhibit": i18n.tr("抑制"), "none": i18n.tr("作用不明")}


def _load() -> list[dict]:
    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [v for v in data.get("views", []) if isinstance(v, dict) and v.get("name")]


def _store(views: list[dict]) -> None:
    SAVE_FILE.write_text(json.dumps({"views": views}, ensure_ascii=False, indent=1), encoding="utf-8")


class SavedViewsPanel(QWidget):
    def __init__(self, tab):
        super().__init__()
        self.tab = tab
        self.views = _load()
        self._summary_text: str | None = None   # 右側の説明欄に出した登録の中身（選択を外したときに消すため）
        self._press_on_current = False          # 選んでいる登録をもう一度押したか（押したら選択を外す）
        self._filtering = False                 # アプリ全体のイベントフィルタを入れているか（選んでいる間だけ）
        layout = QVBoxLayout(self)
        layout.addWidget(self._heading(i18n.tr("登録する項目")))
        self.part_checks: dict[str, QCheckBox] = {}
        for key, (label, desc) in PARTS.items():
            cb = QCheckBox(label)
            cb.setChecked(True)
            cb.setToolTip(desc)
            self.part_checks[key] = cb
            layout.addWidget(cb)
        all_row = QHBoxLayout()
        for text, on in ((i18n.tr("すべて選択"), True), (i18n.tr("すべて解除"), False)):
            button = QPushButton(text)
            button.clicked.connect(lambda _c=False, on=on: self._check_all_parts(on))
            all_row.addWidget(button)
        layout.addLayout(all_row)
        name_row = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(i18n.tr("名前"))
        self.name_edit.returnPressed.connect(self.save_current)
        save_button = QPushButton(i18n.pick("登録", "Save"))
        save_button.clicked.connect(self.save_current)
        name_row.addWidget(self.name_edit, 1)
        name_row.addWidget(save_button)
        layout.addLayout(name_row)

        layout.addSpacing(8)
        layout.addWidget(self._heading(i18n.tr("登録した表示")))
        self.list = QListWidget()
        self.list.setMinimumHeight(160)
        self.list.currentItemChanged.connect(lambda *_: self._show_summary())
        self.list.itemClicked.connect(self._on_item_clicked)
        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)
        buttons = QHBoxLayout()
        self.load_button = QPushButton(i18n.tr("呼び出す"))
        self.load_button.setToolTip(i18n.tr("選んだ表示を、操作中の表示枠に当てはめます。ダブルクリックでも呼び出せます"))
        self.load_button.clicked.connect(self.load_selected)
        self.delete_button = QPushButton(i18n.tr("削除"))
        self.delete_button.clicked.connect(self.delete_selected)
        buttons.addWidget(self.load_button)
        buttons.addWidget(self.delete_button)
        layout.addWidget(self.list)
        layout.addLayout(buttons)

        layout.addStretch(1)
        layout.addWidget(tab.help_button("saved"))
        self._refresh_list()

    @staticmethod
    def _heading(text: str) -> QLabel:
        label = QLabel(text)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        return label

    def _check_all_parts(self, on: bool) -> None:
        for cb in self.part_checks.values():
            cb.setChecked(on)

    # ================= 選択を外す =================
    # 一覧の外（呼び出す・削除のボタンと右側の説明欄を除く）や一覧の空いたところを押す、または選んでいる登録を
    # もう一度押すと、選択を外す。アプリ全体のイベントフィルタは、登録を選んでいる間だけ入れる
    def _set_filtering(self, on: bool) -> None:
        if on == self._filtering:
            return
        self._filtering = on
        app = QApplication.instance()
        if on:
            app.installEventFilter(self)
        else:
            app.removeEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and self.list.currentItem() is not None:
            pos = event.globalPosition().toPoint()
            target = QApplication.widgetAt(pos)
            viewport = self.list.viewport()
            keep = [self.list, self.load_button, self.delete_button, self.tab.detail]
            inside = target is not None and any(target is w or w.isAncestorOf(target) for w in keep)
            item = self.list.itemAt(viewport.mapFromGlobal(pos)) if target is viewport else None
            self._press_on_current = item is not None and item is self.list.currentItem()
            if not inside or (target is viewport and item is None):
                self.clear_selection()
        return super().eventFilter(obj, event)

    def _on_item_clicked(self, item) -> None:
        if self._press_on_current and item is self.list.currentItem():
            self.clear_selection()
        self._press_on_current = False

    def _on_item_double_clicked(self, item) -> None:
        # ブラウザ版では 2 回目の押下で選択が外れるので、ダブルクリックした登録を選び直してから呼び出す
        self._press_on_current = False
        if self.list.currentItem() is not item:
            self.list.setCurrentItem(item)
        self.load_selected()

    def clear_selection(self) -> None:
        self.list.clearSelection()
        self.list.setCurrentItem(None)
        self._show_summary()

    # ================= 登録 =================
    def _capture(self, parts: list[str]) -> dict:
        """操作中の表示枠と、全体の凡例から、選んだ項目を取り出す（遺伝子は名前で持つ）。"""
        tab = self.tab
        pane = tab.active_pane
        names = tab.model.names
        state = pane.state()
        data: dict = {}
        if "focus" in parts:
            data["focus"] = {k: state[k] for k in ("focus", "up", "down")}
        if "trf" in parts:
            data["trf"] = list(state["trf"])
        if "grown" in parts:
            data["grown"] = {k: state[k] for k in EXPANSION_KEYS}
        if "picked" in parts:
            data["picked"] = list(state["picked"])
        if "relation" in parts:
            anchor = tab.rel_anchor.currentData()
            data["relation"] = {"genes": [names[p] for p in tab._rel_checked], "mode": tab._relation_mode(),
                                "steps": tab.rel_steps.value(),
                                "anchor": names.get(anchor) if anchor is not None else None}
        if "legend" in parts:
            data["legend"] = {"hidden": tab.hidden_filters(), "display": dict(tab.display_options)}
        if "conditions" in parts:
            data["conditions"] = {"off": sorted(tab.conditions_off), "top": tab.cond_top.isChecked()}
        return data

    def save_current(self) -> None:
        tab = self.tab
        if tab.active_pane is None or not tab.model:
            return
        name = self.name_edit.text().strip()
        parts = [k for k, cb in self.part_checks.items() if cb.isChecked()]
        if not name:
            QMessageBox.information(self, i18n.pick("登録", "Save view"), i18n.tr("名前を入力してください。"))
            return
        if not parts:
            QMessageBox.information(self, i18n.pick("登録", "Save view"), i18n.tr("登録する項目を 1 つ以上チェックしてください。"))
            return
        same = [i for i, v in enumerate(self.views) if v["name"] == name]
        if same and QMessageBox.question(self, i18n.tr("上書きの確認"),
                                     i18n.tr("「{name}」はすでに登録されています。上書きしますか？", name=name)) \
                != QMessageBox.StandardButton.Yes:
            return
        view = {"name": name, "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "parts": self._capture(parts)}
        if same:
            self.views[same[0]] = view
        else:
            self.views.append(view)
        try:
            _store(self.views)
        except OSError as e:
            QMessageBox.critical(self, i18n.tr("エラー"), i18n.tr("ファイルに書き込めませんでした。\n{error}", error=e))
            return
        self.name_edit.clear()
        self._refresh_list(select=name)
        tab.statusMessage.emit(i18n.tr("「{name}」を登録しました: {parts}", name=name,
                                       parts=i18n.tr("・").join(PARTS[k][0] for k in parts)))

    # ================= 呼び出し =================
    def load_selected(self) -> None:
        view = self._selected()
        tab = self.tab
        if view is None or tab.active_pane is None or not tab.model:
            return
        parts = view["parts"]
        pane = tab.active_pane
        by_name = tab.model.by_name
        ids = lambda names: [by_name[n.upper()] for n in names if n.upper() in by_name]   # noqa: E731

        # 凡例（全表示枠に共通）
        if "conditions" in parts:
            tab.set_conditions_off(set(parts["conditions"].get("off", [])), record=False)   # 履歴には下の load_state で残す
            tab.set_condition_top(parts["conditions"].get("top", False))
        if "legend" in parts:
            tab._set_hidden_filters(parts["legend"].get("hidden", {}))
            display = parts["legend"].get("display", {})
            tab.display_options.update({k: bool(v) for k, v in display.items() if k in tab.display_options})
            for view_pane in tab._views():
                view_pane.push_label_options()

        # 注目・拡張・緑の選択（操作中の表示枠）。登録していない項目は今のまま。
        # 注目だけを呼び出すときは、拡張は外す（別の遺伝子に注目したときと同じ）
        # 経路は、登録に含まれるときだけ消して当てはめ直す（含まれなければ今の経路の表示を保つ）
        if "relation" in parts:
            pane.clear_relation()
        state = pane.state()
        if "focus" in parts:
            state.update({k: v for k, v in parts["focus"].items() if k != "trf"})
            if "grown" not in parts:
                state.update({"extra": [], "uncapped": [], "excluded": [], "grown": [], "grown_info": {},
                              "grown_order": []})
        if "grown" in parts:
            state.update(parts["grown"])
        # TFs の表示。TFs の項目がなく注目だけを呼び出すときは外す（別の遺伝子に注目したときと同じ）。
        # 以前の形式（TFs を注目の項目に含めていた）も読めるようにする
        if "trf" in parts:
            state["trf"] = parts["trf"]
        elif "focus" in parts:
            state["trf"] = parts["focus"].get("trf", [])
        if "picked" in parts:
            state["picked"] = parts["picked"]
        pane.load_state(state)

        # 経路（地図を描き直してから、地図にある遺伝子だけチェックする）
        if "relation" in parts:
            r = parts["relation"]
            tab.set_relation_settings(ids(r.get("genes", [])), r.get("mode", "off"), int(r.get("steps", r.get("lo", 1))),
                                      by_name.get((r.get("anchor") or "").upper()))
        else:
            tab.apply_relation()   # 今の経路の設定のまま、描き直した地図に出し直す
        tab._save_view()
        tab.statusMessage.emit(i18n.tr("「{name}」を呼び出しました", name=view['name']))

    def delete_selected(self) -> None:
        view = self._selected()
        if view is None:
            return
        if QMessageBox.question(self, i18n.tr("削除の確認"), i18n.tr("「{name}」を削除しますか？", name=view['name'])) != QMessageBox.StandardButton.Yes:
            return
        self.views = [v for v in self.views if v is not view]
        try:
            _store(self.views)
        except OSError as e:
            QMessageBox.critical(self, i18n.tr("エラー"), i18n.tr("ファイルに書き込めませんでした。\n{error}", error=e))
        self._refresh_list()

    # ================= 一覧 =================
    def _selected(self) -> dict | None:
        item = self.list.currentItem()
        if item is None:
            return None
        name = item.data(Qt.ItemDataRole.UserRole)
        return next((v for v in self.views if v["name"] == name), None)

    def _refresh_list(self, select: str | None = None) -> None:
        self.list.clear()
        for v in sorted(self.views, key=lambda v: v["name"].casefold()):
            item = QListWidgetItem(v["name"])
            item.setData(Qt.ItemDataRole.UserRole, v["name"])
            item.setToolTip(self._describe(v))
            self.list.addItem(item)
            if v["name"] == select:
                self.list.setCurrentItem(item)
        self._show_summary()

    def _show_summary(self) -> None:
        """選んだ登録の中身を右側の説明欄に出す。選択を外したら、出していた中身を消す。"""
        view = self._selected()
        tab = self.tab
        self._set_filtering(view is not None)
        detail = getattr(tab, "detail", None)
        if detail is None:
            return
        if view is None:
            if self._summary_text is not None and detail.toPlainText() == self._summary_text:
                tab.clear_detail()
            self._summary_text = None
            return
        lines = self._describe(view).split("\n")
        body = "".join(f"<li>{html.escape(line)}</li>" for line in lines[1:])
        tab.selected = None
        tab._set_controls([])
        detail.setHtml(help_text._STYLE + f"<h3>{html.escape(view['name'])}</h3>"
                       f"<p>{html.escape(lines[0])}</p><ul>{body}</ul>")
        self._summary_text = detail.toPlainText()

    @staticmethod
    def _describe(view: dict) -> str:
        parts = view["parts"]
        sep, none = i18n.tr("、"), i18n.tr("なし")
        lines = [i18n.tr("登録日: {date}", date=view.get('saved_at', '') or i18n.tr("不明"))]
        if "focus" in parts:
            f = parts["focus"]
            lines.append(i18n.tr("注目: {genes}、上流 {up}・下流 {down} 段", genes=sep.join(f.get('focus', [])) or none,
                                 up=f.get('up'), down=f.get('down')))
        if "grown" in parts:
            g = parts["grown"]
            lines.append(i18n.tr("拡張: {genes}", genes=sep.join(g.get('grown', [])) or none)
                         + (i18n.tr("、加えた遺伝子 {n} 個", n=len(g.get('extra', []))) if g.get("extra") else ""))
        trf = parts["trf"] if "trf" in parts else parts.get("focus", {}).get("trf")
        if trf is not None:
            lines.append(f"TF: {sep.join(trf) or none}")
        if "picked" in parts:
            lines.append(i18n.tr("緑の選択: {genes}", genes=sep.join(parts['picked']) or none))
        if "relation" in parts:
            from .graph_pane import GraphPane
            r = parts["relation"]
            mode = GraphPane.RELATION_MODES.get(r.get("mode"), ("?",))[0]
            steps = r.get("steps", r.get("lo"))   # 以前の形式（lo〜hi）で登録したものは最小の段数
            span = "" if r.get("mode") == "off" or steps is None else i18n.tr(" {n} 段", n=steps)
            anchor = i18n.tr("、基準 {gene}", gene=r['anchor']) if r.get("anchor") else ""
            lines.append(i18n.tr("経路: {mode}{span}: {genes}", mode=mode, span=span,
                                 genes=sep.join(r.get('genes', [])) or i18n.tr("遺伝子なし")) + anchor)
        if "legend" in parts:
            h = parts["legend"].get("hidden", {})
            hidden = ([ROLE_INFO[k][0] for k in h.get("roles", []) if k in ROLE_INFO]
                      + [type_label(k) for k in h.get("types", [])]
                      + [EFFECT_NAMES.get(k, k) for k in h.get("effects", [])])
            lines.append(i18n.tr("凡例: 隠す項目 {items}", items=sep.join(hidden)) if hidden else i18n.tr("凡例: すべて表示"))
        if "conditions" in parts:
            from .. import conditions
            names = conditions.labels()
            off = parts["conditions"].get("off", [])
            lines.append((i18n.tr("条件: 外す条件 {items}", items=sep.join(names.get(k, k) for k in off)) if off
                          else i18n.tr("条件: すべて選択"))
                         + (i18n.tr("、最も上流の経路") if parts["conditions"].get("top") else ""))
        return "\n".join(lines)
