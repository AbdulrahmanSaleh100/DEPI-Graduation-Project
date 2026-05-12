"""
app.py
------
MedAI — Professional medical diagnosis dashboard (Streamlit-native UI).
Inference: per-category CatBoost + LabelEncoder (see model_artifacts/).
Theme: .streamlit/config.toml — no external CSS file.
"""

from __future__ import annotations

import datetime
import os

import pandas as pd
import streamlit as st

from analytics import (
    category_accuracy_chart,
    category_distribution_donut,
    category_record_ranking,
    compute_kpi,
    disease_distribution_chart,
    medication_frequency_from_df,
    medicine_usage_chart,
    model_comparison_chart,
    prediction_accuracy_tab_chart,
    risk_tier_category_chart,
    side_effects_frequency_chart,
    symptom_cooccurrence_top_pair,
    symptom_frequency_chart,
)
from dashboard_components import (
    diagnosis_page_intro,
    inject_ui_styles,
    info_banner,
    page_hero,
    render_active_chapter_status_card,
    render_category_accuracy_cards,
    render_category_buttons_top10,
    render_diagnosis_progress_rail,
    render_diagnosis_step_header,
    render_prediction_results_block,
    render_summary_cards,
    section_header,
    sidebar_brand,
)
from dataset_insights import (
    compute_dataset_kpis,
    top_categories_by_volume,
)
from model_loader import ARTIFACTS_DIR, MODELS_DIR, load_all_artifacts
from prediction_engine import get_top_symptoms_for_category, predict_top3

# ── Page ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedAI — Medical Diagnosis",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

artifacts = load_all_artifacts()
sym_cols = artifacts["symptom_cols"]
lookup_dict = artifacts["lookup_dict"]
cat_top_syms = artifacts["category_top_symptoms"]
summary = artifacts["summary"]
cat_res = summary.get("category_results", {}) or {}

DATA_PATH = os.path.join(os.path.dirname(__file__), "min_final_merged_dataset.csv")


@st.cache_data(show_spinner=False)
def load_dataset():
    df = pd.read_csv(DATA_PATH)
    for c in ("medicine_1", "medicine_2", "medicine_3", "side_effects"):
        if c in df.columns:
            df[c] = df[c].fillna("Un Known").astype(str).str.strip()
    for c in ("diseases", "Category"):
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    drop_c = [c for c in ("ICD-10 Code", "Arabic Name") if c in df.columns]
    if drop_c:
        df.drop(columns=drop_c, inplace=True)
    return df


df = load_dataset()
ds_kpi = compute_dataset_kpis(df, summary)
kpi = compute_kpi(summary, lookup_dict)

all_categories_sorted = sorted(cat_res.keys(), key=str.lower)
vol_top10 = top_categories_by_volume(df, 15)
top10_diag = [c for c in vol_top10 if c in cat_res][:10]


def _artifact_last_updated() -> str | None:
    try:
        cand = []
        if os.path.isdir(MODELS_DIR):
            for fn in os.listdir(MODELS_DIR):
                if fn.endswith("_model.pkl"):
                    cand.append(os.path.getmtime(os.path.join(MODELS_DIR, fn)))
        meta = os.path.join(ARTIFACTS_DIR, "summary.json")
        if os.path.isfile(meta):
            cand.append(os.path.getmtime(meta))
        if not cand:
            return None
        return datetime.datetime.fromtimestamp(max(cand)).strftime("%Y-%m-%d %H:%M")
    except OSError:
        return None


def _symptom_snippet(row: pd.Series, cols: list[str], k: int = 4) -> str:
    on = [s for s in cols if int(row.get(s, 0) or 0) == 1]
    if not on:
        return "—"
    head, more = on[:k], len(on) - k
    txt = ", ".join(x.title() for x in head)
    if more > 0:
        txt += f" (+{more} more)"
    return txt


def _medicines_join(row: pd.Series) -> str:
    parts = []
    for c in ("medicine_1", "medicine_2", "medicine_3"):
        if c not in row.index:
            continue
        v = str(row[c]).strip()
        if v and v.lower() != "un known":
            parts.append(v)
    return "; ".join(parts) if parts else "—"


