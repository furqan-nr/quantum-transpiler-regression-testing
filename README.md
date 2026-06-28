# Cost-Aware Regression Testing for the Qiskit Transpiler (`cart`)

Research prototype and reproducibility package for the paper
**"Leakage-Safe Evaluation of Quantum Transpiler Regression Testing: Oracle Observability,
Metadata Faults, and a Cost-Aware Pilot in Qiskit"**
(*Quantum Information Processing*, Quantum Software Engineering collection).

Given a change to the Qiskit transpiler and a fixed continuous-integration budget, `cart` selects and
orders circuit–backend tests to detect regressions (correctness, circuit-quality, performance) early,
in a setting where the oracle must decide circuit equivalence modulo qubit-layout permutation.

## What this work contributes

1. **A leakage-safe evaluation methodology**, cohort-separated change events, tiered quantum-aware
   oracles with an empirical false-positive rate, CPU-time cost calibration, a frozen change-stage map,
   six implementation-validity gates, and a strict claim-scope rule, together with a
   **fault-manifestation taxonomy** that classifies each regression by the channel through which it
   could be detected.
2. **An oracle-observability analysis**, black-box output-equivalence oracles cannot observe an
   important class of transpiler regression (contract/metadata-channel faults), demonstrated on a
   built-from-source Qiskit regression (H1) and quantified by a two-rater mining study of 26 real
   transpiler fixes.
3. **A prototype (`cart`) and an honest feasibility pilot** on Qiskit 2.x. The proposed `risk_score`
   selector is a *prototype baseline*; at this scale it does **not** outperform the simple baselines or
   random ordering (a reported null result).

## Status, feasibility pilot (final)

- **Primary evaluation:** 9 controlled quality mutations × 32 circuit–backend units = **288 labels** on
  Qiskit `2.4.2`. All six validity gates pass; 57 automated tests pass.
- **Selection result (null):** mean detection-vs-budget AUC, diversity-only **0.886**,
  cost/history/change-stage **0.877**, random median **0.783**, proposed `risk_score` **0.692**.
  Ablation: removing `impact_prior` raises the proposed AUC to **0.716**.
- **Observability:** one built-from-source historical regression (H1, ElidePermutations PR #14603) is
  confirmed invisible to output oracles; the other four historical events are blocked / rejected /
  inconclusive on commodity hardware.
- **Mining study:** 26 Qiskit transpiler bug-fixes, independently double-coded, Cohen's κ = **0.68**
  (bin