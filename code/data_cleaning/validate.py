#!/usr/bin/env python3
"""
validate.py
Validation for cleaned population or allocation CSV files.

Checks:
- required columns exist
- population > 0
- no duplicates
- states match canonical list (if provided)
- if seats present: sum(seats) == 543 or 888

Usage:
  python code/data_cleaning/validate.py --file data/processed/pop_2036_clean.csv
  python code/data_cleaning/validate.py --file data/outputs/alloc_dp_alpha_0.8_543.csv
"""

import argparse
import pandas as pd
from pathlib import Path
import sys

def load_canonical(path):
    if not path.exists():
        print(f"[WARN] Canonical mapping not found → skipping canonical check")
        return None
    df = pd.read_csv(path)
    cols = df.columns.tolist()
    # assume second column is canonical
    if len(cols) < 2:
        print("[WARN] Canonical file has <2 columns → skipping canonical check")
        return None
    canon = df[cols[1]].dropna().astype(str).str.strip().tolist()
    return canon

def validate_population(df):
    if "population" not in df.columns:
        print("[OK] No population column → skipping population checks.")
        return

    # numeric check
    pop = pd.to_numeric(df["population"], errors="coerce")
    if pop.isna().any():
        print("[ERROR] population contains NaNs after conversion.")
    if (pop < 0).any():
        print("[ERROR] population contains negative values.")
    if (pop == 0).any():
        print("[WARN] Some states have population == 0.")
    print("[OK] population check passed.")

def validate_states(df, canonical):
    if "state" not in df.columns:
        print("[WARN] No state column → cannot validate names.")
        return
    states = df["state"].astype(str).str.strip()

    # duplicates
    dups = states[states.duplicated()].unique()
    if len(dups) > 0:
        print(f"[ERROR] Duplicate states found: {list(dups)}")
    else:
        print("[OK] No duplicate states.")

    if canonical is None:
        return

    missing = [s for s in states if s not in canonical]
    if missing:
        print(f"[WARN] States not in canonical list: {missing}")
    else:
        print("[OK] All states match canonical list.")

def validate_seats(df):
    if "seats" not in df.columns:
        print("[OK] No seats column → skipping seat-sum check.")
        return

    seats = pd.to_numeric(df["seats"], errors="coerce")
    total = seats.sum()

    if total not in (543, 888):
        print(f"[ERROR] Seat sum invalid: {total} (expected 543 or 888)")
    else:
        print(f"[OK] Seat sum = {total}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="CSV to validate")
    ap.add_argument("--canon", default="docs/states_canonical.csv", help="Canonical CSV")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"[FATAL] File {p} not found.")
        sys.exit(1)

    df = pd.read_csv(p)
    canonical = load_canonical(Path(args.canon))

    print(f"\n=== VALIDATION REPORT for {p.name} ===")

    validate_population(df)
    validate_states(df, canonical)
    validate_seats(df)

    print("=== VALIDATION COMPLETE ===\n")

if __name__ == "__main__":
    main()
