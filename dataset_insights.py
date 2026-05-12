"""
dataset_insights.py
-------------------
Dataset-level KPIs and narrative insights for the Streamlit platform.
Reads the merged CSV shape and columns; no model retraining.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd


def _med_series_all(df: pd.DataFrame) -> pd.Series:
    parts = []
    for c in ("medicine_1", "medicine_2", "medicine_3"):
        if c in df.columns:
            parts.append(df[c].fillna("").astype(str).str.strip())
    if not parts:
        return pd.Series(dtype=str)
    out = pd.concat(parts, ignore_index=True)
    return out[(out != "") & (out.str.lower() != "un known")]


def _side_effect_terms(df: pd.DataFrame) -> Counter:
    ctr: Counter = Counter()
    if "side_effects" not in df.columns:
        return ctr
    for raw in df["side_effects"].fillna("").astype(str):
        if not raw.strip() or raw.strip().lower() == "un known":
            continue
        for term in raw.replace(";", ",").split(","):
            t = term.strip().lower()
            if t:
                ctr[t] += 1
    return ctr


def compute_dataset_kpis(df: pd.DataFrame, summary: dict) -> dict[str, Any]:
    """Executive KPIs derived from the merged dataset and model summary."""
    n_diseases = int(df["diseases"].nunique()) if "diseases" in df.columns else 0
    n_cats = int(df["Category"].nunique()) if "Category" in df.columns else 0

    meds = _med_series_all(df)
    n_unique_meds = int(meds.nunique()) if len(meds) else 0

    se_ctr = _side_effect_terms(df)
    n_unique_se = len(se_ctr)

    cat_counts = df["Category"].value_counts() if "Category" in df.columns else pd.Series()
    disease_counts = df["diseases"].value_counts() if "diseases" in df.columns else pd.Series()

    most_common_cat = str(cat_counts.idxmax()) if len(cat_counts) else "—"
    most_common_disease = str(disease_counts.idxmax()) if len(disease_counts) else "—"

    top_med = "—"
    if len(meds):
        top_med = str(meds.value_counts().index[0])

    top_se = "—"
    if se_ctr:
        top_se = max(se_ctr, key=se_ctr.get)

    avg_acc = float(summary.get("avg_accuracy", 0.0)) * 100

    cat_res = summary.get("category_results", {}) or {}
    most_predictable = "—"
    if cat_res:
        most_predictable = max(cat_res, key=lambda c: cat_res[c].get("accuracy", 0))

    return {
        "n_diseases": n_diseases,
        "n_categories": n_cats,
        "n_medicines_distinct": n_unique_meds,
        "n_side_effect_terms": n_unique_se,
        "most_common_category_rows": most_common_cat,
        "most_common_disease": most_common_disease,
        "most_common_medication": top_med,
        "most_frequent_side_effect_term": top_se,
        "catboost_avg_accuracy_pct": round(avg_acc, 2),
        "most_predictable_category": most_predictable,
        "category_value_counts": cat_counts,
        "disease_value_counts": disease_counts,
    }


def top_categories_by_volume(df: pd.DataFrame, n: int = 10) -> list[str]:
    """Categories with the most dataset rows (for diagnosis card ordering)."""
    if "Category" not in df.columns:
        return []
    vc = df["Category"].value_counts()
    return [str(x) for x in vc.head(n).index.tolist()]


def remaining_categories(all_categories: list[str], top10: list[str]) -> list[str]:
    rest = [c for c in all_categories if c not in top10]
    return sorted(rest, key=str.lower)


def most_recurring_medication(df: pd.DataFrame) -> tuple[str, int]:
    meds = _med_series_all(df)
    if len(meds) == 0:
        return "—", 0
    vc = meds.value_counts()
    return str(vc.index[0]), int(vc.iloc[0])
