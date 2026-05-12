"""
analytics.py
------------
All Plotly chart builders used across the dashboard.
Every function returns a plotly Figure object; the caller renders it
with st.plotly_chart(fig, use_container_width=True).
"""

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ── Shared theme ───────────────────────────────────────────────────────────────
DARK_BG    = "#0a0f1e"
CARD_BG    = "#0d1b2a"
GRID_COLOR = "#1a2a3a"
TEXT_COLOR = "#e0e6f0"
ACCENT1    = "#00d4ff"
ACCENT2    = "#7b2fff"
ACCENT3    = "#ff6b6b"
PALETTE    = [ACCENT1, ACCENT2, ACCENT3, "#f39c12", "#2ecc71",
              "#e67e22", "#9b59b6", "#1abc9c", "#e74c3c", "#3498db"]

_layout_defaults = dict(
    paper_bgcolor=DARK_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color=TEXT_COLOR, family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=50, b=20),
)


def _apply_defaults(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=ACCENT1)),
        **_layout_defaults,
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig


# ── 1. Top-3 horizontal confidence bar chart ───────────────────────────────────
def top3_confidence_bar(predictions: list) -> go.Figure:
    """Horizontal bar chart showing top-3 disease confidence percentages."""
    diseases  = [p["disease"].title()   for p in predictions]
    confs     = [p["confidence"]        for p in predictions]
    colors    = [p["risk_color"]        for p in predictions]

    fig = go.Figure(go.Bar(
        x=confs[::-1], y=diseases[::-1],
        orientation="h",
        marker=dict(color=colors[::-1], line=dict(width=0)),
        text=[f"<b>{c:.1f}%</b>" for c in confs[::-1]],
        textposition="outside",
        textfont=dict(size=14, color=TEXT_COLOR),
    ))
    fig.update_xaxes(range=[0, 115], ticksuffix="%")
    return _apply_defaults(fig, "Top 3 Predicted Diseases — Confidence Scores")


# ── 2. Confidence gauge for the #1 prediction ────────────────────────────────
def confidence_gauge(confidence: float, disease: str) -> go.Figure:
    """Semicircular gauge showing the top prediction's confidence."""
    color = "#2ecc71" if confidence >= 70 else "#f39c12" if confidence >= 40 else "#e74c3c"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=confidence,
        number=dict(suffix="%", font=dict(size=36, color=TEXT_COLOR)),
        title=dict(text=f"<b>{disease[:30]}</b>", font=dict(size=13, color=ACCENT1)),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor=GRID_COLOR,
                      tickfont=dict(color=TEXT_COLOR)),
            bar=dict(color=color, thickness=0.25),
            bgcolor=CARD_BG,
            borderwidth=0,
            steps=[
                dict(range=[0,  40], color="#1a0a0a"),
                dict(range=[40, 70], color="#1a1200"),
                dict(range=[70,100], color="#0a1a0a"),
            ],
            threshold=dict(line=dict(color=ACCENT1, width=3), thickness=0.75, value=confidence),
        ),
    ))
    fig.update_layout(paper_bgcolor=DARK_BG, font=dict(color=TEXT_COLOR),
                      margin=dict(l=20, r=20, t=60, b=20), height=280)
    return fig


# ── 3. Probability pie chart ──────────────────────────────────────────────────
def top3_pie(predictions: list) -> go.Figure:
    """Pie chart of top-3 disease probabilities."""
    labels = [p["disease"].title() for p in predictions]
    values = [p["confidence"]      for p in predictions]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.5,
        marker=dict(colors=PALETTE[:3], line=dict(color=DARK_BG, width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color=TEXT_COLOR),
    ))
    return _apply_defaults(fig, "Probability Distribution")


