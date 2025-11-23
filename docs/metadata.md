# Metadata — Representation Lab

This file documents the data structure, units, column meanings, sources, and conventions used in the Representation project.

Maintainer: Arasan
Last updated: YYYY-MM-DD

---

## 1. Data Sources

### Population Projections
- Source: Registrar General of India / Technical Group on Population Projections (TGPP)
- File: data/raw/India_Statewise_Populations_2011_2036.csv
- Years included: 2011, 2016, 2021, 2026, 2031, 2036
- Unit: Crores (1 crore = 10 million).
- Unit conversion used in analysis:
  - Crores → Persons (multiply by 10,000,000)

### Historical Population Data
- Files:
  - India_Statewise_Population_1971.csv
  - India_Statewise_Population_1981.csv
  - India_Statewise_Population_1991.csv
  - India_Statewise_Population_2001.csv
  - India_Statewise_Population_2011.csv
- All values: Persons
- States/UT naming varies; canonical mapping applied (see section 3).

### Allocation Files
- Files:
  - dp_alpha_0.4.csv, dp_alpha_0.5.csv, dp_alpha_0.6.csv, dp_alpha_0.8.csv, dp_alpha_0.9.csv
  - dp_alpha_0.4_888.csv, dp_alpha_0.5_888.csv, ...
  - proportional_seats_fixed_543_delim_years_only.csv
  - proportional_seats_888_delim_years.csv
- Units: Seats (integer)
- Method: Largest Remainder (Hamilton)
- Total seats must be either 543 or 888 depending on file.

---

## 2. Column Conventions

### Population Files
| Column | Meaning | Notes |
|--------|---------|-------|
| State/UT or State | Name of state | Will be canonicalised |
| 2011, 2016, ... | Population in crores | Convert to persons |

### Allocation Files
| Column | Meaning |
|--------|---------|
| state | Canonical state name |
| seats | Assigned seats under that model |
| quota | Exact quota before rounding (if included) |

### Processed/Merged Files
| Column | Meaning |
|--------|---------|
| population | Population in persons |
| seats_prop | Proportional allocation (α = 1) |
| seats_dp08 | DP allocation at α = 0.8 |
| seat_change_dp08_vs_prop | DP − proportional |
| seats_per_million | Seats per million persons |

---

## 3. Canonical State Names
All analyses use the following standardized state names:

- Andhra Pradesh
- Arunachal Pradesh
- Assam
- Bihar
- Chhattisgarh
- Goa
- Gujarat
- Haryana
- Himachal Pradesh
- Jammu & Kashmir
- Jharkhand
- Karnataka
- Kerala
- Madhya Pradesh
- Maharashtra
- Manipur
- Meghalaya
- Mizoram
- Nagaland
- Odisha
- Punjab
- Rajasthan
- Sikkim
- Tamil Nadu
- Telangana
- Tripura
- Uttar Pradesh
- Uttarakhand
- West Bengal
- Andaman & Nicobar Islands
- Chandigarh
- Dadra & Nagar Haveli and Daman & Diu
- Delhi
- Lakshadweep
- Puducherry
- Ladakh

Merged/harmonized variants include:
`TAMIL NADU`, `Tamilnadu`, `Tamil Nadu` → Tamil Nadu

---

## 4. Processing Pipeline

### Steps:
1. Load raw population CSVs.
2. Fix malformed rows, strip whitespace, standardize state names.
3. Convert crores → persons.
4. Merge with allocation files.
5. Compute fairness metrics:
   - Loosemore–Hanby
   - Gini of representation
   - Marginal Representation
6. Export outputs to data/outputs/.

---

## 5. Known Issues & Notes

- Raw population CSV contained inconsistent delimiters; fixed in processed version.
- Population projections beyond 2036 are extrapolated, not official.
- Allocation uses Hamilton method with deterministic tie-breaking.
- Reserved seat distributions (SC/ST) not modeled in this version.

---

## 6. Citation

Arasan (2024). Designing a Fair Parliament: Degressive Proportionality and Federal Representation in India. SSRN Working Paper.
