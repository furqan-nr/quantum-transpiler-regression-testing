# Oracle Observability of Quantum Transpiler Regressions

Research prototype and reproducibility package for the paper
**"Oracle Observability of Quantum Transpiler Regressions: What Output-Equivalence Oracles Miss in
Qiskit, and a Leakage-Safe, Cost-Aware Regression-Testing Pilot"**
(submitted to *Quantum Information Processing*, Quantum Software Engineering collection).

**DOI:** [10.5281/zenodo.21020113](https://doi.org/10.5281/zenodo.21020113) ·
**Repository:** https://github.com/furqan-nr/quantum-transpiler-regression-testing

Quantum compilers such as Qiskit's transpiler change constantly, and a single pass modification can
introduce a correctness, circuit-quality, or compilation-performance regression. This work asks **how
often such regressions escape the black-box output-equivalence oracles that CI relies on — and what CI
should assert instead** — and provides an open, leakage-safe harness (`cart`) for studying it.

## What this work shows

1. **An oracle-observability gap (the headline finding).** Across 26 merged Qiskit transpiler bug-fixes,
   **≈ 38% (10/26, Wilson 95% CI [22%, 57%])** lie in channels a black-box output-equivalence oracle
   **cannot** observe — corrupted layout/contract metadata, non-determinism, and dropped global phase.
   Two independent raters agree at Cohen's **κ = 0.68 (95% CI [0.38, 0.97])**. We anchor the measurement
   with a built-from-source case (**H1**, ElidePermutations, PR #14603) that an output oracle cannot
   distinguish from its fix, yet a **fault-class-matched isolated-pass/property oracle detects**. Output
   equivalence is thus an *incomplete* correctness criterion for the transpiler.
2. **A leakage-safe evaluation methodology and harness.** Cohort-separated change events (forward /
   fix-boundary / mutation, never pooled), layout-aware oracles with an empirical false-positive rate
   (**0.068**), CPU-time cost calibration, a frozen change–stage map, six implementation-validity gates,
   a strict claim-scope rule, and a fault-manifestation taxonomy.
3. **A prototype (`cart`, cost-aware regression testing) and an honest feasibility pilot** on Qiskit 2.x,
   including a verified forward-regression event and a **documented null** for the selection study.

## Key results (feasibility pilot)

- **Validity:** all six implementation-validity gates pass; **64 automated tests** pass.
- **Verified forward regression:** **H4** (VF2PostLayout no-op, PR #14120) is confirmed by a multi-run
  Stage-2 performance protocol — candidate slowdown grows with width from ≈ 1.9× (16 q) to > 300× (27 q)
  on symmetric circuits over a large heavy-hex map (Cliff's δ = 1.0).
- **Selection (documented null):** on 9 controlled mutations × 32 units (**288 labels**, Qiskit 2.4.2),
  no selector beats simple baselines or random ordering — mean detection-vs-budget AUC: diversity-only
  0.886, cost/history/change-stage 0.877, random (median) 0.783, proposed `risk_score` 0.692. An ablation
  traces the deficit to the severity term (removing `impact_prior` → 0.716). Selection is reported as an
  explicit feasibility baseline, not a claimed method.

## Reproduce

The mutation pilot reproduces from the anchor environment in two commands (see `REPRODUCE.md`):

```bash
python -m cart.cli ground-truth --unit-limit 64
python -m cart.cli evaluate --split all --random-seeds 20
```

Historical events require per-event from-source Qiskit builds (Rust toolchain; see
`environment/setup/SETUP_WINDOWS.md` and `FORWARD_REGRESSION_PLAN.md`).

## Tooling (`scripts/`)

| Script | Purpose |
|---|---|
| `verify_h4_perf.py` | Multi-run Stage-2 performance confirmation (verifies H4). |
| `verify_h1_isolated.py` | Isolated-pass differential for the property/contract oracle (detects H1). |
| `find_introducing_commit.py` | Locate a regression's introducing commit (pager-free, no bisection). |
| `add_forward_event.py` | Register a forward-regression event in the ledger from a known commit. |
| `mining_stats.py` | Observability stats: Wilson CI + Cohen's κ (with CI) + Fleiss' κ. |

## Repository layout

```
src/cart/            prototype: manifest, events, oracles, selectors, metrics, gates, labels
configs/             frozen thresholds, seeds, cutoff, change–stage map
data/                event ledger, mining dataset, write-once raw oracle artifacts, derived labels
paper/               manuscript (PAPER.docx), cover letter, figures
scripts/             verification + scale-up tooling (table above)
environment/         two-layer env recipes; per-event from-source build scripts
tests/               automated test suite (64 tests)
REPRODUCE.md · METHODOLOGY.md · FORWARD_REGRESSION_PLAN.md · SCALEUP_PROTOCOLS.md · REVISION_TODO.md
```

## Status

Feasibility pilot with a repositioned, review-revised manuscript. The pre-specified scale-up (powered
mining study; property/layout oracle wired into the pipeline; ≥ 3 verified forward regressions) is
documented in `SCALEUP_PROTOCOLS.md` and `REVISION_TODO.md`.

## Citation

See `CITATION.cff`. Artifact archived at [10.5281/zenodo.21020113](https://doi.org/10.5281/zenodo.21020113);
released under the repository's OSI-approved license (`LICENSE`).