# ── 4. Category accuracy bar chart ───────────────────────────────────────────
def category_accuracy_chart(summary: dict) -> go.Figure:
    cat_res = summary.get("category_results", {})
    cats    = sorted(cat_res, key=lambda c: cat_res[c]["accuracy"], reverse=True)
    accs    = [cat_res[c]["accuracy"] * 100 for c in cats]

    fig = go.Figure(go.Bar(
        x=accs, y=cats, orientation="h",
        marker=dict(
            color=accs,
            colorscale=[[0, ACCENT2], [0.5, ACCENT1], [1, "#2ecc71"]],
            showscale=False,
            line=dict(width=0),
        ),
        text=[f"{a:.1f}%" for a in accs],
        textposition="outside",
        textfont=dict(size=10, color=TEXT_COLOR),
    ))
    fig.update_xaxes(range=[0, 115], ticksuffix="%")
    return _apply_defaults(fig, "Per-Category Model Accuracy (CatBoost)")


# ── 5. Symptom frequency bar chart ───────────────────────────────────────────
def symptom_frequency_chart(df: pd.DataFrame, symptom_cols: list,
                             category: str = None, n: int = 20) -> go.Figure:
    """Top-N symptom frequencies, optionally filtered to one category."""
    subset = df[df["Category"] == category] if category else df
    freq   = subset[symptom_cols].sum().sort_values(ascending=False).head(n)

    fig = go.Figure(go.Bar(
        x=list(freq.index), y=list(freq.values),
        marker=dict(color=ACCENT1, opacity=0.85, line=dict(width=0)),
    ))
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=9))
    title = f"Top {n} Symptoms" + (f" — {category}" if category else " (All Categories)")
    return _apply_defaults(fig, title)


# ── 6. Category distribution donut ───────────────────────────────────────────
def category_distribution_donut(df: pd.DataFrame) -> go.Figure:
    counts = df["Category"].value_counts()
    fig = go.Figure(go.Pie(
        labels=counts.index.tolist(), values=counts.values.tolist(),
        hole=0.55,
        marker=dict(colors=PALETTE, line=dict(color=DARK_BG, width=2)),
        textinfo="label+percent",
        textfont=dict(size=10, color=TEXT_COLOR),
    ))
    return _apply_defaults(fig, "Disease Category Distribution")


# ── 7. Model comparison bar ───────────────────────────────────────────────────
def model_comparison_chart(summary: dict) -> go.Figure:
    comp = summary.get("comparison_results", [])
    if not comp:
        return go.Figure()
    models  = [r["Model"]    for r in comp]
    metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    colors  = [ACCENT1, ACCENT2, ACCENT3, "#f39c12"]

    fig = go.Figure()
    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Bar(
            name=metric,
            x=models,
            y=[r[metric] for r in comp],
            marker=dict(color=color, opacity=0.85),
        ))
    fig.update_layout(barmode="group",
                      legend=dict(bgcolor=DARK_BG, bordercolor=GRID_COLOR))
    return _apply_defaults(fig, "Model Algorithm Comparison (Benchmark Category)")


# ── 8. Symptom heatmap ────────────────────────────────────────────────────────
def symptom_heatmap(df: pd.DataFrame, symptom_cols: list,
                    category: str, top_n: int = 15) -> go.Figure:
    """
    Heatmap: diseases (rows) x top symptoms (columns).
    Values = average symptom presence per disease.
    """
    cat_df  = df[df["Category"] == category]
    top_sym = cat_df[symptom_cols].sum().sort_values(ascending=False).head(top_n).index.tolist()
    grp     = cat_df.groupby("diseases")[top_sym].mean().round(2)

    fig = go.Figure(go.Heatmap(
        z=grp.values, x=top_sym, y=grp.index.tolist(),
        colorscale=[[0, DARK_BG], [0.5, ACCENT2], [1, ACCENT1]],
        hoverongaps=False,
        colorbar=dict(tickfont=dict(color=TEXT_COLOR)),
    ))
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
    fig.update_yaxes(tickfont=dict(size=8))
    return _apply_defaults(fig, f"Symptom–Disease Heatmap — {category}")


