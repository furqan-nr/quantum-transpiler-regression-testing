# Cover Letter, Quantum Information Processing (Quantum Software Engineering Topical Collection)

**To:** Guest Editors of the *Quantum Software Engineering* Topical Collection,
Prof. José García-Alonso, Prof. Alejandro Fernández, and Prof. Salvador E. Venegas-Andraca
**Journal:** Quantum Information Processing (Springer)
**Article type:** Original Paper (Topical Collection: Quantum Software Engineering)
**Submission deadline:** 31 July 2026

Dear Guest Editors,

We submit our manuscript, **"Oracle Observability of Quantum Transpiler Regressions: What
Output-Equivalence Oracles Miss in Qiskit, and a Leakage-Safe, Cost-Aware Regression-Testing Pilot,"** for consideration in the
*Quantum Software Engineering* Topical Collection of *Quantum Information Processing*.

**Fit with the collection.** The work falls squarely within the collection's stated scope,
quantum-software *testing, verification, and quality assurance*; *methodologies*; *frameworks and
tools*; *automation of quantum-software production*; *metrics*; and *empirical evaluations*. Its central
question is how often real transpiler regressions escape black-box output-equivalence oracles, and what
CI should assert instead; it also presents a leakage-safe, cost-aware pilot of regression-test selection
for the Qiskit transpiler, where the oracle must reason about circuit equivalence modulo qubit-layout
permutation.

**Contribution and honesty of claims.** We contribute (i) a leakage-safe, cost-aware methodology,
comprising cohort-separated change events, tiered layout-aware oracles, a transparent selector,
detection-curve metrics, six implementation-validity gates, and a fault-manifestation taxonomy; and
(ii) an honest Qiskit 2.x feasibility pilot. We report our findings without overstatement. Our most
concrete empirical finding is an **observability gap**: a **repository-mining study of 26 real
transpiler bug-fixes** (two independent raters, Cohen's κ = 0.68) finds that ≈ 38% lie in channels
invisible to output-equivalence oracles, and we confirm one such case directly on a built-from-source
regression. On the selection task we report a **null result**: over nine controlled mutations and 32
circuit–backend test units (288 labels), the proposed selector shows no advantage over the simple
baselines or random ordering, which an ablation traces to its severity term. We make no
comparative-effectiveness or temporal-generalization claims and frame the study explicitly as a
feasibility study.

**Reproducibility.** A working prototype, frozen configurations, seeds, write-once raw artifacts, and
the exact commands that reproduce every table and figure accompany the paper. The artifact is archived
at https://doi.org/10.5281/zenodo.21020113 (repository: https://github.com/furqan-nr/quantum-transpiler-regression-testing);
see Section 11 and the Statements and Declarations.

**Originality.** This manuscript is original, has not been published previously, and is not under
consideration elsewhere. The authors declare no competing interests. AI-based assistants were used to
support drafting and implementation under the authors' supervision, with all results verified by the
authors (disclosed in the manuscript).

We believe this contribution will be of interest to the collection's readership working on quantum
software testing and quality assurance. Thank you for your consideration.

Sincerely,

**Furqan Nasir** (corresponding author), **Arif Shah**, and **Iftikhar Alam**
¹ City University of Science and Information Technology (CUSIT), Peshawar, Pakistan
² Department of Co