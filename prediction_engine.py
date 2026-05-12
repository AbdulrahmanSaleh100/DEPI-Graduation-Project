"""
prediction_engine.py
--------------------
Core prediction logic.  Given a category and a list of selected symptom
names, returns the top-3 most likely diseases with confidence scores,
risk levels, and treatment information.
"""

import numpy as np


# ── Risk thresholds ────────────────────────────────────────────────────────────
RISK_HIGH   = 70   # >= 70 %
RISK_MEDIUM = 40   # 40 – 69 %
# Below 40 % = Low risk


def _get_risk_level(confidence_pct: float) -> str:
    """Classify confidence score into High / Medium / Low."""
    if confidence_pct >= RISK_HIGH:
        return "High"
    elif confidence_pct >= RISK_MEDIUM:
        return "Medium"
    return "Low"


def _risk_color(risk_level: str) -> str:
    """Map risk level to a hex color for the UI."""
    return {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"}.get(risk_level, "#95a5a6")


def _display_value(val: str) -> str:
    """Return 'Ask Doctor' when the stored value is unknown or empty."""
    s = str(val).strip()
    if not s or s.lower() in ("un known", "unknown", "nan"):
        return "Ask Doctor"
    return s


def _lookup_disease_row(lookup: dict, disease_name: str) -> dict:
    """
    Resolve disease → {medicine_*, side_effects}.

    Uses exact key first, then case-insensitive match, because a mismatch
    would otherwise yield {} and every field becomes 'Un Known' → 'Ask Doctor'.
    """
    if disease_name in lookup:
        return lookup[disease_name]
    dn = str(disease_name).strip()
    if not dn:
        return {}
    dnl = dn.lower()
    for k, v in lookup.items():
        if str(k).strip().lower() == dnl:
            return v
    return {}


def get_top_symptoms_for_category(category: str, artifacts: dict) -> list:
    """Return the top-15 most common symptoms for a disease category."""
    cat_top = artifacts["category_top_symptoms"]
    if category not in cat_top:
        raise ValueError(f"Unknown category: '{category}'")
    return cat_top[category]


def predict_top3(category: str, selected_symptoms: list, artifacts: dict) -> list:
    """
    Predict the TOP 3 most likely diseases for the given category,
    ordered from highest to lowest confidence.

    Parameters
    ----------
    category          : str  - disease category chosen by the user
    selected_symptoms : list[str] - symptom column names marked as present
    artifacts         : dict - output of load_all_artifacts()

    Returns
    -------
    list of up to 3 dicts, each with:
        rank, disease, confidence (%), risk_level, risk_color,
        medicine_1, medicine_2, medicine_3, side_effects
    """
    models   = artifacts["category_models"]
    encoders = artifacts["category_encoders"]
    sym_cols = artifacts["symptom_cols"]
    lookup   = artifacts["lookup_dict"]

    if category not in models:
        raise ValueError(f"No model found for category: '{category}'")

    # Build binary feature vector
    vec = np.zeros(len(sym_cols), dtype=int)
    for sym in selected_symptoms:
        if sym in sym_cols:
            vec[sym_cols.index(sym)] = 1

    model   = models[category]
    encoder = encoders[category]

    # Probability for every disease class in this category
    probabilities = model.predict_proba([vec])[0]

    # Rank by probability descending; take top 3
    n_top = min(3, len(probabilities))
    top_indices = np.argsort(probabilities)[::-1][:n_top]

    results = []
    for rank, idx in enumerate(top_indices, start=1):
        disease_name = encoder.inverse_transform([int(idx)])[0]
        confidence   = round(float(probabilities[idx]) * 100, 2)
        risk_level   = _get_risk_level(confidence)

        info = _lookup_disease_row(lookup, disease_name)

        results.append({
            "rank":        rank,
            "disease":     disease_name,
            "confidence":  confidence,
            "risk_level":  risk_level,
            "risk_color":  _risk_color(risk_level),
            "medicine_1":  _display_value(info.get("medicine_1",  "Un Known")),
            "medicine_2":  _display_value(info.get("medicine_2",  "Un Known")),
            "medicine_3":  _display_value(info.get("medicine_3",  "Un Known")),
            "side_effects":_display_value(info.get("side_effects", "Un Known")),
        })

    return results