# ── 9. Medicine usage bar ─────────────────────────────────────────────────────
def medicine_usage_chart(lookup_dict: dict, top_n: int = 15) -> go.Figure:
    """Bar chart of the most frequently prescribed medicines across all diseases."""
    from collections import Counter
    counter = Counter()
    for info in lookup_dict.values():
        for key in ["medicine_1", "medicine_2", "medicine_3"]:
            val = info.get(key, "Un Known").strip()
            if val and val != "Un Known":
                counter[val] += 1

    most_common = counter.most_common(top_n)
    meds, counts = zip(*most_common) if most_common else ([], [])

    fig = go.Figure(go.Bar(
        x=list(counts)[::-1], y=list(meds)[::-1],
        orientation="h",
        marker=dict(color=ACCENT2, opacity=0.85, line=dict(width=0)),
    ))
    return _apply_defaults(fig, f"Top {top_n} Most Prescribed Medicines")


# ── 10. KPI summary cards (returned as dict for st.metric) ───────────────────
def side_effects_frequency_chart(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Horizontal bar of most frequent side-effect terms in the dataset."""
    from collections import Counter

    ctr: Counter = Counter()
    if "side_effects" in df.columns:
        for raw in df["side_effects"].fillna("").astype(str):
            if not raw.strip() or raw.strip().lower() == "un known":
                continue
            for term in raw.replace(";", ",").split(","):
                t = term.strip().lower()
                if t:
                    ctr[t] += 1
    most = ctr.most_common(top_n)
    if not most:
        fig = go.Figure()
        return _apply_defaults(fig, "Side Effect Terms (no data)")
    terms, counts = zip(*most)
    fig = go.Figure(go.Bar(
        x=list(counts)[::-1], y=list(terms)[::-1],
        orientation="h",
        marker=dict(color=ACCENT3, opacity=0.88, line=dict(width=0)),
    ))
    return _apply_defaults(fig, f"Top {top_n} Side Effect Terms")


def disease_distribution_chart(df: pd.DataFrame, top_n: int = 25) -> go.Figure:
    """Most frequent diseases across the full dataset."""
    if "diseases" not in df.columns:
        return go.Figure()
    vc = df["diseases"].value_counts().head(top_n)
    fig = go.Figure(go.Bar(
        x=vc.values[::-1], y=[str(x) for x in vc.index][::-1],
        orientation="h",
        marker=dict(color=ACCENT1, opacity=0.85, line=dict(width=0)),
    ))
    return _apply_defaults(fig, f"Top {top_n} Diseases by Record Count")


def medication_frequency_from_df(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Prescription frequency using medicine_1..3 columns in the dataset."""
    meds = []
    for c in ("medicine_1", "medicine_2", "medicine_3"):
        if c in df.columns:
            s = df[c].fillna("").astype(str).str.strip()
            meds.append(s[(s != "") & (s.str.lower() != "un known")])
    if not meds:
        return go.Figure()
    all_m = pd.concat(meds, ignore_index=True)
    vc = all_m.value_counts().head(top_n)
    fig = go.Figure(go.Bar(
        x=vc.values[::-1], y=[str(x) for x in vc.index][::-1],
        orientation="h",
        marker=dict(color=ACCENT2, opacity=0.85, line=dict(width=0)),
    ))
    return _apply_defaults(fig, f"Top {top_n} Medications (dataset frequency)")


def category_record_ranking(df: pd.DataFrame) -> go.Figure:
    """Bar chart: records per category."""
    if "Category" not in df.columns:
        return go.Figure()
    vc = df["Category"].value_counts().sort_values(ascending=True)
    fig = go.Figure(go.Bar(
        x=vc.values, y=[str(x) for x in vc.index],
        orientation="h",
        marker=dict(
            color=vc.values,
            colorscale=[[0, ACCENT2], [0.5, ACCENT1], [1, "#2ecc71"]],
            showscale=False,
            line=dict(width=0),
        ),
    ))
    return _apply_defaults(fig, "Records per Category")


def prediction_accuracy_tab_chart(summary: dict) -> go.Figure:
    """Accuracy vs F1 scatter per category — risk / reliability view."""
    cat_res = summary.get("category_results", {}) or {}
    if not cat_res:
        return go.Figure()
    cats = list(cat_res.keys())
    acc = [cat_res[c]["accuracy"] * 100 for c in cats]
    f1v = [cat_res[c]["f1"] * 100 for c in cats]
    sizes = [max(12, cat_res[c].get("diseases", 3) * 2) for c in cats]
    fig = go.Figure(go.Scatter(
        x=acc, y=f1v, mode="markers+text",
        text=cats, textposition="top center",
        textfont=dict(size=8, color=TEXT_COLOR),
        marker=dict(size=sizes, color=acc, colorscale=[[0, ACCENT3], [0.5, ACCENT2], [1, ACCENT1]],
                    showscale=True, colorbar=dict(title="Acc %", tickfont=dict(color=TEXT_COLOR))),
    ))
    fig.update_xaxes(title="Accuracy %", range=[0, 105])
    fig.update_yaxes(title="F1 %", range=[0, 105])
    return _apply_defaults(fig, "Category Reliability — Accuracy vs F1")


def symptom_cooccurrence_top_pair(df: pd.DataFrame, symptom_cols: list, category: str | None,
                                  top_symptoms_n: int = 12) -> go.Figure:
    """
    Simple symptom association view: correlation among top symptoms (Pearson).
    """
    subset = df[df["Category"] == category] if category else df
    if subset.empty or not symptom_cols:
        return go.Figure()
    use_cols = list(subset[symptom_cols].sum().sort_values(ascending=False).head(top_symptoms_n).index)
    sub = subset[use_cols].astype(float)
    cm = sub.corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=cm.values, x=use_cols, y=use_cols,
        colorscale=[[0, DARK_BG], [0.5, ACCENT2], [1, ACCENT1]],
        zmin=-1, zmax=1,
        colorbar=dict(tickfont=dict(color=TEXT_COLOR)),
    ))
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
    fig.update_yaxes(tickfont=dict(size=8))
    title = f"Symptom Correlation — {category}" if category else "Symptom Correlation — All Data"
    return _apply_defaults(fig, title)


