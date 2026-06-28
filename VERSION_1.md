# Version 1, Complete (pilot)

Snapshot of the cost-aware regression-testing prototype for Qiskit transpilation at the end of the
micro-corpus pilot. This marks **v1 complete**: methodology finalized, Phases 0–5 implemented and
validated, event ledger audited.

## What is built (Phases 0–5)
- **Phase 0**, static manifest + instrumentation harness (executed pass stages, CPU-time cost,
  memory, routing); smoke profile.
- **Phase 1**, event table (schema + cohorts + split-group leakage control), mutation engine,
  validation; targeted regression-trigger units (separate category, provenance-tagged).
- **Phase 2**, tiered semantic oracle (exact ≤12q; structural otherwise, memory-safe), quality
  Pareto oracle (pre-declared thresholds), performance Stage-1 screen (exploratory); write-once raw
  artifacts; per-event baseline profiles; ground-truth labels.
- **Phase 3**, five baselines (random, cheapest-first, diversity-only, history-only, change-stage),
  budget-compliant, leakage-safe.
- **Phase 4**, proposed transparent `risk_score` selector (separated `impact_prior` vs
  `oracle_confidence`, ε floor, exploration reserve, cold-start fallback, connectivity-pressure).
- **Phase 5**, metrics (Recall@budget, normalized TTFR, detection@{5,10,20,40}%, AUC), two
  evaluations (Primary CI vs Secondary retrospective), six validity gates.
- **Per-event from-source venv runner** for historical events (generic + targeted paths).

## Decisions locked
- Window: Qiskit 2.x (band 2.1→latest; anchor **2.4.2**); harness Python 3.11; two-layer pinning.
- Cost calibration: **CPU process time** (`time.process_time`); wall-clock secondary.
- Topology feature: connectivity pressure (pre-layout proxy). Stage map **frozen** before held-out.

## Validation status
- **Tests:** 47 passing.
- **Validity gates:** all six PASS (budget compliance, reproducibility, leakage absence, label
  reproducibility, metric correctness, oracle coverage).
- **Pilot metrics (mutation cohort):** proposed ≈ baselines, both > random; per-event + averaged,
  cohorts never pooled. Classified **pilot evidence** (§5.4: 0 verified forward-regression events).

## Event ledger (9 events; cohorts never pooled)
| cohort | events | status |
|---|---|---|
| mutation (quality) | 4 | **verified** (sandbox/Phase 2) |
| fix_boundary | H1 elide-permutations | **rejected** (production-unobservable: property-only fault) |
| fix_boundary | H3 vf2-determinism | blocked (needs noisy Target) |
| fix_boundary | H5 vf2-panic (functional) | blocked (not run) |
| forward_regression | H4 vf2postlayout-noop | blocked (perf below screen; exploratory) |
| fix_boundary | H2 final-layout | blocked (not run) |

## Key honest finding
Black-box semantic/performance oracles on commodity hardware **under-detect** internal-property,
noise-dependent, and small-overhead transpiler regressions. This motivates: the mutation cohort as a
controlled backbone, the targeted-trigger + retrospective design, and the Phase-6 scale-up with
stronger oracles (property/layout, noisy-Target determinism, 3-run-median perf on controlled
hardware).

## Defects found & fixed during validation
- `--use-targeted` not forwarded by the CLI handler (fixed; regression understood).
- Semantic oracle built a full 2^n operator for large circuits (512 GiB at 18q) → capped exact
  oracle at ≤12q, structural above (fixed; regression test added).
- `labels.json` now derives from the write-once raw artifact (reproducible even for timing fields).

## Reproduce (anchor venv)
```
python -m cart.cli events validate --require-ready
python -m cart.cli ground-truth --unit-limit 8
python -m cart.cli select --baseline all --budget 0.15
python -m cart.cli evaluate --split all
python -m pytest -q
```

## Not in v1 (deferred to Phase 6 / future work)
Scale-up corpus + verified forward regressions; optional ML comparison; property/layout & noisy-
Target oracles; multi-run perf on controlled hardware; native-Windows from-source build hardening.
