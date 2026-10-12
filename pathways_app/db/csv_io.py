"""CSV 一括インポート（DB を作る道具で使う）。読み込みは UTF-8 と Shift_JIS を受け付ける。
アプリからの CSV の書き出しは、2026-10-12 に外した（データを配り直す形にしないため）。

pandas は読み込みでだけ使う（配布するアプリに pandas・numpy を入れずに済むように。PathwaysViewer.spec で外している）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from .database import Database
from .models import Interaction, Protein
from .vocab import DETAILS, EFFECT_ALIASES, guess_threshold

if TYPE_CHECKING:
    import pandas as pd

PROTEIN_COLUMNS = ["gene_name", "standard_name", "complex_category", "protein_properties",
                   "description", "basal_activity"]
INTERACTION_COLUMNS = ["source_protein", "target_protein", "interaction_type", "effect", "threshold",
                       "weight", "signal_threshold_rule", "evidence"]
# 列名のゆらぎを吸収する
COLUMN_ALIASES = {
    "gene": "gene_name", "name": "gene_name", "遺伝子名": "gene_name",
    "systematic_name": "standard_name", "orf": "standard_name",
    "category": "complex_category", "group": "complex_category",
    "properties": "protein_properties",
    "source": "source_protein", "source_gene": "source_protein", "上流": "source_protein",
    "target": "target_protein", "target_gene": "target_protein", "下流": "target_protein",
    "type": "interaction_type",
    "rule": "signal_threshold_rule",
}


@dataclass
class ImportReport:
    added: int = 0
    updated: int = 0
    created_proteins: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"追加: {self.added} 件 / 更新: {self.updated} 件"]
        if self.created_proteins:
            lines.append(f"未登録だったため自動作成した遺伝子 ({len(self.created_proteins)}): "
                         + ", ".join(self.created_proteins))
        if self.errors:
            lines.append(f"スキップした行 ({len(self.errors)}):")
            lines += ["  " + e for e in self.errors[:30]]
            if len(self.errors) > 30:
                lines.append(f"  … ほか {len(self.errors) - 30} 件")
        return "\n".join(lines)


def read_csv(path: str) -> pd.DataFrame:
    import pandas as pd   # 取り込みの道具でだけ使う（アプリには入れない）
    last_error = None
    for encoding in ("utf-8-sig", "cp932"):
        try:
            df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding=encoding)
            break
        except UnicodeDecodeError as e:
            last_error = e
    else:
        raise last_error
    df.columns = [COLUMN_ALIASES.get(c.strip().lower(), c.strip().lower()) for c in df.columns]
    return df.apply(lambda col: col.str.strip())


def detect_kind(df: pd.DataFrame) -> str | None:
    if {"source_protein", "target_protein"} <= set(df.columns):
        return "interactions"
    if "gene_name" in df.columns:
        return "proteins"
    return None


def _float_or_none(text: str, lo=0.0, hi=1.0):
    if text == "":
        return None
    value = float(text)
    if not lo <= value <= hi:
        raise ValueError(f"{value} は {lo}〜{hi} の範囲外です")
    return value


def import_proteins(db: Database, df: pd.DataFrame, replace: bool) -> ImportReport:
    report = ImportReport()
    with db.session() as s, s.begin():
        if replace:
            s.execute(delete(Interaction))
            s.execute(delete(Protein))
        by_name = {p.gene_name.upper(): p for p in s.scalars(select(Protein))}
        for i, row in df.iterrows():
            gene = row.get("gene_name", "")
            if not gene:
                report.errors.append(f"{i + 2} 行目: gene_name が空です")
                continue
            try:
                basal = _float_or_none(row.get("basal_activity", ""))
            except ValueError as e:
                report.errors.append(f"{i + 2} 行目 ({gene}): basal_activity {e}")
                continue
            p = by_name.get(gene.upper())
            if p is None:
                p = Protein(gene_name=gene)
                s.add(p)
                by_name[gene.upper()] = p
                report.added += 1
            else:
                report.updated += 1
            for col in ("standard_name", "complex_category", "protein_properties", "description"):
                if col in df.columns:
                    setattr(p, col, row[col])
            if "basal_activity" in df.columns:
                p.basal_activity = basal
        db.ensure_categories(s, [p.complex_category for p in by_name.values()])
    return report


def import_interactions(db: Database, df: pd.DataFrame, replace: bool) -> ImportReport:
    report = ImportReport()
    with db.session() as s, s.begin():
        if replace:
            s.execute(delete(Interaction))
        lookup = {}
        for p in s.scalars(select(Protein)):
            lookup[p.gene_name.upper()] = p
            if p.standard_name:
                lookup.setdefault(p.standard_name.upper(), p)
        existing = {(it.source_id, it.target_id, it.interaction_type): it
                    for it in s.scalars(select(Interaction)).unique()}

        def protein_for(name: str) -> Protein:
            p = lookup.get(name.upper())
            if p is None:
                p = Protein(gene_name=name, complex_category="未分類")
                s.add(p)
                s.flush()
                lookup[name.upper()] = p
                report.created_proteins.append(name)
            return p

        for i, row in df.iterrows():
            src, tgt = row.get("source_protein", ""), row.get("target_protein", "")
            if not src or not tgt:
                report.errors.append(f"{i + 2} 行目: 上流または下流の遺伝子名が空です")
                continue
            itype = (row.get("interaction_type", "") or "activation").lower()
            rule = row.get("signal_threshold_rule", "")
            try:
                threshold = _float_or_none(row.get("threshold", ""))
                weight = _float_or_none(row.get("weight", ""))
            except ValueError as e:
                report.errors.append(f"{i + 2} 行目 ({src}→{tgt}): {e}")
                continue
            effect_text = row.get("effect", "")
            effect = EFFECT_ALIASES.get(effect_text.lower()) if effect_text else None
            if effect_text and effect is None:
                report.errors.append(f"{i + 2} 行目 ({src}→{tgt}): effect '{effect_text}' を解釈できません")
                continue
            source, target = protein_for(src), protein_for(tgt)
            key = (source.id, target.id, itype)
            it = existing.get(key)
            if it is None:
                it = Interaction(source_id=source.id, target_id=target.id, interaction_type=itype)
                s.add(it)
                existing[key] = it
                report.added += 1
            else:
                report.updated += 1
            it.effect = effect
            it.threshold = threshold if threshold is not None else guess_threshold(rule)
            it.weight = weight if weight is not None else 1.0
            it.signal_threshold_rule = rule
            it.evidence = row.get("evidence", "")
            for name in ["conditions"] + [n for n, _ in DETAILS]:   # 列があれば使う（なければ今の値のまま）
                if name in row:
                    setattr(it, name, row.get(name, "") or "")
        db.ensure_categories(s, ["未分類"] if report.created_proteins else [])
    return report
