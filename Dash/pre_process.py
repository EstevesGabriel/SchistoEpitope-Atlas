"""
SchistoEpitope Atlas
====================

Pre-processing pipeline for the "More Reactive Teg" worksheet.

The source workbook uses vertically merged cells in the Proteins column.
Pandas reads only the first cell of each merged region; the remaining cells
become NaN. This script reconstructs those protein labels and exports three
host-specific tables for downstream analysis and visualization.

Data-integrity rule
-------------------
NaN values are preserved as missing observations. They are never converted
into zero. Literal zero measurements remain zero.
"""

from pathlib import Path

import pandas as pd


# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_SOURCE = (
    "https://raw.githubusercontent.com/EstevesGabriel/"
    "SchistoEpitope-Atlas/main/"
    "Final%20Human%20X%20All%20Rhesus%20X%20Mouse.xlsx"
)

SHEET_NAME = "More Reactive Teg"
OUTPUT_DIR = Path("data/processed")


HUMAN_COLUMNS = [
    "Proteins",
    "Human Peptides",
    "N-endemic",
    "SR Sum",
    "SR Mean",
    "SR 13506",
    "SR 02704",
    "SR 13502",
    "SR 19003",
    "SR 13508",
    "SR 12606",
    "SR 13304",
    "SR 16101",
    "RR Sum",
    "RR Mean",
    "RR 18301",
    "RR 02502",
    "RR 02701",
    "RR 19302",
    "RR 18805",
    "RR 17704",
    "RR 00301",
    "RR 16406",
    "RR 12302",
    "Human Sum",
    "Human Mean",
]

MOUSE_COLUMNS = [
    "Proteins",
    "Mouse x Human",
    "Mouse Peptide",
    "Mean All",
    "Control",
    "IFNgR KO 2&3",
    "Mean Infec",
    "Infect 3",
    "Infect 2",
    "Infect 1",
    "Mean Vaccn",
    "Vaccn 3",
    "Vaccn 2",
    "Vaccn 1",
]

RHESUS_COLUMNS = [
    "Proteins",
    "Rhesus Peptides",
    "Fast 2 W10",
    "Fast 2 W42",
    "Fast 2 W43",
    "Fast 2 W46",
    "Fast 3 W10",
    "Fast 3 W42",
    "Fast 3 W43",
    "Fast 3 W46",
    "Fast 4 W10",
    "Fast 4 W42",
    "Fast 4 W43",
    "Fast 4 W46",
    "Fast 9 W10",
    "Fast 9 W42",
    "Fast 9 W43",
    "Fast 9 W46",
    "Slow 5 w10",
    "Slow 5 w42",
    "Slow 5 w43",
    "Slow 5 w46",
    "Slow 6 w10",
    "Slow 6 w42",
    "Slow 6 w43",
    "Slow 6 w46",
    "Slow 8 w10",
    "Slow 8 w42",
    "Slow 8 w43",
    "Slow 8 w46",
    "Slow 11 w10",
    "Slow 11 w42",
    "Slow 11 w43",
    "Slow 11 w46",
    "Sum",
    "Rhe Mean",
]


def validate_columns(dataframe: pd.DataFrame, columns: list[str], name: str) -> None:
    """Raise an informative error when an expected column is absent."""
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise ValueError(
            f"{name}: missing expected columns: {', '.join(missing)}"
        )


def prepare_proteins(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Reconstruct vertically merged protein labels without touching other columns."""
    result = dataframe.copy()
    result["Proteins"] = result["Proteins"].ffill()
    return result


def build_host_table(
    dataframe: pd.DataFrame,
    columns: list[str],
    peptide_column: str,
) -> pd.DataFrame:
    """Create one host-specific table while preserving all non-key NaN values."""
    table = dataframe.loc[:, columns].copy()
    table = table.dropna(subset=[peptide_column])
    table = table.dropna(axis=1, how="all")
    return table


def export_csv(dataframe: pd.DataFrame, filename: str) -> Path:
    """Export a processed dataframe and return its path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    dataframe.to_csv(path, index=False)
    return path


def main() -> None:
    print("=" * 72)
    print("SCHISTOEPITOPE ATLAS — PRE-PROCESSING")
    print("=" * 72)
    print(f"Worksheet: {SHEET_NAME}")
    print("Reading source workbook...")

    dataframe = pd.read_excel(
        DATA_SOURCE,
        sheet_name=SHEET_NAME,
        engine="openpyxl",
    )

    print(f"Rows loaded:    {dataframe.shape[0]}")
    print(f"Columns loaded: {dataframe.shape[1]}")

    print("\nReconstructing merged protein labels...")
    dataframe = prepare_proteins(dataframe)

    print("Validating schema...")
    validate_columns(dataframe, HUMAN_COLUMNS, "Human")
    validate_columns(dataframe, MOUSE_COLUMNS, "Mouse")
    validate_columns(dataframe, RHESUS_COLUMNS, "Rhesus")

    human = build_host_table(dataframe, HUMAN_COLUMNS, "Human Peptides")
    mouse = build_host_table(dataframe, MOUSE_COLUMNS, "Mouse Peptide")
    rhesus = build_host_table(dataframe, RHESUS_COLUMNS, "Rhesus Peptides")

    outputs = {
        "Human": export_csv(human, "human_epitopes.csv"),
        "Mouse": export_csv(mouse, "mouse_epitopes.csv"),
        "Rhesus": export_csv(rhesus, "rhesus_epitopes.csv"),
    }

    print("\n" + "=" * 72)
    print("QUALITY CONTROL")
    print("=" * 72)

    for name, table in (("Human", human), ("Mouse", mouse), ("Rhesus", rhesus)):
        nan_count = int(table.isna().sum().sum())
        zero_count = int((table == 0).sum().sum())
        protein_count = int(table["Proteins"].nunique(dropna=True))
        peptide_col = {
            "Human": "Human Peptides",
            "Mouse": "Mouse Peptide",
            "Rhesus": "Rhesus Peptides",
        }[name]
        peptide_count = int(table[peptide_col].notna().sum())

        print(f"\n{name}")
        print(f"  Rows:       {len(table)}")
        print(f"  Columns:    {len(table.columns)}")
        print(f"  Proteins:   {protein_count}")
        print(f"  Peptides:   {peptide_count}")
        print(f"  NaN values: {nan_count}")
        print(f"  Zero values:{zero_count}")
        print(f"  Output:     {outputs[name]}")

    print("\nData-integrity rule: NaN preserved; zeros preserved; no imputation performed.")
    print("Pre-processing completed successfully.")


if __name__ == "__main__":
    main()
