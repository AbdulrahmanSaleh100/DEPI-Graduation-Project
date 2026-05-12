"""
dashboard_components.py
-----------------------
Streamlit-native UI helpers + lightweight injected animations (no external CSS file).
Works with .streamlit/config.toml theme.
"""

from __future__ import annotations

import html as html_lib

import streamlit as st

RISK_LABELS = {"High": "HIGH RISK", "Medium": "MEDIUM RISK", "Low": "LOW RISK"}


def inject_ui_styles():
    """Keyframes & utility classes for fade-in cards and diagnosis shell."""
    st.markdown(
        """
<style>
@keyframes medaiFadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes medaiGlow {
  0%, 100% { box-shadow: 0 0 18px rgba(56,189,248,0.12); }
  50% { box-shadow: 0 0 36px rgba(56,189,248,0.22); }
}
@keyframes medaiShimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.medai-summary-card {
  animation: medaiFadeUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  opacity: 0;
}
.medai-summary-card.d1 { animation-delay: 0.05s; }
.medai-summary-card.d2 { animation-delay: 0.12s; }
.medai-summary-card.d3 { animation-delay: 0.19s; }
.medai-summary-card.d4 { animation-delay: 0.26s; }
.medai-summary-card.d5 { animation-delay: 0.33s; }
.medai-acc-card {
  animation: medaiFadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  opacity: 0;
}
.medai-acc-card.a1 { animation-delay: 0.03s; }
.medai-acc-card.a2 { animation-delay: 0.06s; }
.medai-acc-card.a3 { animation-delay: 0.09s; }
.medai-acc-card.a4 { animation-delay: 0.12s; }
.medai-acc-card.a5 { animation-delay: 0.15s; }
.medai-diag-shell {
  animation: medaiFadeUp 0.45s ease-out forwards;
  border-radius: 18px;
  padding: 2px;
  background: linear-gradient(135deg, rgba(56,189,248,0.45), rgba(129,140,248,0.35), rgba(244,114,182,0.25));
  margin-bottom: 8px;
}
.medai-diag-inner {
  background: linear-gradient(180deg, #0f172a 0%, #0b1120 100%);
  border-radius: 16px;
  padding: 22px 24px;
  border: 1px solid rgba(51,65,85,0.6);
}
.medai-step-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  background: rgba(56,189,248,0.08);
  border: 1px solid rgba(56,189,248,0.25);
  color: #7dd3fc;
  margin-bottom: 12px;
}
@keyframes medaiCardIn {
  from { opacity: 0; transform: translateY(20px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes medaiBorderPulse {
  0%, 100% { border-color: rgba(56,189,248,0.35); box-shadow: 0 0 0 0 rgba(56,189,248,0.15); }
  50% { border-color: rgba(56,189,248,0.65); box-shadow: 0 0 24px rgba(56,189,248,0.12); }
}
@keyframes medaiShine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.medai-pred-card {
  animation: medaiCardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  opacity: 0;
}
.medai-pred-card.pc1 { animation-delay: 0.04s; }
.medai-pred-card.pc2 { animation-delay: 0.1s; }
.medai-pred-card.pc3 { animation-delay: 0.16s; }
.medai-pred-card.pc4 { animation-delay: 0.22s; }
.medai-pred-card.pc5 { animation-delay: 0.28s; }
.medai-pred-shell {
  position: relative;
  border-radius: 18px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(56,189,248,0.35), rgba(129,140,248,0.2), rgba(244,114,182,0.15));
  margin-bottom: 20px;
  overflow: hidden;
}
.medai-pred-shell-inner {
  border-radius: 17px;
  background: linear-gradient(165deg, #0f172a 0%, #0b1120 100%);
  border: 1px solid rgba(30,58,95,0.6);
  padding: 20px 22px 22px;
}
.medai-pred-shine {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(56,189,248,0.7), transparent);
  animation: medaiShine 3s ease-in-out infinite;
}
.medai-step-rail {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 0 0 22px 0;
}
.medai-step-rail-item {
  flex: 1 1 160px;
  border-radius: 14px;
  padding: 14px 16px;
  background: linear-gradient(160deg, rgba(17,24,39,0.95), rgba(15,23,42,0.98));
  border: 1px solid rgba(51,65,85,0.5);
  transition: transform 0.25s ease, border-color 0.25s ease;
  animation: medaiCardIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  opacity: 0;
}
.medai-step-rail-item.sd1 { animation-delay: 0.05s; }
.medai-step-rail-item.sd2 { animation-delay: 0.12s; }
.medai-step-rail-item.sd3 { animation-delay: 0.19s; }
.medai-step-rail-item.active {
  border-color: rgba(56,189,248,0.65);
  box-shadow: 0 0 28px rgba(56,189,248,0.14), inset 0 1px 0 rgba(56,189,248,0.08);
}
.medai-step-rail-item.done {
  border-color: rgba(52,211,153,0.45);
}
.medai-status-float {
  animation: medaiCardIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) 0.08s forwards;
  opacity: 0;
}
.medai-chart-wrap {
  border-radius: 14px;
  padding: 12px;
  background: linear-gradient(180deg, rgba(15,23,42,0.6), rgba(11,17,32,0.4));
  border: 1px solid rgba(30,58,95,0.45);
  margin-bottom: 8px;
  animation: medaiCardIn 0.55s ease-out forwards;
  opacity: 0;
}
.medai-chart-wrap.cw1 { animation-delay: 0.12s; }
.medai-chart-wrap.cw2 { animation-delay: 0.2s; }
.medai-chart-wrap.cw3 { animation-delay: 0.28s; }
.medai-disease-card-anim {
  animation: medaiCardIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  opacity: 0;
}
.medai-disease-card-anim.r1 { animation-delay: 0.08s; }
.medai-disease-card-anim.r2 { animation-delay: 0.16s; }
.medai-disease-card-anim.r3 { animation-delay: 0.24s; }
</style>
        """,
        unsafe_allow_html=True,
    )


