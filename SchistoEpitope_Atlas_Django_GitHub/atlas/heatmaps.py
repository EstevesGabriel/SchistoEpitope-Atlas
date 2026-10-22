"""Build interactive Plotly heatmaps from the real processed Atlas CSV files."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_ROOT = BASE_DIR / "data" / "processed"

HOST_LABELS = {
    "human": "Human",
    "mouse": "Mouse",
    "rhesus": "Rhesus Macaque",
    "baboon": "Baboon",
    "chimp": "Chimpanzee",
}

TISSUES = [
    ("more_reactive_teg", "Tegument — More Reactive"),
    ("less_reactive_teg", "Tegument — Less Reactive"),
    ("gastrodermis_carreadores", "Gastrodermis — Carriers"),
    ("gastrodermis_enzymes", "Gastrodermis — Enzymes"),
    ("esophageal_gland", "Esophageal Gland"),
]

STUDIES = {
    "vance-2024": {
        "id": "vance_2024",
        "label": "Vance et al. (2024)",
        "description": "Rhesus samples labelled Hi/Low",
    },
    "woellner-2024": {
        "id": "woellner_2024",
        "label": "Woellner-Santos et al. (2024)",
        "description": "Rhesus samples labelled Fast/Slow",
    },
}

PEPTIDE_COLUMNS = {
    "human": ("Human Peptides", "Human Peptide"),
    "human_ige": ("Human Peptides", "Human Peptide"),
    "mouse": ("Mouse Peptides", "Mouse Peptide"),
    "rhesus": ("Rhesus Peptides", "Rhesus Peptide"),
    # Provenance rule: these hosts use Mouse peptide identifiers from the same tissue/row.
    "baboon": ("Mouse Peptides", "Mouse Peptide"),
    "chimp": ("Mouse Peptides", "Mouse Peptide"),
}
PROTEIN_COLUMNS = ("Proteins", "Protein")
VMIN = 6000
VMAX = 40000
PSA_TICKS = [6000, 10000, 20000, 30000, 40000]
COLORSCALE = [[0.0, "#FFFFFF"], [0.5, "#7FDBFF"], [1.0, "#FF0000"]]


def _find_column(columns, candidates):
    by_normalized = {str(c).strip().casefold(): c for c in columns}
    for candidate in candidates:
        found = by_normalized.get(candidate.strip().casefold())
        if found is not None:
            return found
    return None


def _study_for_sample(sample: str) -> str:
    """Assign a Rhesus sample to a known source; fail closed on unknown labels."""
    normalized = re.sub(r"\s+", " ", str(sample)).strip().casefold()
    if re.search(r"\b(?:hi|low|lo)\b", normalized):
        return "vance_2024"
    if re.search(r"\b(?:fast|slow)\s*\d+\b", normalized):
        return "woellner_2024"
    raise ValueError(
        f"Rhesus sample '{sample}' could not be assigned to a known study source. "
        "The heatmap was not generated to avoid mixing experimental sources."
    )


def _read_tissue(host: str, tissue_key: str) -> pd.DataFrame:
    path = PROCESSED_ROOT / host / f"{tissue_key}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Processed dataset not found: {path.relative_to(BASE_DIR)}")
    df = pd.read_csv(path)
    protein_col = _find_column(df.columns, PROTEIN_COLUMNS)
    peptide_col = _find_column(df.columns, PEPTIDE_COLUMNS[host])
    if protein_col is None:
        raise ValueError(f"No Proteins/Protein column found in {path.name}.")
    if peptide_col is None:
        raise ValueError(
            f"No real peptide identifier column found in {path.name}; synthetic epitope labels are disabled."
        )
    df = df.copy()
    df[protein_col] = df[protein_col].ffill().astype("string").str.strip()
    df[peptide_col] = df[peptide_col].astype("string").str.strip()
    df = df.dropna(subset=[peptide_col])
    df = df[df[peptide_col].ne("")]
    return df, protein_col, peptide_col


def _measurement_columns(df: pd.DataFrame, protein_col: str, peptide_col: str) -> list[str]:
    excluded = {protein_col, peptide_col}
    result = []
    for column in df.columns:
        if column in excluded:
            continue
        numeric = pd.to_numeric(df[column], errors="coerce")
        if numeric.notna().any():
            result.append(column)
    return result


def _protein_blocks(proteins: list[str]) -> list[dict]:
    if not proteins:
        return []
    blocks = []
    start = 0
    current = str(proteins[0])
    for idx in range(1, len(proteins)):
        protein = str(proteins[idx])
        if protein != current:
            end = idx - 1
            blocks.append({"protein": current, "start": start, "end": end, "center": (start + end) / 2})
            start, current = idx, protein
    end = len(proteins) - 1
    blocks.append({"protein": current, "start": start, "end": end, "center": (start + end) / 2})
    return blocks


def build_figure(host: str, tissue_key: str, tissue_label: str, study_key: str | None = None):
    df, protein_col, peptide_col = _read_tissue(host, tissue_key)
    measurement_label = "Fluorescence Intensity" if host == "human_ige" else "PSA Score"
    sample_columns = _measurement_columns(df, protein_col, peptide_col)

    if host == "rhesus":
        study_id = STUDIES[study_key]["id"]
        sample_to_study = {column: _study_for_sample(column) for column in sample_columns}
        sample_columns = [column for column in sample_columns if sample_to_study[column] == study_id]

    if not sample_columns:
        raise ValueError("No numeric sample measurements are available for this host/tissue/study.")

    for column in sample_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=sample_columns, how="all")
    if df.empty:
        raise ValueError("The selected dataset contains no numeric measurements.")

    proteins = df[protein_col].fillna("Unknown protein").astype(str).tolist()
    peptides = df[peptide_col].astype(str).tolist()
    matrix = df[sample_columns].to_numpy(dtype=float).T
    customdata = [
        [[proteins[col], peptides[col], None if pd.isna(matrix[row, col]) else float(matrix[row, col])
          ] for col in range(len(peptides))]
        for row in range(len(sample_columns))
    ]

    fig = go.Figure(
        data=[go.Heatmap(
            z=matrix,
            x=list(range(len(peptides))),
            y=list(range(len(sample_columns))),
            customdata=customdata,
            colorscale=COLORSCALE,
            zmin=VMIN,
            zmax=VMAX,
            zsmooth=False,
            xgap=0.5,
            ygap=0.5,
            connectgaps=False,
            hovertemplate="<extra></extra>",
            colorbar={
                "title": {"text": measurement_label, "side": "right", "font": {"size": 18}},
                "tickmode": "array",
                "tickvals": PSA_TICKS,
                "ticktext": [f"{v:,}" for v in PSA_TICKS],
                "tickfont": {"size": 16},
                "thickness": 18,
                "len": 0.86,
            },
        )]
    )
    blocks = _protein_blocks(proteins)
    fig.update_layout(
        title={"text": tissue_label, "x": 0.01, "xanchor": "left", "font": {"size": 25}},
        font={"family": "Arial, sans-serif", "size": 16, "color": "#243746"},
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin={"l": 90, "r": 95, "t": 72, "b": 155},
        height=max(500, min(950, 250 + len(sample_columns) * 28)),
        hovermode="closest",
        xaxis={
            "tickmode": "array",
            "tickvals": [b["center"] for b in blocks],
            "ticktext": [b["protein"] for b in blocks],
            "tickangle": 45,
            "tickfont": {"size": 16},
            "side": "bottom",
            "showgrid": False,
            "zeroline": False,
            "range": [-0.5, len(peptides) - 0.5],
        },
        yaxis={
            "tickmode": "array",
            "tickvals": list(range(len(sample_columns))),
            "ticktext": sample_columns,
            "tickfont": {"size": 16},
            "title": {"text": "Samples", "font": {"size": 18}},
            "autorange": "reversed",
            "showgrid": False,
            "zeroline": False,
            "range": [-0.5, len(sample_columns) - 0.5],
        },
        shapes=[
            {
                "type": "line",
                "x0": block["start"] - 0.5,
                "x1": block["start"] - 0.5,
                "y0": -0.5,
                "y1": len(sample_columns) - 0.5,
                "line": {"color": "rgba(0,0,0,0.60)", "width": 1, "dash": "dot"},
            }
            for block in blocks[1:]
        ],
    )
    return fig


def get_host_charts(host: str, study_key: str | None = None) -> tuple[list[dict], list[str]]:
    charts, errors = [], []
    for tissue_key, tissue_label in TISSUES:
        try:
            figure = build_figure(host, tissue_key, tissue_label, study_key)
            charts.append({
                "tissue_key": tissue_key,
                "tissue_label": tissue_label,
                "script_id": f"figure-{tissue_key}",
                "figure_json": json.loads(figure.to_json()),
                "measurement_label": "Fluorescence Intensity" if host == "human_ige" else "PSA Score",
            })
        except (FileNotFoundError, ValueError, KeyError) as exc:
            errors.append(f"{tissue_label}: {exc}")
    return charts, errors
