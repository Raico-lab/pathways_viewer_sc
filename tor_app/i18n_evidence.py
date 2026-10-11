"""根拠欄（interactions.evidence）とカテゴリの説明（categories.description）を、英語の画面で出すときに英訳する。

- DB の中身は日本語のまま。画面に出す直前に evidence_en / category_description_en を通す（英語の画面のときだけ）。
  複合体の印（complex_groups.parse）・「文献で確認」の見分けなど、日本語の言葉で読むところは元の日本語で行う。
- 根拠欄は "; " でつないだ区切りごとに訳す。決まった書き方（取得日・PMID・条件の名前・IDEA・Deleteome など）は
  下の置き換えの規則で訳し、文献の要旨（"要旨: …"）は別に作った訳の辞書（data/i18n/en/evidence_summaries_*.json。
  {要旨の日本語（"要旨: " を除く）: 英語}）を引く。自由に書いた文（本文・注記など）は data/i18n/en/evidence_texts.json
  （{区切りの日本語: 英語}）を引く。訳がなければ、言葉ごとの置き換えをしたうえで残りは日本語のまま出す。
- 用語は data/i18n/GLOSSARY.md にそろえる。
"""
import json
import re
from pathlib import Path

from .paths import resource_path

_summaries: dict[str, str] | None = None
_texts: dict[str, str] | None = None
_cond_words: list[tuple[str, str]] | None = None
_cache: dict[str, str] = {}


