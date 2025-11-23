#!/usr/bin/env python3
"""
compute_indicators.py

Inputs:
 - cleaned population CSV (state,population) e.g. data/processed/pop_2036_clean.csv
 - allocation CSVs in a directory (data/outputs) with columns at least: state,seats
   Expected filenames include "proportional" and "dp_alpha" variants.

Outputs (annexures/):
 - Annexure_C_MI_Table.csv        (per-allocation: state, population, seats, seats_per_million, rep_ratio, elasticity)
 - Annexure_D_Elasticity_Summary.csv (summary per allocation: median/mean elasticity etc.)
 - Annexure_E_MRC_Summary.csv     (MRC = mean relative change vs proportional)
 - fairness_indicators.csv        (one-line summary per allocation: Gini, MI, avg_rep_ratio, etc.)

Run:
 python code/analysis/compute_indicators.py --pop data/processed/pop_2036_clean.csv --alloc_dir data/outputs --out annexures
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import glob

def gini(x: np.ndarray):
    """Gini coefficient for positive array x."""
    x = x.flatten()
    x = x[~np.isnan(x)]
    if x.size == 0:
        return np.nan
    if np.any(x < 0):
        x = x - x.min()  # shift to non-negative
    n = x.size
    if n == 0:
        return np.nan
    sorted_x = np.sort(x)
    cumx = np.cumsum(sorted_x, dtype=float)
    sum_x = cumx[-1]
    if sum_x == 0:
        return 0.0
    idx = np.arange(1, n+1)
    return (2.0 * np.sum(idx * sorted_x) / (n * sum_x)) - (n + 1) / n

def compute_metrics(df_merge):
    """
    df_merge must have columns: state, population, seats
    Returns the df with added columns and some summary metrics.
    """
    S = df_merge['seats'].sum()
    P = df_merge['population'].sum()
    df = df_merge.copy()
    # seats per million
    df['seats_per_million'] = df['seats'] / (df['population'] / 1e6)
    # representation ratio (seats per million) alternative label
    df['rep_ratio'] = df['seats'] / (df['population'] / 1e6)
    # shares
    df['seats_share'] = df['seats'] / S
    df['pop_share'] = df['population'] / P
    # elasticity (seats_share / pop_share) -> >1 favors state, <1 disfavors
    df['elasticity'] = df['seats_share'] / df['pop_share']
    # Malapportionment Index (MI) defined here as 0.5 * sum |(seats/pop) - (S/P)| scaled to per million:
    # (seats/pop) has unit seats/person; multiply by 1e6 to be seats per million.
    df['seats_per_person'] = df['seats'] / df['population']
    avg_seats_per_person = S / P
    df['seats_per_million_diff'] = (df['seats_per_person'] - avg_seats_per_person) * 1e6
    MI = 0.5 * np.sum(np.abs(df['seats_per_million_diff']))  # seats-per-million index
    # Gini on seats_per_million (interprets inequality of representation intensity)
    G = gini(df['seats_per_million'].replace([np.inf, -np.inf], np.nan).fillna(0).values)
    # simple summaries
    summary = {
        'total_seats': int(S),
        'total_population': int(P),
        'MI_seats_per_million': float(MI),
        'Gini_seats_per_million': float(G),
        'mean_elasticity': float(np.nanmean(df['elasticity'])),
        'median_elasticity': float(np.nanmedian(df['elasticity'])),
        'mean_seats_per_million': float(np.nanmean(df['seats_per_million'])),
    }
    return df, summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", required=True, help="Clean population CSV (state,population)")
    ap.add_argument("--alloc_dir", default="data/outputs", help="Directory with allocation CSVs")
    ap.add_argument("--out", default="annexures", help="Output annexures dir")
    args = ap.parse_args()

    p_pop = Path(args.pop)
    alloc_dir = Path(args.alloc_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    pop_df = pd.read_csv(p_pop)
    pop_df = pop_df.rename(columns={col: col.strip() for col in pop_df.columns})
    if 'state' not in pop_df.columns or 'population' not in pop_df.columns:
        raise SystemExit("Population file must have 'state' and 'population' columns.")

    # find allocation files
    alloc_files = sorted([Path(p) for p in glob.glob(str(alloc_dir / "*.csv"))])
    if not alloc_files:
        raise SystemExit(f"No allocation CSVs found in {alloc_dir}")

    summaries = []
    # try to find proportional baseline file (filename containing 'proportional')
    prop_file = None
    for f in alloc_files:
        if 'proportional' in f.name.lower():
            prop_file = f
            break

    prop_df = None
    if prop_file is not None:
        prop_df = pd.read_csv(prop_file)

    # loop over allocation files
    annexure_c_rows = []
    elasticity_summaries = []
    mrc_rows = []  # MRC summary rows
    for f in alloc_files:
        a_df = pd.read_csv(f)
        # find seats column name
        seats_cols = [c for c in a_df.columns if c.lower() in ('seats','seat','allocated','allocation')]
        if not seats_cols:
            raise SystemExit(f"No seats-like column in {f.name}")
        seats_col = seats_cols[0]
        a_df = a_df.rename(columns={seats_col: 'seats'})
        # ensure state col
        state_cols = [c for c in a_df.columns if c.lower() in ('state','state_name','region')]
        if not state_cols:
            raise SystemExit(f"No state-like column in {f.name}")
        state_col = state_cols[0]
        a_df = a_df.rename(columns={state_col: 'state'})

        merged = pd.merge(pop_df[['state','population']], a_df[['state','seats']], on='state', how='left')
        if merged['seats'].isna().any():
            print(f"[WARN] {f.name} has unmatched states; filling seats=0 for missing states.")
            merged['seats'] = merged['seats'].fillna(0)

        metrics_df, summary = compute_metrics(merged)
        summary['file'] = f.name
        summaries.append(summary)

        # annexure C: per-state table for this allocation (append a column to identify allocation)
        out_c = metrics_df[['state','population','seats','seats_per_million','rep_ratio','elasticity']].copy()
        out_c['allocation_file'] = f.name
        annexure_c_rows.append(out_c)

        # elasticity summary (Annexure_D)
        elasticity_summaries.append({
            'file': f.name,
            'mean_elasticity': summary['mean_elasticity'],
            'median_elasticity': summary['median_elasticity'],
            'p90_elasticity': float(np.nanpercentile(metrics_df['elasticity'],90)),
            'p10_elasticity': float(np.nanpercentile(metrics_df['elasticity'],10)),
        })

        # MRC vs proportional baseline (Annexure_E) if baseline exists
        if prop_df is not None and f.name != prop_file.name:
            # merge seats_per_million with proportional
            prop_merged = pd.merge(pop_df[['state','population']], prop_df.rename(columns={state_col:'state', seats_col:'seats'})[['state','seats']], on='state', how='left')
            prop_merged['seats'] = prop_merged['seats'].fillna(0)
            prop_calc, _ = compute_metrics(prop_merged)
            # compute relative change in seats_per_million
            # avoid div by zero
            base_spm = prop_calc['seats_per_million'].replace(0, np.nan)
            cur_spm = metrics_df['seats_per_million']
            rel_change = (cur_spm - base_spm) / base_spm.replace(0, np.nan)
            rel_change = rel_change.replace([np.inf, -np.inf], np.nan)
            mrc = float(np.nanmean(np.abs(rel_change)))  # mean relative change (abs)
            mrc_rows.append({
                'file': f.name,
                'mrc_mean_abs_rel_change': mrc
            })

    # write Annexure_C (concatenate)
    annexure_c = pd.concat(annexure_c_rows, ignore_index=True)
    annexure_c.to_csv(out_dir / "Annexure_C_MI_Table.csv", index=False)

    # Annexure_D (elasticity summary)
    annexure_d = pd.DataFrame(elasticity_summaries)
    annexure_d.to_csv(out_dir / "Annexure_D_Elasticity_Summary.csv", index=False)

    # Annexure_E (MRC)
    annexure_e = pd.DataFrame(mrc_rows)
    annexure_e.to_csv(out_dir / "Annexure_E_MRC_Summary.csv", index=False)

    # fairness_indicators summary
    fairness = pd.DataFrame(summaries)
    fairness = fairness[['file','total_seats','total_population','MI_seats_per_million','Gini_seats_per_million','mean_elasticity','median_elasticity','mean_seats_per_million']]
    fairness.to_csv(out_dir / "fairness_indicators.csv", index=False)

    print("Wrote annexures to:", out_dir.resolve())
    print("Files written:", [p.name for p in out_dir.glob("*.csv")])

if __name__ == "__main__":
    main()
