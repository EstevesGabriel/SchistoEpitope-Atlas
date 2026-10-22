"""Data-integrity checks for the processed Atlas datasets."""
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
HUMAN_IGE = DATA / "human_ige"
TISSUES = [
    "more_reactive_teg",
    "less_reactive_teg",
    "gastrodermis_carreadores",
    "gastrodermis_enzymes",
    "esophageal_gland",
]


def peptide_column(frame):
    return next((c for c in frame.columns if str(c).strip().casefold() in {"mouse peptide", "mouse peptides"}), None)


class ProcessedDataIntegrityTests(unittest.TestCase):
    def test_expected_host_tissue_csvs_exist(self):
        for host in ("human", "mouse", "rhesus", "baboon", "chimp"):
            for tissue in TISSUES:
                self.assertTrue((DATA / host / f"{tissue}.csv").exists(), f"Missing {host}/{tissue}.csv")

    def test_baboon_and_chimp_peptide_ids_match_mouse_by_tissue_and_row(self):
        for host in ("baboon", "chimp"):
            for tissue in TISSUES:
                mouse = pd.read_csv(DATA / "mouse" / f"{tissue}.csv")
                other = pd.read_csv(DATA / host / f"{tissue}.csv")
                mouse_peptide = peptide_column(mouse)
                host_peptide = peptide_column(other)
                self.assertIsNotNone(mouse_peptide)
                self.assertIsNotNone(host_peptide)
                self.assertEqual(mouse[mouse_peptide].fillna("").tolist(), other[host_peptide].fillna("").tolist())

    def test_no_synthetic_epitope_columns_are_present(self):
        for host in ("human", "mouse", "rhesus", "baboon", "chimp"):
            for tissue in TISSUES:
                frame = pd.read_csv(DATA / host / f"{tissue}.csv", nrows=5)
                self.assertFalse(any(str(c).casefold().startswith("epitope ") for c in frame.columns))

    def test_human_ige_contains_only_the_five_approved_tissues(self):
        for tissue in TISSUES:
            self.assertTrue((HUMAN_IGE / f"{tissue}.csv").exists(), f"Missing human_ige/{tissue}.csv")
        self.assertEqual(sorted(p.stem for p in HUMAN_IGE.glob("*.csv")), sorted(TISSUES))

    def test_human_ige_keeps_adapter_prefixes_and_uses_intensity_columns(self):
        frame = pd.read_csv(HUMAN_IGE / "more_reactive_teg.csv")
        self.assertEqual(len(frame), 1331)
        self.assertIn("Human Peptides", frame.columns)
        self.assertIn("Proteins", frame.columns)
        self.assertEqual(frame.loc[0, "Human Peptides"], "GSGSGEENSNSIITD")
        self.assertTrue(frame["Human Peptides"].astype(str).str.startswith(("GSG", "SGSG")).any())
        self.assertIn("NE", frame.columns)
        self.assertIn("SR 8", frame.columns)
        self.assertIn("RR 1", frame.columns)
        self.assertFalse(any(str(c).startswith("Unnamed:") for c in frame.columns))

    def test_human_ige_keeps_missing_measurements_missing(self):
        frame = pd.read_csv(HUMAN_IGE / "more_reactive_teg.csv")
        self.assertTrue(frame["SR 8"].isna().any())


if __name__ == "__main__":
    unittest.main()