def _load(pattern: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(Path(resource_path("data", "i18n", "en")).glob(pattern)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            out.update({k: v for k, v in data.items() if isinstance(v, str) and v})
    return out


def _summary_catalog() -> dict[str, str]:
    global _summaries
    if _summaries is None:
        _summaries = _load("evidence_summaries_*.json")
    return _summaries


def _text_catalog() -> dict[str, str]:
    global _texts
    if _texts is None:
        _texts = _load("evidence_texts*.json")
    return _texts


# 条件の名前（data/conditions.csv の label）の英語。conditions.csv に英語の列（label_en）があればそれを使い、
# なければ画面の訳の辞書、それもなければ YEASTRACT+ の小群の名前・下の表を使う
_COND_EXTRA = {
    "通常の増殖": "normal growth", "G1 期": "G1 phase", "S 期": "S phase", "G2 期": "G2 phase",
    "分裂期（M 期）": "M phase", "分裂期の終わり・細胞質分裂": "mitotic exit / cytokinesis",
    "細胞周期の同調（時期は問わない）": "cell cycle synchronized (any phase)", "ラパマイシン": "rapamycin",
    "小胞体ストレス": "ER stress", "分類なし": "not classified", "未分類": "unassigned",
    "条件の記録なし": "No condition recorded",
    # 文献の CSV の条件の書き方（自由に書いたもの）でよく出る言葉
    "分裂期": "M phase", "分裂期の終わり": "mitotic exit", "細胞質分裂": "cytokinesis", "M 期": "M phase",
    "G1期": "G1 phase", "S期": "S phase", "G2期": "G2 phase", "M期": "M phase",
    "アミノ酸飢餓": "amino acid starvation", "窒素飢餓": "nitrogen starvation", "グルコース飢餓": "glucose starvation",
    "減数分裂": "meiosis", "窒素の飢餓": "nitrogen starvation", "アミノ酸の飢餓": "amino acid starvation",
    "熱": "heat", "高浸透圧": "hyperosmotic stress", "低浸透圧": "hypo-osmotic stress",
    "栄養の飢餓": "nutrient starvation", "薬剤": "drug", "フェロモン": "pheromone", "ガラクトース": "galactose",
    "イノシトール": "inositol", "カルシウム": "calcium", "低酸素": "hypoxia", "アミノ酸の制限": "amino acid limitation",
    "グルコース枯渇": "glucose depletion", "グルコース添加": "glucose addition", "鉄欠乏": "iron deficiency", "飢餓": "starvation", "通常時": "normal growth",
}


def _cond_table() -> list[tuple[str, str]]:
    """条件の名前（日本語 → 英語）。長い名前から当てるように並べる。"""
    global _cond_words
    if _cond_words is None:
        words = dict(_COND_EXTRA)
        try:
            from . import conditions
            from .i18n import catalog
            tr = catalog()
            for c in conditions.load():
                ja = getattr(c, "label_ja", c.label)
                en = getattr(c, "label_en", "") or tr.get(ja, "")
                if not en or en == ja:
                    en = _COND_EXTRA.get(ja) or (c.yeastract.split(" / ", 1)[-1] if c.yeastract else "")
                if en:
                    words[ja] = en
        except Exception:   # 条件の表が読めなくても、下の表だけで訳す
            pass
        _cond_words = sorted(words.items(), key=lambda kv: len(kv[0]), reverse=True)
    return _cond_words


# 言葉ごとの置き換え（決まった書き方の中に出る言葉）。長い言葉から当てる
_WORDS = {
    # 作用・種類
    "作用不明": "unknown effect", "促進": "activation", "抑制": "inhibition",
    "転写制御": "transcriptional regulation", "リン酸化": "phosphorylation", "脱リン酸化": "dephosphorylation",
    "ユビキチン化": "ubiquitination", "脱ユビキチン化": "deubiquitination", "メチル化": "methylation",
    "脱メチル化": "demethylation", "アセチル化": "acetylation", "脱アセチル化": "deacetylation",
    "SUMO 化": "sumoylation", "脱 SUMO 化": "desumoylation", "ネディレーション": "neddylation", "NEDD 化": "neddylation",
    "タンパク質分解（プロセシング）": "proteolytic processing", "タンパク質分解": "proteolysis",
    "酵素活性・修飾なし": "biochemical activity, no modification", "酵素活性": "biochemical activity",
    "修飾なし": "no modification", "グリコシル化": "glycosylation", "脱グリコシル化": "deglycosylation",
    "パルミトイル化": "palmitoylation", "プレニル化": "prenylation", "ミリストイル化": "myristoylation",
    "ADP リボシル化": "ADP-ribosylation", "局在制御": "localization control", "機構不明": "unknown mechanism",
    "結合": "binding", "複合体": "complex", "転写因子": "transcription factor", "上流": "upstream", "下流": "downstream",
    # よく出る言い回し
    "直接かは不明": "unclear whether direct", "間接の作用を含む": "may include indirect effects",
    "間接の作用": "indirect effect", "直接の作用": "direct effect", "間接": "indirect", "直接": "direct",
    "記録の向きと一致": "agrees with the recorded effect", "標的": "target", "推定": "inferred",
    "を介する": "", "依存": "-dependent", "など": " etc.", "取得": "retrieved",
}
_WORDS_SORTED = sorted(_WORDS.items(), key=lambda kv: len(kv[0]), reverse=True)

_JA = re.compile(r"[぀-ヿ㐀-鿿＀-￯]")


def has_japanese(text: str) -> bool:
    return bool(_JA.search(text or ""))


def _conds(text: str) -> str:
    """条件の名前を英語にする（"・" で並べたものも。長い名前から当てる）。"""
    for ja, en in _cond_table():
        if ja in text:
            text = text.replace(ja, en)
    return text


def _words(text: str) -> str:
    text = _conds(text)
    for ja, en in _WORDS_SORTED:
        if ja in text:
            text = text.replace(ja, en)
    return _punct(text)


def _punct(text: str) -> str:
    """全角の記号を英語の書き方にする。"""
    text = re.sub(r"\s*（", " (", text).replace("）", ")")
    text = re.sub(r"\s*[、，]\s*", ", ", text)
    text = re.sub(r"\s*・\s*", ", ", text)
    text = re.sub(r"\s*：\s*", ": ", text)
    text = text.replace("。", ". ").replace("〜", "–").replace("「", "“").replace("」", "”")
    text = re.sub(r"\(\s+", "(", text)
    return re.sub(r"  +", " ", text).strip()


def _sign(word: str) -> str:
    return {"促進": "activation", "抑制": "inhibition", "作用不明": "unknown effect"}.get(word, word)


def _record(m: re.Match) -> str:
    """（記録の向きと一致）・（記録の促進を直した）・（記録の抑制のまま）"""
    s = m.group(1)
    if s == "記録の向きと一致":
        return "(agrees with the recorded effect)"
    mm = re.fullmatch(r"記録の(促進|抑制|作用不明)を直した", s)
    if mm:
        return f"(corrected from the recorded {_sign(mm.group(1))})"
    mm = re.fullmatch(r"記録の(促進|抑制|作用不明)のまま", s)
    if mm:
        return f"(recorded {_sign(mm.group(1))} kept)"
    return m.group(0)


# 区切りごとの規則（順に当てる。re.sub で置き換え、最後に言葉ごとの置き換えをする）
_RULES: list[tuple[re.Pattern, object]] = [(re.compile(p), r) for p, r in [
    # 取得日
    (r"（([\d\-, ]+) 取得）", r" (retrieved \1)"),
    (r"^文献で確認（([^、]*)、PubMed で PMID と要旨を確認）",
     lambda m: f"Literature-verified ({'no date' if m.group(1) == '日付なし' else m.group(1)}; PMID and abstract checked in PubMed)"),
    (r"^activator と inhibitor の両方の報告あり（作用不明）$", "Reported as both activator and inhibitor (unknown effect)"),
    (r"^確度: ", "Confidence: "),
    (r"^実験の規模: 網羅的な実験だけ$", "Scale: high-throughput only"),
    (r"^実験の規模: 個別実験あり$", "Scale: includes low-throughput experiments"),
    (r"^実験の規模: ", "Scale: "),
    (r"^フィードバック（下流から上流への作用）$", "Feedback (downstream acting on upstream)"),
    (r"^複合体 (.+?)（(上流|下流)）として（論文は複合体の名前で書いている）$",
     lambda m: f"As part of complex {m.group(1)} ({'upstream' if m.group(2) == '上流' else 'downstream'}; the paper names the complex)"),
    (r"^⚠ 出典で作用が食い違う（この関係 (\S+) / 公開データ (\S+)）$",
     lambda m: f"⚠ Sources disagree on the effect (this relation: {_sign(m.group(1))} / public data: {_sign(m.group(2))})"),
    (r"^⚠ 破壊株データでは逆向き: ", "⚠ Opposite in deletion data: "),
    (r"^⚠ 条件ごとの発現では逆向き: ", "⚠ Opposite in expression across conditions: "),
    (r"^⚠ IDEA では逆向き: ", "⚠ Opposite in IDEA: "),
    (r"^⚠ ", "⚠ "),
    (r"^作用の向き: ", "Effect from: "),
    (r"^公開データ: ", "Public data: "),
    (r"^条件: ", "Condition: "),
    (r"^注記: ", "Note: "),
    (r"^本文: ", "Full text: "),
    (r"^要旨: ", "Summary: "),
    # 出典ごとの書き方
    (r"IDEA（Hackett et al\. 2020、転写因子の誘導）", "IDEA (Hackett et al. 2020, TF induction)"),
    (r"誘導 ([\d.]+) 分で標的が(増加|減少)（log2 ([+\-−]?[\d.]+)）",
     lambda m: f"target {'up' if m.group(2) == '増加' else 'down'} {m.group(1)} min after induction (log2 {m.group(3)})"),
    (r"破壊株データ Deleteome（Kemmeren et al\. 2014）", "Deletion data Deleteome (Kemmeren et al. 2014)"),
    (r"転写因子の破壊で標的が(増加|減少)（log2 比 ([^,）]+), p=([^）]+)）",
     lambda m: f"target {'up' if m.group(1) == '増加' else 'down'} in the TF deletion (log2 ratio {m.group(2)}, p={m.group(3)})"),
    (r"条件ごとの発現（SPELL）と転写因子の活性の目印", "Expression across conditions (SPELL) and TF activity markers"),
    (r"転写因子の活性が変わる条件（(.+)）で、標的が活性と(同じ|逆)向きに動く（平均 z ([^）]+)）",
     lambda m: f"in conditions that change TF activity ({_conds(m.group(1))}), the target moves "
               f"{'with' if m.group(2) == '同じ' else 'against'} the activity (mean z {m.group(3)})"),
    (r"→ (促進|抑制)と推定", lambda m: f"→ inferred {_sign(m.group(1))}"),
    (r"→ (促進|抑制|作用不明)", lambda m: f"→ {_sign(m.group(1))}"),
    (r"（(記録の[^（）]+)）", _record),
    (r"（細胞周期の発現（SPELL））", " (cell-cycle expression (SPELL))"),
    (r"組むサイクリン (\S+?) からの推定", r"inferred from the partner cyclin \1"),
    (r"GO-CAM「(.*)」: (直接)?(正|負)に制御(（間接）)?",
     lambda m: f"GO-CAM “{m.group(1)}”: {'directly ' if m.group(2) else ''}{'positively' if m.group(3) == '正' else 'negatively'}"
               f" regulates{' (indirect)' if m.group(4) else ''}"),
    (r"GO-CAM「(.*)」: 因果的に(正|負)の作用(（間接）)?",
     lambda m: f"GO-CAM “{m.group(1)}”: causally {'positive' if m.group(2) == '正' else 'negative'} effect"
               f"{' (indirect)' if m.group(3) else ''}"),
    (r"（YEASTRACT\+（([^（）]+)））", r" (YEASTRACT+ (\1))"),
    (r"SGD GO 注釈", "SGD GO annotation"),
    (r"（PhosphoGRID）: 部位 (.+?)(?: ほか (\d+) か所)?$",
     lambda m: " (PhosphoGRID): sites " + m.group(1).replace("・", ", ")
               + (f" and {m.group(2)} more" if m.group(2) else "")),
    (r"UniProt 修飾された残基", "UniProt modified residue"),
    (r"UniProt (\S+) 活性の調節", r"UniProt \1 activity regulation"),
    (r"（PMID ([\d, ]+?)(?: ほか (\d+) 報)?）",
     lambda m: f" (PMID {m.group(1)}" + (f" and {m.group(2)} more" if m.group(2) else "") + ")"),
    (r"(PMID: [\d, ]+) ほか (\d+) 報", r"\1 and \2 more"),
    (r"^Public data: (BioGRID|YEASTRACT\+)(.*?) (\S+)・(作用不明|促進|抑制)$",
     lambda m: f"Public data: {m.group(1)}{m.group(2)} {_words(m.group(3))}, {_sign(m.group(4))}"),
]]


_YEASTRACT_COND = re.compile(r"(条件: )?(.+?)（YEASTRACT\+（([^（）]+)））")


def segment_en(seg: str) -> str:
    """根拠欄の 1 区切りを英語にする。"""
    seg = seg.strip()
    if not seg or not has_japanese(seg):
        return seg
    if seg.startswith("要旨: "):
        body = seg[len("要旨: "):]
        en = _summary_catalog().get(body)
        return f"Summary: {en}" if en else seg
    en = _text_catalog().get(seg)
    if en:
        return en
    # 条件の名前（YEASTRACT+ の群・小群つき）。括弧の中は YEASTRACT+ の原文なので、そのまま残す
    m = _YEASTRACT_COND.fullmatch(seg)
    if m:
        return f"{'Condition: ' if m.group(1) else ''}{_punct(_conds(m.group(2)))} (YEASTRACT+: {m.group(3)})"
    out = seg
    for rx, rep in _RULES:
        out = rx.sub(rep, out)
    out = _words(out)
    if not has_japanese(out):
        return out
    # 決まった書き方で訳しきれない（自由に書いた文が残る）ときは、言葉ごとに混ぜて訳さず、
    # 前置き（本文・注記など）だけ英語にして、文は日本語のまま出す
    for ja, en in _HEADS:
        if seg.startswith(ja):
            rest = seg[len(ja):]
            if ja.endswith("（") and rest.endswith("）"):
                rest = rest[:-1]
                inner = _words(rest)
                return f"{en}{inner if not has_japanese(inner) else rest})"
            return f"{en}{rest}"
    return seg


# 自由に書いた文の前置き
_HEADS = [("要旨・本文: ", "Summary and full text: "), ("本文: ", "Full text: "), ("注記: ", "Note: "),
          ("条件: ", "Condition: "), ("間接の作用（", "Indirect effect ("), ("作用の向き: ", "Effect from: ")]


def evidence_en(text: str) -> str:
    """根拠欄の全体を英語にする（"; " で区切って 1 つずつ）。"""
    if not text or not has_japanese(text):
        return text or ""
    hit = _cache.get(text)
    if hit is None:
        hit = "; ".join(segment_en(p) for p in text.split("; "))
        if len(_cache) < 20000:
            _cache[text] = hit
    return hit


_GENETIC = {"生育の低下": "reduced growth", "表現型の増強": "phenotypic enhancement", "合成致死": "synthetic lethality",
            "負の遺伝的相互作用": "negative genetic interaction", "正の遺伝的相互作用": "positive genetic interaction",
            "表現型の抑圧": "phenotypic suppression", "合成増殖不良": "synthetic growth defect"}


def description_line_en(line: str) -> str:
    """カテゴリの説明の 1 行（パラログの説明など）を英語にする。"""
    if not has_japanese(line):
        return line
    m = re.fullmatch(r"パラログ（(.+)）", line)
    if m:
        return f"Paralog ({m.group(1)})"
    m = re.fullmatch(r"GO（生物学的過程・分子機能）の重なり: (.+)", line)
    if m:
        return f"GO overlap (biological process, molecular function): {m.group(1)}"
    m = re.fullmatch(r"両方を壊すと強く悪くなる（BioGRID の遺伝的相互作用）: (.+?)。PMID: (.+)", line)
    if m:
        kinds = []
        for part in m.group(1).split("・"):
            name, _, n = part.rpartition(" ")
            kinds.append(f"{_GENETIC.get(name, name)} {n}" if name else _GENETIC.get(part, part))
        return f"Double deletion is much worse (BioGRID genetic interactions): {', '.join(kinds)}. PMID: {m.group(2)}"
    return _text_catalog().get(line) or _words(line)


def category_description_en(text: str) -> str:
    """カテゴリの説明（categories.description。行ごと）を英語にする。"""
    if not text or not has_japanese(text):
        return text or ""
    return "\n".join(description_line_en(line) for line in text.split("\n"))
