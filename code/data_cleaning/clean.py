#!/usr/bin/env python3
"""
clean.py
- Reads all CSVs in data/raw (or a single infile).
- Converts populations given in crores -> persons (scale default 1e7) if requested.
- Canonicalises state names using docs/states_canonical.csv (mapping file).
- Basic sanity checks and writes cleaned CSVs to data/processed with suffix _clean.csv
Usage:
  python code/data_cleaning/clean.py --infile data/raw/pop_2036.csv --out data/processed --scale 1e7
  python code/data_cleaning/clean.py --indir data/raw --out data/processed --scale 1e7
"""
from pathlib import Path
import argparse
import pandas as pd
import sys

def load_canonical_map(path: Path):
    if not path.exists():
        print(f"Warning: canonical mapping not found at {path}. Proceeding without mapping.")
        return {}
    df = pd.read_csv(path)
    if 'raw' in df.columns and 'canonical' in df.columns:
        return dict(zip(df['raw'].str.strip(), df['canonical'].str.strip()))
    # try common patterns
    if 'state' in df.columns and 'canonical_state' in df.columns:
        return dict(zip(df['state'].str.strip(), df['canonical_state'].str.strip()))
    # fallback: two-column first two cols
    cols = df.columns.tolist()
    if len(cols) >= 2:
        return dict(zip(df[cols[0]].astype(str).str.strip(), df[cols[1]].astype(str).str.strip()))
    return {}

def canonicalise_name(name: str, cmap: dict):
    if pd.isna(name):
        return name
    s = name.strip()
    return cmap.get(s, s)

def process_file(p_in: Path, p_out_dir: Path, cmap: dict, scale: float, force_scale: bool):
    df = pd.read_csv(p_in)
    # try to find a population column
    pop_cols = [c for c in df.columns if c.lower() in ('population','pop','population_total','total_population','persons')]
    if not pop_cols:
        # fallback: numeric column with largest sum
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if not numeric_cols:
            raise ValueError(f"No population or numeric columns found in {p_in}")
        pop_col = max(numeric_cols, key=lambda c: df[c].sum(skipna=True))
    else:
        pop_col = pop_cols[0]

    # try to find a state column
    state_cols = [c for c in df.columns if c.lower() in ('state','state_name','region','unit')]
    if not state_cols:
        # fallback to first non-numeric
        nonnum = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        if not nonnum:
            raise ValueError(f"No state/name-like column found in {p_in}")
        state_col = nonnum[0]
    else:
        state_col = state_cols[0]

    # copy and clean
    out = pd.DataFrame()
    out['state'] = df[state_col].astype(str).str.strip()
    out['population_raw'] = df[pop_col]

    # scale populations if they look like crores or user forces scaling
    sample_mean = pd.to_numeric(out['population_raw'], errors='coerce').dropna().mean()
    need_scale = force_scale or (sample_mean is not None and sample_mean < 1e6)  # if mean < 1e6 maybe in crores
    if need_scale and scale != 1.0:
        out['population'] = pd.to_numeric(out['population_raw'], errors='coerce') * scale
    else:
        out['population'] = pd.to_numeric(out['population_raw'], errors='coerce')

    # canonicalise
    out['state'] = out['state'].apply(lambda x: canonicalise_name(x, cmap))

    # sanity checks
    if out['population'].isna().any():
        print(f"Warning: NaNs in population after conversion for file {p_in.name}")
    if (out['population'] < 0).any():
        raise ValueError(f"Negative population values found in {p_in}")

    # write
    p_out = p_out_dir / (p_in.stem + "_clean.csv")
    out[['state','population']].to_csv(p_out, index=False)
    print(f"Wrote cleaned file: {p_out}")
    return p_out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", help="Single input CSV file (optional). If omitted, --indir is used.")
    ap.add_argument("--indir", help="Input directory with raw CSVs (default: data/raw)", default="data/raw")
    ap.add_argument("--out", help="Output directory for cleaned CSVs (default: data/processed)", default="data/processed")
    ap.add_argument("--canon", help="Canonical mapping CSV (default: docs/states_canonical.csv)", default="docs/states_canonical.csv")
    ap.add_argument("--scale", type=float, default=1e7, help="Scale multiplier (crores->persons = 1e7). Use 1 to leave as-is.")
    ap.add_argument("--force-scale", action='store_true', help="Force applying scale even if mean looks big.")
    args = ap.parse_args()

    p_out_dir = Path(args.out)
    p_out_dir.mkdir(parents=True, exist_ok=True)

    cmap = load_canonical_map(Path(args.canon))

    if args.infile:
        p_in = Path(args.infile)
        if not p_in.exists():
            print(f"ERROR: infile {p_in} not found", file=sys.stderr); sys.exit(1)
        process_file(p_in, p_out_dir, cmap, args.scale, args.force_scale)
    else:
        p_in_dir = Path(args.indir)
        if not p_in_dir.exists():
            print(f"ERROR: indir {p_in_dir} not found", file=sys.stderr); sys.exit(1)
        csvs = list(p_in_dir.glob("*.csv"))
        if not csvs:
            print(f"No CSVs found in {p_in_dir}", file=sys.stderr); sys.exit(1)
        for f in csvs:
            try:
                process_file(f, p_out_dir, cmap, args.scale, args.force_scale)
            except Exception as e:
                print(f"Skipped {f} due to error: {e}")

if __name__ == "__main__":
    main()
