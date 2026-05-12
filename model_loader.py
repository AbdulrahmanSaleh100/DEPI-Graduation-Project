"""
model_loader.py
---------------
Loads all CatBoost per-category models and shared JSON artifacts.
Results are cached with st.cache_resource so they load only once.
"""

import os
import json
import joblib
import streamlit as st


ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "model_artifacts")
MODELS_DIR    = os.path.join(ARTIFACTS_DIR, "category_models")


@st.cache_resource(show_spinner="Loading AI models...")
def load_all_artifacts():
    """
    Load every artifact needed by the dashboard.

    Returns
    -------
    dict with keys:
        symptom_cols          : list[str]   - 377 ordered symptom column names
        lookup_dict           : dict        - disease -> {medicine_1..3, side_effects}
        category_top_symptoms : dict        - category -> top-15 symptom list
        category_models       : dict        - category -> CatBoost model
        category_encoders     : dict        - category -> LabelEncoder
        summary               : dict        - performance metrics
    """
    # JSON artifacts
    with open(os.path.join(ARTIFACTS_DIR, "symptom_cols.json"))           as f:
        symptom_cols = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "lookup_dict.json"),
              encoding="utf-8")                                             as f:
        lookup_dict = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "category_top_symptoms.json"),
              encoding="utf-8")                                             as f:
        category_top_symptoms = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "summary.json"))                as f:
        summary = json.load(f)

    # Per-category CatBoost models and LabelEncoders
    category_models   = {}
    category_encoders = {}

    for fname in sorted(os.listdir(MODELS_DIR)):
        if not fname.endswith("_model.pkl"):
            continue
        # Reconstruct category name: "Gynecologic_Disorder_model.pkl" -> "Gynecologic Disorder"
        cat_safe = fname.replace("_model.pkl", "")
        # Map file safe name back to original category name
        cat_name = cat_safe.replace("_", " ")
        # Handle "Substance-Related Disorder" which has a hyphen
        # Files are stored as "Substance-Related_Disorder_model.pkl"
        model_path   = os.path.join(MODELS_DIR, fname)
        encoder_path = os.path.join(MODELS_DIR, fname.replace("_model.pkl", "_encoder.pkl"))

        category_models[cat_name]   = joblib.load(model_path)
        category_encoders[cat_name] = joblib.load(encoder_path)

    return {
        "symptom_cols":          symptom_cols,
        "lookup_dict":           lookup_dict,
        "category_top_symptoms": category_top_symptoms,
        "category_models":       category_models,
        "category_encoders":     category_encoders,
        "summary":               summary,
    }
