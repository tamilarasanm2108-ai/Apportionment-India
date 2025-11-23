# Representation Lab

## Designing a Fair Parliament for India

This repository contains all data, code, and analysis for my working paper:

**“Designing a Fair Parliament: Degressive Proportionality and the Challenge of Federal Representation in India.”**

The project studies how India’s Lok Sabha seats can be allocated fairly using:
- Population projections (2011–2036 and extended 2046–2066)
- Degressive Proportionality (DP)
- Different α values (0.4–1.0)
- Fairness metrics (LHI, Gini, Marginal Representation)
- Multi-cycle simulations (2026 → 2036 → 2046 → 2056 → 2066)

After comparing all models, **α = 0.8** emerges as the most balanced and stable option for India’s long-term federal design.

---

## 📁 Repository Structure

representation/
├─ data/
│ ├─ raw/ # original CSVs and PDFs (unchanged)
│ ├─ processed/ # cleaned datasets
│ └─ outputs/ # model outputs and projections
│
├─ code/
│ ├─ allocation/ # DP alpha models, proportional model
│ ├─ data_cleaning/ # scripts to fix population CSVs
│ ├─ analysis/ # fairness metrics + multi-cycle analysis
│ └─ notebooks/ # exploratory work
│
├─ paper/
│ ├─ ssrn_v0.1.pdf # original working paper
│ ├─ ssrn_v0.2_draft.md # updated version in progress
│ └─ figures/ # plots used in the paper
│
└─ docs/
├─ metadata.md # units, column notes, state list
└─ states_canonical.csv


---

## 🔧 Methods (Short)

- Population data: Registrar General of India + TGPP report  
- Extended projections: exponential/logistic continuation  
- Seat allocation:  
  - Proportional (α = 1.0)  
  - Degressive Proportionality (α = 0.4–0.9)  
  - Largest Remainder (Hamilton)  
- Fairness tests:  
  - Loosemore–Hanby Index (LHI)  
  - Gini of representation  
  - Marginal Representation  
- Outputs include proportional vs DP comparisons for **2036, 2046, 2056**.

---

## 📊 Key Result

**α = 0.8** is the recommended DP parameter because it:
- protects low-growth southern states (TN, KL, AP, TS, KA),
- moderates high-growth states (UP, Bihar) without extreme penalization,
- remains stable across future demographic cycles,
- reduces malapportionment better than α = 0.4–0.6,
- avoids the north-heavy tilt of α = 0.9–1.

---

## 📄 License

- **Code** — MIT License (see `LICENSE`)
- **Data** — CC BY 4.0 (see `LICENSE-data`)
- **Paper & Documentation** — CC BY 4.0 (see `LICENSE-paper`)

---

## 📚 Citation

Arasan (2024). *Designing a Fair Parliament: Degressive Proportionality and Federal Representation in India*.  
SSRN Working Paper.  
(Original uploaded file: `/mnt/data/ssrn-5539498.pdf`)

---

## 🤝 Contributing

Issues, pull requests, and suggestions are welcome.

---

## 📬 Contact

Maintained by **Arasan** (tamilarasanm2108-ai on GitHub)


## Quick run (data -> allocation -> annexures)
1. python code/data_cleaning/clean.py --in data/raw --out data/processed
2. python code/allocation/run_allocations.py --in data/processed --out data/outputs
3. python code/analysis/compute_indicators.py --in data/outputs --out annexures

