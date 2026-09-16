"""Milestone 1 EDA dashboard for the Adaptive Timeline Organizer.

Run locally:
  /home/alihamdi/python-env/ml/bin/streamlit run app/milestone_01_eda_dashboard.py

The dashboard is intentionally analysis-only. It does not load or invoke a
model. A later milestone may attach a trained artifact through the documented
model contract without changing the EDA notebook.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "notebooks" / "outputs" / "milestone_01_eda"
OUTPUT_DIR = Path(os.getenv("MSLATTE_EDA_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))


@st.cache_data
def load_metrics(directory: str) -> dict:
    with (Path(directory) / "eda_metrics.json").open(encoding="utf-8") as source:
        return json.load(source)


@st.cache_data
def load_task_audit(directory: str) -> pd.DataFrame:
    return pd.read_csv(Path(directory) / "task_level_audit.csv")


def require_eda_exports() -> bool:
    missing = [name for name in ("eda_metrics.json", "task_level_audit.csv") if not (OUTPUT_DIR / name).is_file()]
    if missing:
        st.error("Milestone 1 EDA exports are not available.")
        st.code(
            "MSLATTE_PATH=/path/to/MS-LaTTE.json jupyter nbconvert --to notebook "
            "--execute --inplace notebooks/01_mslatte_milestone1_full_eda_kaggle.ipynb"
        )
        st.caption(f"Expected output folder: {OUTPUT_DIR}")
        return False
    return True


st.set_page_config(page_title="MS-LaTTE | Milestone 1 EDA", page_icon="📊", layout="wide")
st.title("MS-LaTTE — Milestone 1: Data Foundation & EDA")
st.caption("Adaptive Timeline Organizer · analysis dashboard · no trained model loaded")

if require_eda_exports():
    metrics = load_metrics(str(OUTPUT_DIR))
    tasks = load_task_audit(str(OUTPUT_DIR))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Task records", f"{metrics['records']:,}")
    col2.metric("Unique list titles", f"{metrics['unique_list_titles']:,}")
    col3.metric("Known time labels", f"{metrics['known_time_annotation_rate']:.1%}")
    col4.metric("Known locations", f"{metrics['known_location_annotation_rate']:.1%}")

    st.subheader("Dataset integrity")
    integrity = pd.DataFrame(
        {
            "Check": ["Unique IDs", "Empty task titles", "Duplicate-title records", "Privacy replacement markers"],
            "Value": [
                f"{metrics['unique_ids']:,} / {metrics['records']:,}",
                metrics["empty_task_titles"],
                metrics["records_in_duplicate_title_groups"],
                metrics["records_containing_privacy_replacement_zero"],
            ],
        }
    )
    st.dataframe(integrity, hide_index=True, use_container_width=True)

    st.subheader("EDA figures")
    figure_dir = OUTPUT_DIR / "figures"
    figures = sorted(figure_dir.glob("*.png"))
    if figures:
        for left, right in zip(figures[::2], figures[1::2] + [None] * (len(figures) % 2)):
            a, b = st.columns(2)
            a.image(str(left), caption=left.stem, use_container_width=True)
            if right:
                b.image(str(right), caption=right.stem, use_container_width=True)

    st.subheader("Task-level audit")
    query = st.text_input("Search a task or list title")
    preview = tasks
    if query.strip():
        mask = preview["task_title"].fillna("").str.contains(query, case=False, regex=False)
        mask |= preview["list_title"].fillna("").str.contains(query, case=False, regex=False)
        preview = preview.loc[mask]
    st.dataframe(preview, use_container_width=True, hide_index=True, height=360)

    with st.expander("Future model connection contract"):
        st.markdown(
            """
            This dashboard intentionally does **not** run a model during Milestone 1.
            After model training is complete, add a versioned model artifact and
            `model_manifest.json` under `models/`. The manifest must define:
            `artifact_path`, `feature_schema_version`, `trained_on_split`,
            `metrics`, and `label_definition`. Only then should a prediction page
            load the artifact and expose inference.
            """
        )