def page_hero(title: str, subtitle: str):
    st.markdown(
        f'<div style="animation:medaiGlow 4s ease-in-out infinite;border-radius:14px;padding:18px 20px;margin-bottom:8px;'
        f'background:linear-gradient(135deg,rgba(56,189,248,0.08),rgba(129,140,248,0.06));border:1px solid rgba(56,189,248,0.2);">'
        f'<p style="font-size:2rem;font-weight:800;margin:0 0 4px 0;color:#38bdf8;">{html_lib.escape(title)}</p>'
        f'<p style="font-size:0.95rem;color:#94a3b8;margin:0;max-width:760px;">{html_lib.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def render_diagnosis_progress_rail(active_step: int):
    """
    Three animated step cards. active_step in {1,2,3}.
    Steps before active_step are marked done; current is active.
    """
    labels = [
        ("1", "Clinical chapter", "Pick specialty"),
        ("2", "Symptoms", "Map findings"),
        ("3", "AI ranking", "Top-3 diseases"),
    ]

    def item_class(n: int) -> str:
        base = f"medai-step-rail-item sd{n}"
        if n < active_step:
            return f"{base} done"
        if n == active_step:
            return f"{base} active"
        return base

    parts = []
    for n, (num, title, sub) in enumerate(labels, start=1):
        ic = item_class(n)
        parts.append(
            f"""
<div class="{ic}">
  <div style="font-size:0.62rem;font-weight:800;letter-spacing:2px;color:#64748b;">STEP {num}</div>
  <div style="font-size:0.95rem;font-weight:700;color:#e2e8f0;margin-top:6px;">{html_lib.escape(title)}</div>
  <div style="font-size:0.72rem;color:#94a3b8;margin-top:4px;">{html_lib.escape(sub)}</div>
</div>
            """
        )
    st.markdown(
        f'<div class="medai-step-rail">{"".join(parts)}</div>',
        unsafe_allow_html=True,
    )


def render_diagnosis_step_header(step_num: int, title: str, subtitle: str, delay_class: str = "pc1"):
    """Animated gradient header strip for each workflow block."""
    st.markdown(
        f"""
<div class="medai-pred-shell medai-pred-card {html_lib.escape(delay_class)}">
  <div class="medai-pred-shine"></div>
  <div class="medai-pred-shell-inner">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span style="display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:10px;
        background:linear-gradient(135deg,rgba(56,189,248,0.25),rgba(129,140,248,0.2));border:1px solid rgba(56,189,248,0.35);
        font-weight:800;font-size:0.9rem;color:#38bdf8;">{step_num}</span>
      <div>
        <div style="font-size:1.12rem;font-weight:800;color:#f8fafc;letter-spacing:-0.02em;">{html_lib.escape(title)}</div>
        <div style="font-size:0.8rem;color:#94a3b8;margin-top:4px;max-width:720px;line-height:1.45;">{html_lib.escape(subtitle)}</div>
      </div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_active_chapter_status_card(category_display: str, accuracy_pct_display: str):
    """Right-column floating status with entrance animation."""
    cat_e = html_lib.escape(category_display)
    acc_e = html_lib.escape(accuracy_pct_display)
    st.markdown(
        f"""
<div class="medai-status-float" style="border-radius:16px;padding:18px 18px 20px;
background:linear-gradient(155deg,rgba(17,24,39,0.98),rgba(15,23,42,0.99));
border:1px solid rgba(56,189,248,0.28);box-shadow:0 12px 40px rgba(0,0,0,0.35);">
  <div style="font-size:0.62rem;font-weight:800;letter-spacing:2.5px;color:#64748b;text-transform:uppercase;">
    Active chapter
  </div>
  <div style="font-size:1rem;font-weight:800;color:#f1f5f9;margin-top:10px;line-height:1.35;">
    {cat_e}
  </div>
  <div style="margin-top:14px;height:4px;border-radius:3px;background:#1e293b;overflow:hidden;">
    <div style="width:100%;height:100%;background:linear-gradient(90deg,#0ea5e9,#a78bfa);opacity:0.85;"></div>
  </div>
  <div style="margin-top:12px;font-size:0.78rem;color:#94a3b8;">
    Model hold-out accuracy
    <span style="display:block;font-size:1.25rem;font-weight:800;color:#38bdf8;margin-top:4px;">{acc_e}</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def diagnosis_page_intro():
    """Premium header strip for the diagnosis workflow."""
    st.markdown(
        """
<div class="medai-diag-shell medai-pred-card pc1">
  <div class="medai-diag-inner">
    <p style="margin:0;font-size:0.7rem;font-weight:700;letter-spacing:3px;color:#64748b;text-transform:uppercase;">
      Clinical inference pipeline
    </p>
    <p style="margin:8px 0 0 0;font-size:1.65rem;font-weight:800;background:linear-gradient(90deg,#38bdf8,#a78bfa,#f472b6);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      Differential diagnosis studio
    </p>
    <p style="margin:10px 0 0 0;font-size:0.9rem;color:#94a3b8;line-height:1.55;max-width:820px;">
      Map presenting complaints to the notebook-aligned CatBoost posterior — ranked diseases, therapeutic hints,
      and safety copy pulled from your merged lookup table.
    </p>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = ""):
    st.markdown(f"##### {title}")
    if subtitle:
        st.caption(subtitle)


def info_banner(text: str):
    st.info(text)


def render_summary_cards(items: list[dict]):
    """
    items: list of {title, value, hint, accent_hex optional}
    Renders animated KPI cards in one row (expects len<=6).
    """
    accents = [it.get("accent", "#38bdf8") for it in items]
    delay_cls = ["d1", "d2", "d3", "d4", "d5", "d6"]
    cols = st.columns(len(items))
    for i, (col, it) in enumerate(zip(cols, items)):
        dc = delay_cls[i] if i < len(delay_cls) else "d5"
        title = html_lib.escape(it["title"])
        value = html_lib.escape(str(it["value"]))
        hint = html_lib.escape(it.get("hint", ""))
        ac = accents[i]
        with col:
            st.markdown(
                f"""
<div class="medai-summary-card {dc}" style="border-radius:14px;padding:16px 14px;
background:linear-gradient(160deg,#111827,#0f172a);border:1px solid #1e293b;
border-top:3px solid {ac};min-height:118px;">
  <div style="font-size:0.65rem;font-weight:700;letter-spacing:1.6px;color:#64748b;text-transform:uppercase;">{title}</div>
  <div style="font-size:1.55rem;font-weight:800;color:{ac};margin-top:6px;line-height:1.1;">{value}</div>
  <div style="font-size:0.72rem;color:#94a3b8;margin-top:8px;line-height:1.35;">{hint}</div>
</div>
                """,
                unsafe_allow_html=True,
            )


def _accuracy_color(acc_pct: float) -> str:
    if acc_pct >= 0.95:
        return "#34d399"
    if acc_pct >= 0.90:
        return "#38bdf8"
    if acc_pct >= 0.80:
        return "#fbbf24"
    return "#fb923c"


def render_category_accuracy_cards(cat_res: dict):
    """One animated card per category: accuracy % + F1 + progress bar."""
    rows_sorted = sorted(cat_res.keys(), key=lambda c: cat_res[c]["accuracy"], reverse=True)
    st.markdown("##### Model accuracy by category")
    st.caption("Hold-out accuracy per CatBoost specialist — higher is more reliable within that chapter.")

    delay_cycle = ["a1", "a2", "a3", "a4", "a5"]
    for row_start in range(0, len(rows_sorted), 5):
        chunk = rows_sorted[row_start : row_start + 5]
        cols = st.columns(5)
        for j, cat in enumerate(chunk):
            r = cat_res[cat]
            acc = r["accuracy"] * 100
            f1 = r["f1"] * 100
            acolor = _accuracy_color(r["accuracy"])
            bar_w = min(int(acc), 100)
            dc = delay_cycle[j % 5]
            short_name = cat if len(cat) <= 26 else cat[:24] + "…"
            safe_cat = html_lib.escape(cat)
            safe_short = html_lib.escape(short_name)
            with cols[j]:
                st.markdown(
                    f"""
<div class="medai-acc-card {dc}" style="border-radius:12px;padding:12px 12px 14px;
background:linear-gradient(165deg,#111827,#0c1829);border:1px solid #1e3a5f;margin-bottom:10px;">
  <div style="font-size:0.68rem;font-weight:700;color:#64748b;line-height:1.2;min-height:2.2em;" title="{safe_cat}">
    {safe_short}
  </div>
  <div style="font-size:1.35rem;font-weight:800;color:{acolor};margin-top:6px;">{acc:.1f}%</div>
  <div style="font-size:0.65rem;color:#64748b;margin-top:2px;">F1 · {f1:.1f}%</div>
  <div style="margin-top:10px;height:5px;background:#1e293b;border-radius:4px;overflow:hidden;">
    <div style="width:{bar_w}%;height:100%;background:linear-gradient(90deg,{acolor}66,{acolor});border-radius:4px;
      transition:width 0.8s ease-out;"></div>
  </div>
</div>
                    """,
                    unsafe_allow_html=True,
                )


def metric_row_metrics(items: list[dict]):
    """Fallback compact metrics row."""
    n = len(items)
    cols = st.columns(n)
    for col, it in zip(cols, items):
        with col:
            kwargs = {"label": it["label"], "value": it["value"]}
            if "delta" in it:
                kwargs["delta"] = it["delta"]
            st.metric(**kwargs)


def _therapy_grid_html(rank_border: str, rows: list[tuple[str, str, object, str]]) -> str:
    """
    rows: (badge_title, icon_emoji, raw_value, html_escaped_display)
    """
    accents = [rank_border, "#818cf8", "#f472b6"]
    chunks = []
    for i, (badge, icon, raw, disp) in enumerate(rows):
        ac = accents[i % len(accents)]
        is_ask = str(raw).strip() == "Ask Doctor"
        top = "#fbbf24" if is_ask else ac
        bg = (
            "linear-gradient(165deg,rgba(120,53,15,0.28),rgba(15,23,42,0.95))"
            if is_ask
            else "linear-gradient(165deg,rgba(15,23,42,0.98),rgba(17,24,39,0.85))"
        )
        ring = "rgba(251,191,36,0.45)" if is_ask else "rgba(148,163,184,0.18)"
        badge_txt = "Consult clinician" if is_ask else badge
        chunks.append(
            f"""
<div style="flex:1 1 175px;min-width:155px;max-width:300px;border-radius:14px;padding:14px 16px 16px;
background:{bg};border:1px solid {ring};border-top:4px solid {top};
box-shadow:0 10px 28px rgba(0,0,0,0.35);">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <span style="font-size:0.58rem;font-weight:800;letter-spacing:2px;color:#94a3b8;text-transform:uppercase;">
      {badge_txt}
    </span>
    <span style="font-size:1.05rem;" aria-hidden="true">{icon}</span>
  </div>
  <div style="font-size:0.86rem;font-weight:600;color:#f8fafc;line-height:1.5;word-break:break-word;">{disp}</div>
</div>
            """
        )
    joined = "".join(chunks)
    return f"""
<div style="margin-top:18px;">
  <div style="font-size:0.62rem;font-weight:800;letter-spacing:3px;color:#64748b;margin-bottom:12px;">
    RECOMMENDED THERAPIES
  </div>
  <div style="display:flex;gap:14px;flex-wrap:wrap;align-items:stretch;">
    {joined}
  </div>
</div>
"""


def render_prediction_card(pred: dict):
    """Prediction block with therapy grid + side-effects panel."""
    rank = pred["rank"]
    disease = html_lib.escape(str(pred["disease"]))
    confidence = pred["confidence"]
    risk_level = pred["risk_level"]
    risk_color = pred["risk_color"]
    raw_m1, raw_m2, raw_m3 = pred["medicine_1"], pred["medicine_2"], pred["medicine_3"]
    med1 = html_lib.escape(str(raw_m1))
    med2 = html_lib.escape(str(raw_m2))
    med3 = html_lib.escape(str(raw_m3))
    side = html_lib.escape(str(pred["side_effects"]))
    border_color = {1: "#38bdf8", 2: "#818cf8", 3: "#f472b6"}.get(rank, "#64748b")
    rank_label = {1: "Most likely", 2: "Second", 3: "Third"}.get(rank, "")
    bar_w = min(int(confidence), 100)

    therapy_html = _therapy_grid_html(
        border_color,
        [
            ("Primary option", "💊", raw_m1, med1),
            ("Secondary option", "💊", raw_m2, med2),
            ("Adjunct / supportive", "💊", raw_m3, med3),
        ],
    )

    st.markdown(
        f"""
<div class="medai-disease-card-anim r{rank}">
<div style="background:linear-gradient(145deg,#0f172a,#111827);border:1px solid #1e3a5f;
border-radius:16px;padding:20px 22px;margin-bottom:22px;border-left:4px solid {border_color};
box-shadow:0 8px 32px rgba(0,0,0,0.45);">
  <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-start;gap:12px;">
    <div>
      <span style="font-size:0.7rem;font-weight:700;letter-spacing:1.5px;color:#64748b;text-transform:uppercase;">
        {rank_label}
      </span>
      <h3 style="margin:6px 0 0 0;font-size:1.18rem;font-weight:700;color:#f1f5f9;">{disease}</h3>
    </div>
    <div style="text-align:right;">
      <div style="font-size:1.55rem;font-weight:800;color:{border_color};">{confidence:.1f}%</div>
      <div style="font-size:0.75rem;font-weight:600;color:{risk_color};">{RISK_LABELS.get(risk_level, risk_level)}</div>
    </div>
  </div>
  <div style="margin-top:14px;height:8px;background:#1e293b;border-radius:6px;overflow:hidden;">
    <div style="width:{bar_w}%;height:100%;background:linear-gradient(90deg,{border_color}88,{border_color});border-radius:6px;"></div>
  </div>
  {therapy_html}
  <div style="margin-top:18px;padding:14px 16px;background:linear-gradient(180deg,#0c1222,#0a0f18);border-radius:12px;border:1px solid #1e293b;">
    <span style="font-size:0.68rem;font-weight:800;letter-spacing:2px;color:#64748b;text-transform:uppercase;">Safety · Side effects</span>
    <p style="margin:8px 0 0 0;font-size:0.88rem;color:#cbd5e1;line-height:1.5;">{side}</p>
  </div>
</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_category_buttons_top10(top10: list[str], selected: str | None, key_prefix: str = "cat"):
    """Top categories as full-width buttons in a grid."""
    cols = st.columns(5)
    for i, cat in enumerate(top10):
        with cols[i % 5]:
            label = f"{'✓ ' if cat == selected else ''}{cat}"
            if st.button(label, key=f"{key_prefix}_{i}", use_container_width=True):
                st.session_state["selected_category"] = cat
                st.session_state["diag_cat_sb"] = cat
                st.rerun()


def render_prediction_results_block(results: list, selected_cat: str):
    from analytics import confidence_gauge, top3_confidence_bar, top3_pie

    st.markdown(
        """
<div class="medai-pred-card pc4" style="margin:4px 0 14px 0;">
  <div style="border-radius:14px;padding:14px 18px;background:linear-gradient(105deg,rgba(56,189,248,0.12),rgba(129,140,248,0.06));
  border:1px solid rgba(56,189,248,0.22);">
    <div style="font-size:0.62rem;font-weight:800;letter-spacing:3px;color:#64748b;text-transform:uppercase;">Live analytics</div>
    <div style="font-size:1.05rem;font-weight:800;color:#f1f5f9;margin-top:6px;">Probability & distribution</div>
    <div style="font-size:0.78rem;color:#94a3b8;margin-top:4px;">Gauge, donut, and ranked bars update with each run.</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            confidence_gauge(results[0]["confidence"], results[0]["disease"]),
            use_container_width=True,
            key="pe_gauge",
        )
    with c2:
        st.plotly_chart(top3_pie(results), use_container_width=True, key="pe_pie")
    st.plotly_chart(top3_confidence_bar(results), use_container_width=True, key="pe_bar")

    st.markdown(
        """
<div class="medai-pred-card pc5" style="margin:18px 0 12px 0;">
  <div style="border-radius:14px;padding:12px 16px;border-left:4px solid #a78bfa;background:rgba(129,140,248,0.06);">
    <span style="font-size:0.95rem;font-weight:800;color:#e2e8f0;">Clinical ranking</span>
    <span style="display:block;font-size:0.76rem;color:#94a3b8;margin-top:4px;">Therapy hints and safety text per disease.</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    for pred in results:
        render_prediction_card(pred)


def sidebar_brand():
    st.sidebar.markdown(
        '<p style="text-align:center;font-size:1.5rem;margin:0;">◈</p>'
        '<p style="text-align:center;font-size:1.15rem;font-weight:800;margin:4px 0 0 0;color:#38bdf8;">MedAI</p>'
        '<p style="text-align:center;font-size:0.72rem;color:#94a3b8;margin:2px 0 16px 0;letter-spacing:2px;">'
        "MEDICAL AI PLATFORM</p>",
        unsafe_allow_html=True,
    )