def risk_tier_category_chart(summary: dict) -> go.Figure:
    """Count categories by accuracy tier (model risk bands)."""
    cat_res = summary.get("category_results", {}) or {}
    low = med = high = 0
    for c in cat_res:
        a = cat_res[c]["accuracy"] * 100
        if a < 75:
            low += 1
        elif a < 90:
            med += 1
        else:
            high += 1
    labels = ["High reliability (≥90%)", "Moderate (75–89%)", "Elevated uncertainty (<75%)"]
    values = [high, med, low]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=[ACCENT1, ACCENT3, "#e74c3c"], line=dict(width=0)),
    ))
    return _apply_defaults(fig, "Model Risk Tiers (categories per band)")


def compute_kpi(summary: dict, lookup_dict: dict) -> dict:
    cat_res   = summary.get("category_results", {})
    avg_acc   = summary.get("avg_accuracy", 0)
    n_disease = summary.get("n_diseases", 0)
    n_cat     = summary.get("n_categories", 0)
    n_feat    = summary.get("n_features", 0)

    best_cat  = max(cat_res, key=lambda c: cat_res[c]["accuracy"]) if cat_res else "N/A"
    best_acc  = cat_res[best_cat]["accuracy"] * 100 if cat_res else 0

    unknown_meds = sum(
        1 for info in lookup_dict.values()
        for k in ["medicine_1","medicine_2","medicine_3"]
        if info.get(k,"").strip() == "Un Known"
    )
    known_pct = round(100 - unknown_meds / max(len(lookup_dict)*3, 1) * 100, 1)

    return {
        "avg_accuracy":  f"{avg_acc*100:.1f}%",
        "n_diseases":    n_disease,
        "n_categories":  n_cat,
        "n_features":    n_feat,
        "best_category": best_cat,
        "best_acc":      f"{best_acc:.1f}%",
        "known_meds_pct":f"{known_pct:.1f}%",
    }
