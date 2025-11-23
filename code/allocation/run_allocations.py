#!/usr/bin/env python3
"""
run_allocations.py
- Runs proportional and Degressive Proportional (DP) seat allocations.
- Input : cleaned population file with columns [state, population]
- Output: CSVs for proportional & DP allocations for all α values requested.
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path


# -------------------------
# Core Allocation Functions
# -------------------------

def proportional_allocation(pop, seats_total):
    """Strict proportional allocation via Hamilton (largest remainder)."""
    quotas = pop / pop.sum() * seats_total
    base = np.floor(quotas).astype(int)
    remainder = quotas - base

    seats_left = seats_total - base.sum()
    idx = np.argsort(-remainder)[:seats_left]
    base[idx] += 1
    return base


def dp_allocation(pop, seats_total, alpha):
    """Degressive proportional allocation: seats ∝ population^α."""
    weights = pop ** alpha
    return proportional_allocation(weights, seats_total)


# -------------------------
# Runner
# -------------------------

def run(pop_file, out_dir, seats, alphas):
    df = pd.read_csv(pop_file)

    if "population" not in df.columns:
        raise ValueError("Input file must contain a 'population' column.")

    states = df["state"]
    pop = df["population"].astype(float)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- proportional (α = 1) ---
    prop_seats = proportional_allocation(pop, seats)
    pd.DataFrame({
        "state": states,
        "population": pop,
        "seats": prop_seats
    }).to_csv(out_dir / f"alloc_proportional_{seats}.csv", index=False)

    # --- DP α versions ---
    for a in alphas:
        dp_seats = dp_allocation(pop, seats, a)
        pd.DataFrame({
            "state": states,
            "population": pop,
            "alpha": a,
            "seats": dp_seats
        }).to_csv(out_dir / f"alloc_dp_alpha_{a}_{seats}.csv", index=False)

    print("Allocations completed.")


# -------------------------
# CLI
# -------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--infile", required=True, help="Cleaned population CSV")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--seats", type=int, required=True, help="Total seats (543 or 888)")
    p.add_argument(
        "--alpha",
        nargs="+",
        type=float,
        default=[0.4, 0.5, 0.6, 0.8, 0.9],
        help="DP α values"
    )

    args = p.parse_args()

    run(args.infile, args.out, args.seats, args.alpha)