def _init_session():
    defaults = {
        "active_page": "Home",
        "selected_category": None,
        "prediction_results": None,
        "prediction_history": [],
        "diag_sym_multiselect": [],
        "diag_cat_sb": "— Select —",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_session()

inject_ui_styles()

# Session resets must run before any widget binds to these keys (Streamlit rule).
if st.session_state.pop("_pending_session_reset", False):
    st.session_state.pop("diag_sym_multiselect", None)
    st.session_state["selected_category"] = None
    st.session_state["prediction_results"] = None
    st.session_state["prediction_history"] = []
    st.session_state["diag_cat_sb"] = "— Select —"

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    sidebar_brand()

    st.sidebar.markdown("##### Navigate")
    pages = [
        "Home",
        "Diagnosis Prediction",
        "Analytics Dashboard",
        "About Model",
    ]
    for p in pages:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state["active_page"] = p

    st.divider()
    st.markdown("##### About this project")
    st.caption(
        "AI-assisted differential diagnosis from symptoms. "
        "Uses your merged medical dataset and trained gradient-boosted classifiers (CatBoost) per disease category."
    )

    st.markdown("##### Model snapshot")
    st.metric("Mean hold-out accuracy", kpi["avg_accuracy"])
    st.metric("Disease classes", f"{kpi['n_diseases']}")
    st.metric("Symptom features", f"{kpi['n_features']}")

    st.markdown("##### Dataset snapshot")
    st.metric("Total rows", f"{len(df):,}")
    st.metric("Categories", f"{ds_kpi['n_categories']}")

    st.markdown("##### Quick insight")
    st.success(f"Most common category by volume: **{ds_kpi['most_common_category_rows']}**")

    st.divider()
    st.markdown("##### Appearance")
    st.caption("Theme is controlled by **.streamlit/config.toml** (dark blue). Adjust colors there — no CSS file.")

    if st.button("Reset session", use_container_width=True):
        st.session_state["_pending_session_reset"] = True
        st.rerun()

    st.caption("Not medical advice. For research and education.")

page = st.session_state.get("active_page", "Home")
if page == "Insights":
    st.session_state["active_page"] = "Analytics Dashboard"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":
    page_hero(
        "Clinical intelligence hub",
        "Explore the corpus, model quality, and launch AI-guided differentials. "
        "Built with Streamlit, Plotly, and your CatBoost inference pipeline.",
    )

    render_summary_cards(
        [
            {
                "title": "Diseases",
                "value": f"{ds_kpi['n_diseases']}",
                "hint": "Unique disease labels in corpus",
                "accent": "#38bdf8",
            },
            {
                "title": "Categories",
                "value": f"{ds_kpi['n_categories']}",
                "hint": "Clinical chapters modeled",
                "accent": "#a78bfa",
            },
            {
                "title": "Medicines",
                "value": f"{ds_kpi['n_medicines_distinct']}",
                "hint": "Distinct Rx strings observed",
                "accent": "#22d3ee",
            },
            {
                "title": "Mean accuracy",
                "value": kpi["avg_accuracy"],
                "hint": "Average across 15 CatBoost models",
                "accent": "#34d399",
            },
            {
                "title": "Features",
                "value": f"{kpi['n_features']}",
                "hint": "Binary symptom dimensions",
                "accent": "#fbbf24",
            },
        ]
    )

    st.divider()
    render_category_accuracy_cards(cat_res)

    st.divider()
    section_header("Population & model quality", "Record volume vs per-category CatBoost accuracy")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(category_record_ranking(df), use_container_width=True, key="h1")
    with c2:
        st.plotly_chart(category_accuracy_chart(summary), use_container_width=True, key="h2")

    with st.expander("Full category metrics table", expanded=False):
        rows = []
        for cat in sorted(cat_res, key=lambda c: cat_res[c]["accuracy"], reverse=True):
            r = cat_res[cat]
            rows.append(
                {
                    "Category": cat,
                    "Accuracy": f"{r['accuracy']*100:.1f}%",
                    "F1": f"{r['f1']*100:.1f}%",
                    "Diseases": r["diseases"],
                    "Rows": f"{r['rows']:,}",
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=320)

    st.divider()
    section_header("Dataset preview", "Filter and page through merged records")
    q = st.text_input("Search (category, disease, medicine, side effects)", key="hq")
    ps = st.slider("Rows per page", 8, 40, 12)
    base = df.copy()
    if q:
        qlow = q.lower()
        txt_cols = [c for c in ("Category", "diseases", "medicine_1", "medicine_2", "medicine_3", "side_effects") if c in base.columns]
        mask = base[txt_cols].apply(lambda s: s.astype(str).str.lower().str.contains(qlow, na=False)).any(axis=1)
        base = base[mask]
    total = len(base)
    npages = max(1, (total + ps - 1) // ps)
    pi = st.number_input("Page", 1, npages, 1)
    sl = (int(pi) - 1) * ps
    chunk = base.iloc[sl : sl + ps]
    prev = [
        {
            "Category": r.get("Category", "—"),
            "Disease": r.get("diseases", "—"),
            "Symptoms": _symptom_snippet(r, sym_cols),
            "Medicines": _medicines_join(r),
            "Side effects": str(r.get("side_effects", "—")),
        }
        for _, r in chunk.iterrows()
    ]
    st.caption(f"{len(chunk)} of {total:,} rows · page {pi}/{npages}")
    st.dataframe(pd.DataFrame(prev), use_container_width=True, height=380)

# ══════════════════════════════════════════════════════════════════════════════
# DIAGNOSIS PREDICTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Diagnosis Prediction":
    # Clear symptoms must happen before multiselect widget binds (same run).
    if st.session_state.pop("_clear_diagnosis_symptoms", False):
        st.session_state.pop("diag_sym_multiselect", None)
        st.session_state["prediction_results"] = None

    diagnosis_page_intro()

    _sel_rail = st.session_state.get("selected_category")
    _res_rail = st.session_state.get("prediction_results")
    _rail_step = 1
    if _sel_rail and _sel_rail in cat_top_syms and _res_rail:
        _rail_step = 3
    elif _sel_rail:
        _rail_step = 2
    render_diagnosis_progress_rail(_rail_step)

    _lc = "_last_diag_category"
    _prev, _curr = st.session_state.get(_lc), st.session_state.get("selected_category")
    if _prev is not None and _curr != _prev:
        st.session_state.pop("diag_sym_multiselect", None)
        st.session_state["prediction_results"] = None
    st.session_state[_lc] = _curr

    def _sync_category_from_select():
        v = st.session_state.get("diag_cat_sb", "— Select —")
        st.session_state["selected_category"] = None if v == "— Select —" else v

    main_col, status_col = st.columns([2.1, 1], gap="large")

    with main_col:
        render_diagnosis_step_header(
            1,
            "Select a clinical chapter",
            "Use quick picks from the top ten by volume, or search the full taxonomy below.",
            "pc1",
        )
        with st.container(border=True):
            st.caption("Quick picks")
            render_category_buttons_top10(top10_diag, st.session_state.get("selected_category"))
            st.selectbox(
                "All categories (searchable)",
                options=["— Select —"] + all_categories_sorted,
                key="diag_cat_sb",
                on_change=_sync_category_from_select,
            )
            _sync_category_from_select()

    with status_col:
        sel_preview = st.session_state.get("selected_category")
        acc_txt = "—"
        if sel_preview and sel_preview in cat_res:
            acc_txt = f"{cat_res[sel_preview]['accuracy']*100:.1f}%"
        render_active_chapter_status_card(
            str(sel_preview) if sel_preview else "None selected",
            acc_txt,
        )

    sel = st.session_state.get("selected_category")
    if sel and sel in cat_top_syms:
        top_syms = get_top_symptoms_for_category(sel, artifacts)

        render_diagnosis_step_header(
            2,
            f"Map presenting symptoms · {sel}",
            "Searchable multiselect builds the binary symptom vector for this chapter’s CatBoost model.",
            "pc2",
        )
        with st.container(border=True):
            info_banner(
                "Select every active finding. Unknown symptoms are ignored; only checked dimensions are set to 1."
            )

            chosen = st.multiselect(
                "Symptom library",
                options=top_syms,
                key="diag_sym_multiselect",
                placeholder="Type to filter…",
            )
            n_pick = len(st.session_state.get("diag_sym_multiselect") or [])
            st.markdown(
                f"""
<div class="medai-pred-card pc3" style="margin:8px 0 14px 0;">
  <div style="display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:12px 16px;border-radius:12px;
    background:linear-gradient(90deg,rgba(167,139,250,0.12),rgba(56,189,248,0.06));border:1px solid rgba(167,139,250,0.25);">
    <span style="font-size:1.6rem;">✦</span>
    <div>
      <div style="font-size:0.72rem;font-weight:800;letter-spacing:2px;color:#94a3b8;text-transform:uppercase;">Selection count</div>
      <div style="font-size:1.35rem;font-weight:800;color:#a78bfa;">{n_pick} <span style="font-size:0.85rem;font-weight:600;color:#94a3b8;">symptom(s)</span></div>
    </div>
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("Quick toggles (checkbox grid)", expanded=False):
                picked = []
                cols = st.columns(3)
                for i, s in enumerate(top_syms):
                    with cols[i % 3]:
                        lab = s[:46] + ("…" if len(s) > 46 else "")
                        if st.checkbox(lab, key=f"cb_{i}"):
                            picked.append(s)
                if picked:
                    st.caption("Checkboxes are complementary — merge with multiselect as needed.")
                    st.write(", ".join(picked))

            b1, b2 = st.columns([2, 1])
            with b1:
                run = st.button("Run AI differential", type="primary", use_container_width=True)
            with b2:
                if st.button("Clear symptoms", use_container_width=True, key="clr_sym_btn"):
                    st.session_state["_clear_diagnosis_symptoms"] = True
                    st.rerun()

        if run:
            if not chosen:
                st.warning("Select at least one symptom.")
            else:
                with st.spinner("Running CatBoost predict_proba…"):
                    results = predict_top3(sel, chosen, artifacts)
                    st.session_state["prediction_results"] = results
                    st.session_state["prediction_history"].append(
                        {
                            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                            "category": sel,
                            "symptoms": list(chosen),
                            "predictions": [
                                {
                                    "rank": p["rank"],
                                    "disease": p["disease"],
                                    "confidence": p["confidence"],
                                    "risk_level": p["risk_level"],
                                    "medicine_1": p["medicine_1"],
                                    "medicine_2": p["medicine_2"],
                                    "medicine_3": p["medicine_3"],
                                    "side_effects": p["side_effects"],
                                }
                                for p in results
                            ],
                        }
                    )

        res = st.session_state.get("prediction_results")
        if res:
            st.divider()
            render_diagnosis_step_header(
                3,
                "AI differential & clinical context",
                "Posterior probabilities, interactive charts, and per-disease therapy panels.",
                "pc4",
            )
            with st.container(border=True):
                render_prediction_results_block(res, sel)
                st.download_button(
                    "Download report (CSV)",
                    data=pd.DataFrame(res).to_csv(index=False).encode("utf-8"),
                    file_name=f"prediction_{sel.replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        st.divider()
        with st.expander("Session prediction history", expanded=False):
            st.caption("This browser session only.")
            hist = st.session_state.get("prediction_history", [])
            if hist:
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Time": h["timestamp"],
                                "Category": h["category"],
                                "Top disease": h["predictions"][0]["disease"] if h.get("predictions") else "—",
                                "Confidence": h["predictions"][0]["confidence"] if h.get("predictions") else None,
                            }
                            for h in reversed(hist[-25:])
                        ]
                    ),
                    use_container_width=True,
                    height=220,
                )
            else:
                st.caption("No runs yet.")
    elif not sel:
        st.markdown(
            """
<div class="medai-pred-card pc2" style="margin-top:8px;">
  <div style="border-radius:16px;padding:28px 24px;text-align:center;
    background:linear-gradient(165deg,rgba(17,24,39,0.95),rgba(15,23,42,0.98));
    border:1px dashed rgba(56,189,248,0.35);">
    <div style="font-size:2rem;margin-bottom:10px;">◇</div>
    <div style="font-size:1.1rem;font-weight:800;color:#e2e8f0;">Choose a chapter to begin</div>
    <div style="font-size:0.88rem;color:#94a3b8;margin-top:10px;max-width:420px;margin-left:auto;margin-right:auto;line-height:1.5;">
      Select a disease category from the cards or the searchable list — symptoms and AI ranking unlock in the next steps.
    </div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Category not available in models.")

# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Analytics Dashboard":
    page_hero("Analytics dashboard", "Interactive Plotly views over the dataset and model benchmarks.")

    t1, t2, t3, t4 = st.tabs(["Overview", "Therapy & safety", "Symptoms & heatmaps", "Model benchmarks"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(category_distribution_donut(df), use_container_width=True, key="a1")
        with c2:
            st.plotly_chart(disease_distribution_chart(df, top_n=24), use_container_width=True, key="a2")
        st.plotly_chart(category_record_ranking(df), use_container_width=True, key="a3")

    with t2:
        st.plotly_chart(medicine_usage_chart(lookup_dict, top_n=20), use_container_width=True, key="a4")
        st.plotly_chart(medication_frequency_from_df(df, top_n=20), use_container_width=True, key="a5")
        st.plotly_chart(side_effects_frequency_chart(df, top_n=22), use_container_width=True, key="a6")

    with t3:
        st.plotly_chart(symptom_frequency_chart(df, sym_cols, n=24), use_container_width=True, key="a7")
        cf = st.selectbox("Category filter", ["All"] + all_categories_sorted, key="acf")
        st.plotly_chart(
            symptom_frequency_chart(df, sym_cols, None if cf == "All" else cf, n=18),
            use_container_width=True,
            key="a8",
        )
        st.plotly_chart(
            symptom_cooccurrence_top_pair(df, sym_cols, None if cf == "All" else cf, top_symptoms_n=12),
            use_container_width=True,
            key="a9",
        )

    with t4:
        st.plotly_chart(prediction_accuracy_tab_chart(summary), use_container_width=True, key="a10")
        st.plotly_chart(category_accuracy_chart(summary), use_container_width=True, key="a11")
        st.plotly_chart(model_comparison_chart(summary), use_container_width=True, key="a12")
        st.plotly_chart(risk_tier_category_chart(summary), use_container_width=True, key="a13")

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT MODEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "About Model":
    page_hero("About the AI stack", "How data becomes a ranked differential — and how to run the app locally.")

    last_touch = _artifact_last_updated()
    st.markdown(
        f"**Artifacts last touched:** `{last_touch or 'unknown'}` · "
        f"**Dataset rows:** {len(df):,} · **Algorithm in production:** **CatBoost** (not Random Forest)."
    )

    st.markdown("##### Why CatBoost here")
    st.write(
        "Your trained artifacts are **15 separate CatBoost classifiers** (one per disease category), "
        "each with a **scikit-learn LabelEncoder** for disease names. "
        "A single global model across all 192 diseases would be far weaker because symptoms overlap across specialties; "
        "splitting by category matches the notebook design and yields high mean accuracy."
    )

    st.markdown("##### Feature engineering & inference")
    st.write(
        "- **Features:** 377 binary symptom columns (0/1) aligned with `symptom_cols.json`.\n"
        "- **Input:** For a chosen category, a vector of zeros except selected symptoms set to 1.\n"
        "- **Output:** `predict_proba` → top-3 disease indices → **inverse_transform** to labels.\n"
        "- **Therapy text:** `lookup_dict.json` maps disease → medicines & side-effect strings.\n"
        "- **Missing / unknown:** Lookup gaps show as “Ask Doctor” in the UI."
    )

    st.markdown("##### Preprocessing (dataset load)")
    st.code(
        "df = pd.read_csv('min_final_merged_dataset.csv')\n"
        "# Med/side-effect Na → 'Un Known'; strip category & disease strings",
        language="python",
    )

    comp = summary.get("comparison_results", [])
    if comp:
        st.markdown("##### Benchmark table (from training notebook)")
        st.dataframe(pd.DataFrame(comp), use_container_width=True, hide_index=True)

    st.markdown("##### Run locally")
    st.code("pip install -r requirements.txt\nstreamlit run app.py", language="bash")

    st.divider()
    st.caption("For Random Forest experiments, retrain separately; this dashboard loads the existing CatBoost bundle only.")
