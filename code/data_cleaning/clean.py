#!/usr/bin/env python3
"""
clean.py
- convert crores -> persons (x1e7)
- canonicalise state names using docs/states_canonical.csv
- basic sanity checks, writes cleaned CSVs to output folder
"""
import sys, argparse, pandas as pd
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", dest="out", required=True)
    args=p.parse_args()
    print("Placeholder: implement cleaning pipeline (crores->persons, name canonicalisation)")
if __name__=="__main__":
    main()
