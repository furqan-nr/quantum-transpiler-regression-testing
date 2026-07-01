# Reproducibility package, *cart* (Cost-Aware Regression Testing for Qiskit Transpilation)

This archive accompanies the manuscript *"Leakage-Safe Evaluation of Quantum Transpiler
Regression Testing: Oracle Observability, Metadata Faults, and a Cost-Aware Pilot in Qiskit"*
(Quantum Information Processing, Quantum Software Engineering collection).

DOI: https://doi.org/10.5281/zenodo.21020113 · License: MIT (see `LICENSE`).

## What is here

```
src/cart/            the cart prototype (CLI + manifest, events, oracles, labels,
                     selectors, metrics, validity gates)
tests/               automated test suite (incl. the six validity gates)
configs/             frozen, pre-declared configuration:
                       stage_map.yaml, thresholds.yaml, budgets.yaml,
                       cutoff.yaml, seeds.yaml
data/
  events/            audited change-event ledger (events.csv/json, EVENTS_AUDIT.md)
                     with exact candidate/baseline commit SHAs
  manifest_static/   static test-unit manifest + targeted triggers
  profile_baseline/  calibrated per-unit cost profiles
  raw/               write-once raw oracle evidence (per event)
  derived/           labels regenerated from raw evidence
  observability_mining.csv      26 classified Qiskit transpiler bug-fixes
  mining_validation/            two-rater validation:
                       CODEBOOK.md, rater2_sheet.csv, dual_rater_labels.csv,
                       compute_kappa.py
results/             generated evaluation outputs (evaluation.json, analyze runs)
environment/         ENV.md, pinned requirements (requirements.lock + sha256),
                     per-event environment recipes  (the from-source Qiskit
                     builds themselves are NOT shipped; rebuild via SHAs + Rust)
paper/               manuscript (PAPER.docx), draft, figures, build_paper.js,
                     cover letter
METHODOLOGY.md       authoritative research specification (read first)
```

## Install

```bash
python -m pip install -e .            # Python 3.11; or use: PYTHONPATH=src
```

The harness layer is pinned in `environment/requirements.lock`
(`requirements.lock.sha256` records its hash).

## Reproduce the primary (mutation-cohort) results, no Rust needed

```bash
python -m cart.cli manifest                       # static manifest + smoke profile
python -m cart.cli ground-truth --unit-limit 64 --max-qubits 8   # label the 9-operator cohort
python -m cart.cli evaluate                        # detection curves, metrics, six gates
python -m cart.cli analyze                          # ablation + sensitivity
```

Expected headline numbers (mutation cohort, 9 events × 32 units = 288 labels):
mean detection-vs-budget AUC, diversity-only **0.886**, cost/history/change-stage **0.877**,
random median **0.783**, proposed risk_score **0.692** (worst). Removing `impact_prior`
raises the proposed AUC to **0.716** (ablation). All six validity gates PASS.

## Reproduce the mining-study agreement

```bash
python3 data/mining_validation/compute_kappa.py
```

Expected: Cohen's kappa **0.68** (binary observable-by-output-oracle), **0.67** (7-class
channel); both raters independently classify **10/26 = 38%** of fixes as invisible to
output-equivalence oracles.

## Historical events (optional; require a Rust toolchain)

Reproducing the from-source historical regressions (e.g. H1 / ElidePermutations PR #14603)
requires building the per-event Qiskit revisions from source:

```bash
python -m cart.cli historical-run --event hist-elide-permutations-mapping
```

See `environment/ENV.md` and the per-event recipes in `environment/events/`. The built
Qiskit trees are intentionally excluded from this archive; rebuild them from the recorded
`baseline_sha` / `candidate_sha`.

## Notes

- All comparative results are reported as a feasibility pilot; see the manuscript's claim-scope
  rule. The proposed `risk_score` selector is a prototype baseline and does **not** outperform the
  simple baselines at this scale (a reported null result).
- Raw oracle evidence in `data/raw/` is write-once; labels in `data/derived/` regenerate from it.
