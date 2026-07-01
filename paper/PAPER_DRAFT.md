# Leakage-Safe Regression Testing for Quantum Transpilers
### A Qiskit Feasibility Study of Oracle Observability and Cost-Aware Selection

**Author:** Furqan Nasir¹,²
¹ City University of Science and Information Technology (CUSIT), Peshawar, Pakistan, PhD Student, Computer Science
² Department of Computer Science, National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad, Pakistan, Lecturer
**Corresponding author:** Furqan Nasir, furqannr@gmail.com

**Paper type:** Methodology + feasibility/pilot (empirical software engineering for quantum computing). 

**Keywords:** Quantum software engineering · Quantum transpiler · Regression test selection · Test oracle · Reproducibility · Empirical software engineering

---

## Working notes (not for final manuscript)
- **Source of truth** for the manuscript content; final `.docx` is generated from this file.
- **Honest framing:** pilot/feasibility. Do NOT make headline comparative-effectiveness claims for
  temporal generalization (claim-scope rule §5.4: < 3 verified forward-regression events).
- **Build order:** Related Work → Introduction → Background → Methodology → Implementation →
  Evaluation → Discussion/Threats/Future/Conclusion → Abstract (last).

## Research questions
- **RQ1 (operational soundness of a leakage-safe pipeline).** Can a cost-aware regression-test-selection
  pipeline for Qiskit transpilation be realized so that its anti-leakage controls and reproducibility
  guarantees actually hold under an executable audit, i.e., does it pass a pre-specified suite of
  implementation-validity gates rather than merely being describable on paper?
- **RQ2 (selection effectiveness, pilot).** On a micro corpus, how does the transparent `risk_score`
  selector compare with classical baselines and random selection on detection-curve metrics under a
  fixed budget, and what, if anything, can be concluded at this scale?
- **RQ3 (fault observability).** Of the real historical Qiskit transpiler regressions we attempt to
  reproduce, which become observable through black-box semantic, quality, and performance oracles on
  commodity hardware, and which do not, distinguishing a demonstrated observability gap from cases
  that are merely unreproduced or under-powered at this scale?

---

## 1. Introduction

Quantum software development kits (SDKs) such as Qiskit are under rapid, continuous development, and
their compilers, *transpilers* that lower abstract circuits onto hardware-native gate sets and
limited qubit connectivity, change frequently. A single change to a layout, routing, translation,
optimization, or scheduling pass can introduce a regression of three distinct kinds: a **correctness**
regression (a crash or a circuit that computes a different unitary), a **circuit-quality** regression
(more two-qubit gates or greater depth, which directly lowers fidelity on noisy hardware), or a
**compilation-performance** regression (slower or more memory-hungry compilation). Empirical studies
confirm that compiler/transpiler components are a notable source of defects in quantum platforms
[Paltenghi2022], and recent transpiler bug fixes in Qiskit span exactly these categories.

Catching such regressions early is a regression-testing problem, but the test space is large. The
atomic unit is a tuple *(circuit, backend, transpiler configuration, oracle)*, and a realistic suite
ranges over many circuit families and device topologies; benchmark suites already enumerate on the
order of a thousand workloads per SDK [Benchpress2025]. Re-running the full suite, and its
equivalence oracles, on every change quickly exceeds a practical continuous-integration (CI) budget.

*Motivating scenario.* A developer opens a pull request that modifies a routing heuristic. Most of
the suite is irrelevant to this change, yet a tight PR-tier budget allows only a fraction of tests to
run. Which tests, in which order, maximize the chance of revealing a regression introduced by *this*
change, given that each test's cost (transpilation plus oracle evaluation) varies widely?

Classical regression test prioritization answers precisely this question for conventional software,
and decades of evidence show that cost-, history-, and change-aware heuristics are strong baselines,
often competitive with heavier learned models when labelled failure data are sparse
[Yoo2012,Machalica2019]. Yet, to our knowledge, no prior work formalizes or evaluates *cost-aware
regression test selection for the quantum transpiler*, where faults are compiler regressions and the
oracle must reason about circuit equivalence under qubit-layout permutation. Existing quantum-testing
work targets bug finding and test generation via metamorphic or differential testing [MorphQ2023,
MorphQpp2024], or SDK benchmarking [Benchpress2025], complementary to, but distinct from, budgeted
selection of existing tests for an incoming change.

This paper contributes a methodology and an honest feasibility pilot, not a large-scale empirical
verdict. Concretely:

1. **A leakage-safe, cost-aware methodology** for regression test selection in quantum transpilation,
   comprising a change-event model with explicitly separated cohorts (forward regression, fix-boundary
   differential, mutation), tiered quantum-aware oracles (semantic, circuit-quality, exploratory
   performance) with an *empirical* false-positive rate, a transparent and interpretable `risk_score`
   selector that separates fault severity from detection confidence, five classical baselines, and
   detection-curve metrics suited to one fault per event.
2. **Strict anti-leakage controls** rarely combined in one design: group-level temporal splitting,
   CPU-time cost calibration, a frozen change–stage map, and a test-provenance rule that keeps
   post-fix tests out of the primary CI claim, together with six implementation-validity gates.
3. **A prototype (`cart`)** realizing the methodology end to end (artifact statement, Section 11) and a
   **feasibility pilot on Qiskit 2.x** with an audited event ledger, reporting two honest outcomes: a
   **null selection result** (no selector, including the proposed one, beats simple baselines or random
   at this scale) and a **single demonstrated observability gap** (a real historical regression that
   black-box output oracles cannot see), both of which motivate the design and the planned scale-up.

We answer three research questions: **RQ1** (is the leakage-safe pipeline operationally sound under an
executable gate audit?), **RQ2** (how does the transparent selector compare with baselines and random
at this scale, and what can be concluded?), and **RQ3** (which real historical transpiler regressions
are observable through black-box oracles on commodity hardware, and which are merely unreproduced?).
We deliberately scope all comparative claims as pilot evidence.

The remainder of the paper is organized as follows. Section 2 gives background; Section 3 surveys
related work; Section 4 presents the methodology; Section 5 describes the implementation; Section 6
reports the pilot evaluation; Sections 7–9 discuss findings, threats, and limitations and future
work; Section 10 concludes.

## 2. Background

### 2.1 The Qiskit transpiler
Qiskit compiles an abstract quantum circuit to a target backend through a staged pass manager
[Qiskit2024]. The canonical stages are **layout** (assign virtual qubits to physical qubits),
**routing** (insert SWAPs so two-qubit gates act on physically adjacent qubits), **translation**
(rewrite gates into the backend's native basis), **optimization** (peephole cancellation, gate
merging, resynthesis), and **scheduling** (timing/idle handling). A preset pass manager bundles these
at optimization levels 0–3. Two properties matter for testing: the actually executed passes depend on
the circuit, backend, configuration, and the exact Qiskit revision (so they must be *observed*, not
inferred from source); and transpilation may permute qubits, so a transpiled circuit equals the
original only modulo a layout permutation.

### 2.2 Transpiler regression types and their manifestation
We separate *what kind of defect a regression is* from *how (and whether) it manifests in an
observable signal*, because the gap between the two is the pilot's central finding. The reported
**fault-type** grouping is the conventional one: **functional** (compilation failure: crash,
exception, or structurally invalid output) and **semantic** (the transpiled circuit computes a
different unitary/output) form the *correctness* group; **circuit quality** (worse two-qubit-gate
count or depth) is the *quality* group; and **compilation performance** (slower or more memory-hungry
compilation) is the *performance* group. A crash is not necessarily a semantic fault, and a 10%
increase in two-qubit gates is not necessarily a quality regression if depth improves substantially,
so quality is judged by a Pareto rule over pre-declared thresholds, with both metrics reported
separately.

Crucially, two regressions of the *same* fault type can manifest in very different observable signals,
and some manifest in signals that a black-box, output-only oracle never inspects. We therefore use a
**fault-manifestation taxonomy**, the channel through which a regression could be detected:

| Manifestation channel | Observable signal | Black-box output oracle sees it? |
|---|---|---|
| `output_semantic` | transpiled circuit computes a different unitary/output state | Yes (within oracle width limits) |
| `compilation_failure` | crash, exception, or structurally invalid circuit | Yes |
| `circuit_quality` | worse two-qubit-gate count or depth | Yes |
| `performance` | slower or more memory-hungry compilation | Yes, if overhead exceeds the screen |
| `transpiler_contract_or_metadata` | incorrect internal property/contract (e.g. `TranspileLayout`, `final_layout`, `routing_permutation`) while the applied output stays correct | **No**, invisible to output-only oracles |
| `determinism_or_reproducibility` | output varies across fixed-seed runs, often only under a specific (e.g. noisy) target | **Only** with a determinism oracle exercising that target |

This taxonomy is what makes the historical results in Section 6.4 interpretable: a regression can be
entirely real yet sit in a manifestation channel our black-box pipeline does not observe. In
particular, the ElidePermutations regression (H1) manifests as `transpiler_contract_or_metadata`
(a corrupted layout property, not a wrong output unitary), and the VF2Layout regression (H3) manifests
as `determinism_or_reproducibility` under a noisy target, neither of which is a `circuit_quality` or
`output_semantic` signal, so a "pass" from the output oracle is expected and is **not** evidence that
the oracle under-detects quality or semantic faults.

### 2.3 The oracle problem for transpilation
Deciding whether a transpiled circuit is correct is an instance of the quantum oracle problem
[QSTSurvey2024], the central obstacle catalogued in the general test-oracle survey [Barr2015]. For small, unitary-pure circuits one can compare unitaries modulo global phase, with
the transpiled circuit's layout normalized before comparison; this is exact but infeasible at scale,
since an n-qubit operator has 2^n × 2^n complex entries (a 30-qubit statevector alone is ~16 GB).
Larger or non-unitary circuits therefore require sampled-statevector, observable, metamorphic, or
structural checks [MorphQ2023]. A practical consequence, central to our findings, is that
black-box equivalence oracles observe the *output*, so a fault that corrupts internal metadata (for
example, a layout property) while leaving the output unitary intact can be invisible to them.
Dedicated quantum equivalence-checking methods exploit reversibility and simulation to compare a
circuit before and after compilation efficiently [Burgholzer2021], but they too reason about the
output map rather than internal transpiler contracts.

### 2.4 Rate-of-detection metrics
Prioritization is classically measured by the Average Percentage of Faults Detected (APFD) and its
cost-cognizant variant APFDc, which weights detection by test cost and fault severity [Elbaum2002,
Elbaum2001]. APFDc, however, assumes multiple faults exposed by a single common ordering. In our
setting each change event typically has a single fault under its own per-event ranking, so APFDc is
inapplicable as a headline metric; we instead use per-event detection-curve summaries (Recall@budget,
time-to-first-regression, detection rate at fixed budget fractions, and area under the
detection-vs-budget curve), averaged across events, with cohorts reported separately.

## 3. Related Work

We position the work across three threads, classical regression test prioritization, learning-based
test selection, and quantum software/compiler testing, and close each by stating the gap our study
addresses.

### 3.1 Regression test selection and prioritization (RTP)
Regression test selection and prioritization reorder or sub-select tests so that faults are revealed
earlier under a budget. Rothermel et al. introduced systematic test-case prioritization and the rate
of fault detection [Rothermel2001]; Elbaum et al. established APFD and a family of empirical studies
[Elbaum2002]; and the cost-cognizant variant APFDc incorporates varying test costs and fault
severities [Elbaum2001], which is the conceptual ancestor of our cost-aware objective. Yoo and
Harman survey the field comprehensively and observe that change-, history-, and cost-aware heuristics
are persistently strong, robust baselines [Yoo2012]. In continuous-integration settings specifically,
lightweight selection and prioritization that avoid coverage instrumentation are markedly more
cost-effective [Elbaum2014], and a large empirical study of readily-available CI and version-control
metadata finds that simple, well-known heuristics frequently outperform complex machine-learned models
[Elsner2021], a result that directly informs our choice of a transparent selector and our cautious
reading of the pilot. Two adaptations are required before this body of
work transfers to quantum transpilation: (i) the "fault" is a *compiler regression* spanning
correctness, circuit quality, and compilation performance rather than a test failure in the program
under test; and (ii) the oracle must decide quantum-circuit equivalence modulo qubit-layout
permutation. We retain the cost-aware objective and the strong classical baselines, but redefine the
fault model, oracles, and metrics accordingly.

### 3.2 Learning-based test selection
At industrial scale, predictive (learned) test selection trains gradient-boosted models on large
histories of test outcomes and can halve testing cost while retaining most failure signal
[Machalica2019]. Such methods, however, are data-hungry: they presuppose a large, labelled corpus of
historical pass/fail outcomes per test, which does not yet exist for quantum-transpiler regressions.
A broad literature applies reinforcement learning [Spieker2017], multi-armed bandits for volatile test
pools [PradoLima2022], and other learners surveyed systematically [Pan2022] to CI test prioritization;
these consistently require substantial historical signal, reinforcing our staged plan. Consistent with
the RTP literature's finding that simple cost/history/change-aware heuristics are
competitive under sparse data [Yoo2012], we deliberately propose a *transparent, interpretable*
selector first and reserve a learned comparison for a future scale-up with sufficient events, under
identical anti-leakage rules.

### 3.3 Quantum software and compiler testing
Quantum software testing must contend with the oracle problem, the expected output of a quantum
program is often unknown or expensive to compute [QSTSurvey2024]. Metamorphic and differential
testing mitigate this: MorphQ generates diverse quantum programs and applies quantum-specific
metamorphic relations to test the Qiskit platform, exposing real bugs [MorphQ2023], and MorphQ++
reproduces and extends metamorphic testing of quantum compilers [MorphQpp2024]. Empirical studies of
bugs in quantum computing platforms document that compiler/transpiler components are a significant
source of defects [Paltenghi2022]. Benchpress provides a large, SDK-agnostic benchmark of circuit
construction, manipulation, and compilation workloads, enabling performance and behaviour comparison
across SDKs [Benchpress2025].

Recent quantum-specific testing frameworks sharpen the picture. QuCheck provides property-based
testing of quantum programs in Qiskit, with flexible generators, assertions, and preconditions, and is
evaluated by mutation analysis [QuCheck2025]; a related line applies delta-debugging to property-based
*regression* testing of quantum programs. QEMI adapts Equivalence-Modulo-Inputs compiler testing to
quantum software stacks, generating program variants by removing dead code and uncovering crash and
behavioural bugs across Qiskit, Q#, and Cirq [QEMI2026]. These are powerful **fault-finding** and
**test-generation** tools; like MorphQ they create or transform programs to expose defects rather than
select among an existing budgeted suite. Differential testing of quantum software stacks (QDiff)
explores semantics-preserving program variants and filters circuits by static characteristics to
compare Qiskit, Cirq, and Pyquil [QDiff2021]; QSPE enumerates skeletal program variants with
statevector-based validation and reports 81 Qiskit miscompilations acknowledged by developers
[QSPE2026]; and concolic testing targets transpiler decision points, parameter thresholds and layout
heuristics, surfacing missed optimizations and semantic deviations in Qiskit passes [Concolic2025].
Complementary formal approaches verify the compiler directly: Giallar provides push-button verification
of Qiskit passes, verifying 44 of 56 passes across 13 versions and uncovering three bugs [Giallar2022].
Static analysis and bug benchmarks round out the picture, with LintQ detecting quantum-specific defects
that general linters miss [LintQ2024] and Bugs4Q curating real, reproducible Qiskit bugs [Bugs4Q2023].

These efforts target *bug finding* and *test generation* (creating new programs that crash or violate
relations), or *benchmarking* (measuring SDK performance). They do not address the complementary CI
problem we study: given a concrete transpiler change and a fixed budget, *select and order existing
tests* to detect the change's regression earliest, with quantum-aware oracles, cohort-separated
change events, CPU-time cost calibration, and leakage-safe temporal evaluation. To our knowledge,
cost-aware regression test selection for the quantum transpiler has not previously been formalized or
piloted. We use Benchpress-style generic workloads for breadth and add small, provenance-tagged
targeted triggers (drawn from fixes' own regression tests) solely for fault observability, kept
strictly out of the primary CI evaluation.

### 3.4 Positioning

Table 5 contrasts the closest threads along the axes that matter for budgeted CI of a compiler. The
distinguishing combination of our work is the rightmost five columns taken *together*: a quantum-aware
oracle applied to *selecting and ordering existing tests* under an explicit cost budget, with
leakage-safe temporal evaluation and cohort separation. Individually, each property appears somewhere
in prior work; in combination, for the quantum transpiler, it does not.

**Table 5. Positioning relative to prior work (○ = no/not applicable, ◐ = partial, ● = yes).**

| Approach | Primary goal | Quantum-aware oracle | Cost/budget-aware | Selects & orders *existing* tests | Leakage-safe temporal eval | Cohort separation |
|---|---|:--:|:--:|:--:|:--:|:--:|
| Classical RTP/TCP [Rothermel2001, Elbaum2002, Elbaum2001, Yoo2012] | prioritize tests of a program | ○ | ● | ● | ◐ | ○ |
| Predictive test selection [Machalica2019] | learned test selection at scale | ○ | ● | ● | ● | ○ |
| MorphQ / MorphQ++ [MorphQ2023, MorphQpp2024] | metamorphic bug finding | ● | ○ | ○ | ○ | ○ |
| QuCheck [QuCheck2025] | property-based testing | ● | ○ | ○ | ○ | ○ |
| QEMI [QEMI2026] | EMI stack bug finding | ● | ○ | ○ | ○ | ○ |
| Benchpress [Benchpress2025] | SDK compilation benchmarking | ◐ | ○ | ○ | ○ | ○ |
| **This work** | **cost-aware regression test *selection* for the transpiler** | **●** | **●** | **●** | **●** | **●** |

## 4. Methodology

### 4.1 Problem formulation
Given a transpiler change and a fixed per-event CI budget B (in seconds), select and order
circuit–backend tests to maximize early detection of regressions. Conceptually, each candidate test
is scored by an expected value
*expected_value ≈ P(regression | change, circuit, backend) × impact ÷ expected_cost*,
and tests are chosen greedily within B. P(·) is the conceptual target; the proposed selector realizes
it with a transparent surrogate (Section 4.5), reserving a calibrated estimator for future learned
comparison. The primary evaluation unit throughout is the (event_id, test_id) pair.

### 4.2 Change-event model and cohorts
The dataset unit is a **change event**, not a commit: *event = (baseline_revision, candidate_revision,
change_metadata, fault_id)*, each with a unique fault_id and a fault_type. Running tests on every
commit is wasteful because most commits contain no regression. Each event declares a cohort, and the
three cohorts are reported separately and never pooled:

- **forward_regression**, baseline = last known-good parent, candidate = regression-inducing commit;
  the only cohort that models the real CI question. `change_metadata_sha` = candidate.
- **fix_boundary_differential** (reverse orientation), used when the introducing commit is not
  traced: baseline = fix commit (fault absent), candidate = the fix's parent (fault present);
  `change_metadata_sha` = fix commit. A fault-revealing differential, *not* a forward regression, and
  never described as CI prediction of an incoming change.
- **mutation**, a controlled single-fault injection on a base revision, used only to fill missing
  fault-type coverage; historical events are preferred over mutations.

Event dates follow the cohort (forward: candidate timestamp; fix-boundary: fix timestamp; mutation:
base-revision timestamp), driving the temporal split (Section 4.9).

### 4.3 Test units, manifest, and provenance
A test unit is *(circuit, backend, transpiler_configuration, oracle)*. A static manifest records pure
metadata (circuit family, width, backend, declared stages, oracle type); a separate calibrated
profile records *measured* baseline cost, executed pass stages (via pass-manager instrumentation, not
filename inference), routing observations, and peak memory, keyed by (event_id, baseline_sha,
test_id, event_environment_id) because these differ per event baseline. Each unit also declares
**provenance**: `pre_existing` (e.g., generic Benchpress workloads), `extracted_from_fix`, or
`synthesized`, with a flag `available_before_candidate`. This supports two evaluations (Section 4.9):
a Primary CI evaluation over tests available before the candidate, and a Secondary retrospective
evaluation that may include post-fix targeted triggers.

### 4.4 Oracles
**Semantic.** Tiered by applicability and width: exact unitary equivalence modulo global phase for
small (≤ 12-qubit), unitary-pure, ancilla-free circuits, with the transpiled circuit's layout
normalized before comparison; structural validity (basis compliance and coupling-map adherence)
otherwise. A full 2^n operator is never materialized for large circuits (memory-safe). This mirrors
dedicated quantum equivalence-checking practice, which compares the maps of pre- and post-compilation
circuits and exploits reversibility and simulation to stay tractable [Burgholzer2021]. Sampled-
statevector checks for the intermediate range are a documented future extension.

**Quality.** A Pareto rule over pre-declared thresholds: a quality regression holds if two-qubit-gate
count worsens materially while depth does not improve materially, or vice versa. Δ two-qubit count
and Δ depth are reported separately; thresholds are fixed before held-out evaluation and a sensitivity
grid is reported.

**Performance.** A two-stage protocol, Stage 1 screens median slowdown against a pre-declared
threshold; Stage 2 (suspected regressions only) uses robust effect sizes. On a single laptop,
performance is treated as **exploratory** and timing uses CPU process time for stability.

**Empirical false-positive rate.** A regression warning counts as a false positive only if it is not
upheld by independent confirmation (a stronger oracle or a metamorphic/re-run cross-check), never
merely because some oracle fired; the FP rate is computed over confirmed-vs-unconfirmed warnings.

### 4.5 The proposed transparent selector (risk_score)
The proposed selector introduces no machine-learning model and outputs an interpretable score, not a
calibrated probability:

> risk_score(test | event) = (ε + change_stage_match) × circuit_backend_sensitivity × impact_prior ×
> oracle_confidence ÷ expected_cost × novelty_multiplier

Design rationale: fault **severity** (`impact_prior`: circuit criticality × topology stress ×
history-conditioned impact) and detection **confidence** (`oracle_confidence`: stronger oracle ⇒
higher) are *separate* multiplicands, so a high-impact test using a weaker oracle is not
double-penalized. The ε floor and a 10–20% stage-independent **exploration reserve** prevent an
incomplete change–stage map from zeroing useful tests; unknown or framework-wide changes route into
the reserve. A neutral **cold-start fallback** (history-conditioned impact = 1.0) applies when no
prior qualifying events exist. The selector consumes only pre-execution information; the candidate's
fault_type, runtime, quality metrics, and labels are never inputs (Section 4.9).

### 4.6 Baselines
Five baselines observe the same per-event budget: **random** (seeded uniform), **cheapest-first**
(ascending baseline cost), **diversity-only** (greedy coverage over circuit family × topology),
**history-only** (descending historical failure rate from prior events), and **change-stage
heuristic** (prefer tests exercising the modified pass stage). These instantiate the strong classical
families identified in the RTP literature [Yoo2012].

### 4.7 Budgeted selection
Selection (proposed and baselines) reserves 10–20% of the budget for stage-independent exploration,
fills the main allocation greedily by score, fills the reserve by sensitivity/novelty alone, enforces
≥ 1 representative per circuit family where the budget permits, never exceeds the budget, and is
seed-deterministic (same seed ⇒ identical ranking).

### 4.8 Metrics
Per event and averaged, with cohorts/sources separated: **Recall@budget**, **normalized TTFR** (time
to first detected regression ÷ full-suite time), **detection rate at {5, 10, 20, 40}% budget**, **area
under the detection-vs-budget curve**, **selection overhead**, **diversity coverage**, and the
**empirical oracle FP rate**. APFDc is reported only for the atypical case of multiple independent
faults under one ordering.

### 4.9 Anti-leakage controls
- **Group-level temporal split.** training: event_date < cutoff; test: event_date ≥ cutoff. Applied at
  `split_group_id` = base_revision + mutation_family; a group straddling the cutoff goes wholly to
  test, preventing near-duplicate mutation variants from leaking across the boundary.
- **Provenance / two evaluations.** The Primary CI evaluation restricts candidates to
  `available_before_candidate = true`; post-fix targeted triggers (`extracted_from_fix`) are confined
  to a Secondary retrospective evaluation and never enter the headline claim.
- **Frozen change–stage map.** The module→stage mapping is frozen before held-out evaluation;
  refinement uses training events only and is versioned.
- **CPU-time cost calibration.** Cost uses `time.process_time` (stable on a shared laptop); wall-clock
  is recorded only as a secondary reference.
- **Selector input restriction.** The selector may use only candidate change metadata, static test
  metadata, baseline-version costs, and historical data strictly before `event_date`; never candidate
  runtime, quality, or labels.

### 4.10 Implementation-validity gates and claim scope
Six gates must pass before any result is reported, verifying *implementation correctness*, not
outcomes: budget compliance, reproducibility (same seed ⇒ same ranking), leakage absence (injecting a
current-event outcome must not change any ranking), label reproducibility from write-once raw
artifacts, metric correctness against ≥ 2 hand-computed cases, and oracle coverage. A **claim-scope
rule** forbids a headline comparative-effectiveness claim for temporal generalization when fewer than
three forward_regression events are verified in the held-out cohort; results are then reported per
event and classified as pilot evidence. Whether the proposed selector beats the baselines is the
empirical result of the study, never a precondition for reporting.

## 5. Implementation

The methodology is realized in an open Python prototype, `cart`, organized by phase: `manifest`
(static manifest + instrumented profiling), `events` (event table, cohorts, mutation engine,
validation), `oracles` (semantic, quality, performance), `labels` (ground-truth + per-event runner),
`selectors` (baselines, the `risk_score` selector, cost model, context), `metrics`, and `gates`. A
command-line interface exposes `manifest`, `events`, `ground-truth`, `select`, `evaluate`, and
`historical-run`. Figure 1 shows the pipeline over its shared reproducibility substrate.

**Two-layer environment.** Reproducing historical regressions requires building *different* Qiskit
revisions, which is incompatible with a single pinned Qiskit. We therefore separate a fixed **harness
layer** (Python 3.11, Benchpress, the oracle/measurement stack, pinned via a lockfile) from a
**Qiskit-under-test layer** built from source per event. Instrumentation and the development/test
environment anchor on Qiskit 2.4.2 within the 2.x release window; building from source requires a
Rust toolchain.

**Per-event from-source runner.** For historical events, a runner builds the baseline and candidate
revisions into isolated virtual environments and executes a worker inside each (as a subprocess);
each worker transpiles the test units with its own Qiskit, serializes outputs (QPY) and CPU timings,
and the harness loads both back and applies the shared oracle pipeline. This keeps the system-under-
test isolated while reusing one oracle implementation across all cohorts.

**Reproducibility artifacts.** Raw oracle evidence is written **write-once** under
`data/raw/<event>/<test>/`; derived labels are regenerated from these artifacts so they reproduce
exactly, including for timing-dependent fields. Per-event environment recipes, RNG seeds, pre-declared
thresholds, the frozen stage map, and per-run frozen configurations are committed. The prototype ships
with an automated test suite and the six validity gates wired into `evaluate`.

**What is implemented versus exercised in this pilot.** To avoid over-stating coverage, we separate
the three states explicitly.

- *Implemented and exercised in the pilot's primary results:* the static manifest and instrumented
  profiling; the mutation engine (four semantics-preserving quality operators); the tiered semantic
  oracle (exact unitary ≤ 12 qubits, structural above); the quality Pareto oracle; the five baselines
  and the proposed `risk_score` selector; budgeted selection; the metric suite (Recall@budget,
  normalized TTFR, detection@{5,10,20,40}%, AUC); the six validity gates; and the held-out evaluation
  on the nine-event × 32-unit (288-label) mutation cohort.
- *Implemented but not part of the primary results:* the per-event from-source historical runner (used
  to attempt H1, H3, and H4, which are respectively rejected, blocked, and blocked); the
  targeted-trigger units and the Secondary retrospective evaluation; the exploratory performance
  Stage-1 screen; and the `incomplete_basis_translation` functional-fallback operator.
- *Specified but deferred (not implemented in this pilot):* the sampled-statevector oracle tier
  (13–22 qubits); a property/layout (contract/metadata) oracle; a noisy-target determinism oracle;
  three-run-median performance on controlled hardware; performance Stage 2; and any learned selector.

## 6. Evaluation

We evaluate the three research questions on a micro corpus, on a single 16 GB laptop, anchored on
Qiskit 2.4.2.

### 6.1 Corpus and setup
The corpus has **fourteen change events** (Table 1): nine controlled quality mutations on the 2.4.2 base
(disable-optimization-loop, drop-VF2PostLayout, downgrade-routing, insert-redundant-CX,
drop-optimization-stage, force-opt-level-1, force-opt-level-0, downgrade-layout-trivial,
insert-redundant-X) and five
historical Qiskit transpiler regressions identified from fix pull requests, each with exact
candidate/baseline commit SHAs. Tests comprise generic circuit families (GHZ, QFT, linear QAOA,
random Clifford) over line and heavy-hex backends for breadth, plus small **targeted regression-
trigger** circuits drawn from each fix's own regression test for fault observability; targeted units
are `extracted_from_fix` and therefore excluded from the Primary CI evaluation. Quality thresholds,
seeds, and the stage map are pre-declared/frozen before evaluation.

**Table 1. Audited event ledger (cohorts never pooled).**

| Event(s) | Cohort | Fault type | Status |
|---|---|---|---|
| 4 mutation operators | mutation | quality | verified (pilot) |
| H4 VF2PostLayout no-op (#14120) | forward_regression | performance | blocked (perf below screen) |
| H1 ElidePermutations (#14603) | fix_boundary | semantic | rejected (production-unobservable) |
| H3 VF2Layout determinism (#14730) | fix_boundary | quality | blocked (needs noisy target) |
| H2 final_layout composition (#14919) | fix_boundary | semantic | blocked (not run) |
| H5 VF2Layout panic (#16285) | fix_boundary | functional | blocked (not run) |

**Table 4. Controlled mutation operators and targeted regression triggers used in the pilot.**

| Name | Kind | Stage / target | Fault type | Effect / oracle |
|---|---|---|---|---|
| disable_optimization_loop | mutation | optimization | quality | removes the iterative peephole/cancellation loop → residual redundancy |
| drop_vf2_post_layout | mutation | layout/optimization | quality | omits VF2PostLayout → worse layout (more SWAPs) |
| downgrade_routing | mutation | routing | quality | forces 'basic' routing → more 2Q/depth on routing-needing circuits |
| insert_redundant_cx_pair | mutation | optimization | quality | appends a CX–CX identity pair → +2 two-qubit gates (semantics preserved) |
| incomplete_basis_translation | mutation (fallback) | translation | functional | drops the 1q basis → natural TranspilerError |
| trig-h1-elide-permutations | targeted (extracted_from_fix) | ElidePermutations | semantic | PermutationGate + swaps; semantic oracle |
| trig-h2-final-layout-composition | targeted (extracted_from_fix) | routing final_layout | semantic | identity-after-routing; semantic oracle |
| trig-h3-vf2-all-1q | targeted (extracted_from_fix) | VF2Layout | quality | all-1q circuit; determinism (property) oracle |

**Test corpus.** To stay within a single 16 GB laptop the corpus is width-capped at 8 qubits,
enumerating 4 circuit families × 2 widths × 2 backend topologies × 2 optimization levels = **32 test
units** (Table A); every unit lies within the exact-unitary oracle tier. The Primary CI evaluation
runs on the **verified mutation cohort**, nine operators × 32 units = **288 (event, test) labels**,
because the five historical events require per-event from-source builds and are reported separately in
the audit below (Table C). All nine operators have `intended_mutation_target = quality`; **eight of the
nine are detected** by the black-box oracle on this corpus (only `drop_vf2_post_layout` is not), and
because a quality-targeted mutation can still surface other observable labels we distinguish
`intended_mutation_target` from `observed_test_unit_label`. The **primary-CI eligibility rule (§4.9) is
implemented and exercised synthetically on this mutation cohort; it is not yet validated on a real
forward-regression event**, because none is verified. Thresholds, seeds, and the stage map are
pre-declared/frozen before evaluation, and no selector parameter was tuned on any of the nine events.

**Table A. Test corpus composition (32 units; width-capped at 8 qubits to keep compute low).**

| Dimension | Values | Count |
|---|---|---|
| Circuit family | GHZ, QFT, linear-QAOA, random-Clifford | 4 |
| Width (qubits) | 5, 8 | 2 |
| Backend topology | linear, heavy-hex | 2 |
| Optimization level | 1, 3 | 2 |
| **Total units** | | **32** |
| Semantic oracle tier | exact-unitary (all widths ≤ 12) | 32 units |

**Table B. Mutation ledger, verified cohort (9 operators × 32 units = 288 labels).** "Detected?" is
whether the black-box oracle pipeline flagged the operator on any unit; "best-selector AUC" is the
per-event area under the detection-vs-budget curve for the best selector. 8 of 9 operators are detected.

| Operator | Target stage | Fault type | Semantics preserved | Detected? | Best-selector event AUC |
|---|---|---|:--:|:--:|:--:|
| disable_optimization_loop | optimization | quality | yes | yes | 0.98 |
| drop_vf2_post_layout | layout / optimization | quality | yes | **no** | 0.00 |
| downgrade_routing | routing | quality | yes | yes | 1.00 |
| insert_redundant_cx_pair | optimization | quality | yes | yes | 1.00 |
| drop_optimization_stage | optimization | quality | yes | yes | 1.00 |
| force_opt_level_1 | optimization | quality | yes | yes | 1.00 |
| force_opt_level_0 | optimization | quality | yes | yes | 1.00 |
| downgrade_layout_trivial | layout | quality | yes | yes | 1.00 |
| insert_redundant_x_pair | optimization | quality | yes | yes | 1.00 |

**Table C. Historical-event audit (5 events; none verified through the black-box oracles in this
pilot). Manifestation channel per the Section 2.2 taxonomy.**

| ID (PR) | Cohort | Fault type | Manifestation channel | candidate→baseline (short SHA) | Status | Reason |
|---|---|---|---|---|---|---|
| H1 ElidePermutations (#14603) | fix_boundary | semantic | transpiler_contract_or_metadata | 7c3890da→96fda188 | **rejected** | built from source; real fault corrupts `virtual_permutation_layout`, not the output unitary → production-unobservable |
| H2 final_layout (#14919) | fix_boundary | semantic | transpiler_contract_or_metadata (expected) | 14df5941→dfcc5c6c | not run | expected to share H1's layout-property masking |
| H3 VF2Layout determinism (#14730) | fix_boundary | quality | determinism_or_reproducibility | 056c6413→d33ef533 | blocked | non-determinism tied to a noisy `Target` absent from our coupling-map backend |
| H4 VF2PostLayout no-op (#14120) | forward_regression | performance | performance | a18e1516→a8d23667 | blocked | overhead below the 20% Stage-1 screen; single-sample timing under-powered |
| H5 VF2Layout panic (#16285) | fix_boundary | functional | compilation_failure | f0fae6f3→0b2cdf2b | not run | input-specific crash; not yet reproduced |

### 6.2 RQ1, Feasibility and rigor
The full pipeline (Phases 0–5) was constructed and runs end to end. **All six implementation-validity
gates pass** (Table 2) and the prototype passes 57 automated tests, including hand-computed metric
checks and a leakage-invariance check. Two genuine defects were found and fixed during validation,
a command-line flag that silently dropped the targeted-run mode, and a semantic oracle that attempted
to materialize a 2^18 operator (~512 GB) on an 18-qubit circuit (now capped, with a regression test).
We answer RQ1 affirmatively: a leakage-safe, cost-aware selection pipeline for Qiskit transpilation is
feasible and passes the validity gates.

**Table 2. Implementation-validity gates.**

| Gate | Result |
|---|---|
| Budget compliance | PASS |
| Reproducibility (same seed ⇒ same ranking) | PASS |
| Leakage absence (current-event outcome cannot change ranking) | PASS |
| Label reproducibility from raw artifacts | PASS |
| Metric correctness vs hand-computed cases | PASS |
| Oracle coverage | PASS |

### 6.3 RQ2, Selection effectiveness (pilot): a null result
On the verified mutation cohort (nine events, 32 units each), **no selector, including the proposed
`risk_score`, improved on the simple deterministic baselines or on random ordering**; the proposed
selector clearly trailed them (Tables 3a–3e, Figure 4). Diversity-only attains the best mean AUC
(0.886), the cost/history/change-stage selectors tie at 0.877, random over 20 seeds reaches a median
of 0.783 (seed range 0.613–0.854), and the proposed selector is lowest at 0.692. The deficit is not
merely noise: against diversity-only the effect size is small and negative (Cliff's δ = −0.30,
Vargha–Delaney Â₁₂ = 0.35), and against the cost baselines and random it is negligible (|δ| ≤ 0.07);
bootstrap 95% CIs are wide and overlapping (proposed 0.692 [0.400, 0.912]).

The per-event view (Tables 3b, 3d) explains the aggregate. Eight of the nine mutations are detected,
most at near-zero cost by every selector. The proposed selector reaches the detector marginally earlier
on six events but loses heavily on the two redundancy mutations (`insert_redundant_cx_pair` and
`insert_redundant_x_pair`, per-event AUC 0.20 and 0.21) and on `force_opt_level_1` (0.85): on these its
severity weighting promotes expensive, high-criticality units ahead of the cheap units that detect the
fault. The ninth mutation, `drop_vf2_post_layout`, is **undetected by every selector**, the black-box
quality oracle does not register VF2PostLayout removal on this corpus, capping all curves at
8/9 ≈ 0.889 (Figure 4).

We therefore report a **null result** at this scale: across nine events the proposed selector shows no
advantage over the simple baselines or random ordering. An **ablation** isolates the cause, removing
the severity term `impact_prior` *raises* mean AUC from 0.692 to 0.716 (it actively hurts); `novelty`
helps marginally (0.688 without); `change_stage` and `oracle_confidence` are inert on this corpus, and
a **sensitivity** sweep over ε ∈ {0.01, 0.05, 0.10} and exploration reserve ∈ {10, 15, 20}% leaves AUC
unchanged at 0.692, so the result is robust, not a tuning artifact. Per the claim-scope rule we make no
comparative-effectiveness or temporal-generalization claim.

All nine mutations share the Qiskit 2.4.2 base revision, so this is **not** a temporal-generalization
test: the configured cutoff (2026-01-01) places all nine mutation split-groups on the test side, with
no mutation event used for training, and selector configurations are frozen (Table 7) and were not
tuned on these events. We therefore label the comparison a *frozen-configuration pilot* rather than a
held-out evaluation.

**Table 3a. Frozen-configuration pilot metrics on the mutation cohort (9 events, 32 units each). Lower
normalized TTFR and higher AUC are better.**

| Selector | recall@5% | @10% | @20% | @40% | mean norm. TTFR | mean AUC |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| diversity_only | 0.89 | 0.89 | 0.89 | 0.89 | 0.114 | 0.886 |
| cheapest_first | 0.89 | 0.89 | 0.89 | 0.89 | 0.123 | 0.877 |
| history_only | 0.89 | 0.89 | 0.89 | 0.89 | 0.123 | 0.877 |
| change_stage | 0.89 | 0.89 | 0.89 | 0.89 | 0.123 | 0.877 |
| random (median, 20 seeds) † | 0.44 | 0.56 | 0.72 | 0.89 | 0.217 | 0.783 |
| proposed (risk_score) | 0.56 | 0.56 | 0.67 | 0.67 | 0.308 | 0.692 |

† Random over 20 seeds: per-fraction detection medians 0.44/0.56/0.72/0.89; mean AUC median 0.783
(seed range 0.613–0.854); mean norm. TTFR median 0.217 (range 0.146–0.387).

**Table 3b. Per-event area under the detection-vs-budget curve (1.0 = detected at ≈ zero cost;
0.0 = never detected). Nine mutation events.**

| Mutation event | cheap. | divers. | hist. | ch-stage | proposed | rand(med) |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| disable_optimization_loop | 0.97 | 0.98 | 0.97 | 0.97 | 0.99 | 0.88 |
| drop_vf2_post_layout | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| downgrade_routing | 0.98 | 1.00 | 0.98 | 0.98 | 1.00 | 0.94 |
| insert_redundant_cx_pair | 1.00 | 1.00 | 1.00 | 1.00 | **0.20** | 0.99 |
| drop_optimization_stage | 0.97 | 1.00 | 0.97 | 0.97 | 0.99 | 0.91 |
| force_opt_level_1 | 0.98 | 1.00 | 0.98 | 0.98 | **0.85** | 0.85 |
| force_opt_level_0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| downgrade_layout_trivial | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| insert_redundant_x_pair | 1.00 | 1.00 | 1.00 | 1.00 | **0.21** | 0.71 |

**Table 3c. Win/tie/loss of the proposed selector vs each baseline, by per-event normalized TTFR
(9 events).**

| Baseline | win | tie | loss |
|---|:--:|:--:|:--:|
| cheapest_first | 5 | 1 | 3 |
| diversity_only | 3 | 1 | **5** |
| history_only | 5 | 1 | 3 |
| change_stage | 5 | 1 | 3 |
| random (median) | 5 | 1 | 3 |

**Table 3e. Effect sizes (proposed vs each baseline on per-event AUC, 9 events) + bootstrap 95% CIs.**

| Comparison (proposed vs) | Cliff's δ | magnitude | Â₁₂ | baseline mean AUC [95% CI] |
|---|:--:|:--:|:--:|---|
| diversity_only | −0.30 | small | 0.35 | 0.886 [0.662, 0.998] |
| cheapest_first | −0.05 | negligible | 0.475 | 0.877 [0.655, 0.993] |
| history_only | −0.05 | negligible | 0.475 | 0.877 [0.655, 0.993] |
| change_stage | −0.05 | negligible | 0.475 | 0.877 [0.655, 0.993] |
| random (median) | +0.07 | negligible | 0.537 | 0.779 [0.750, 0.804] |

*Proposed mean AUC = 0.692 [0.400, 0.912]. (Per-event nTTFR Table 3d and the ablation table are in the
submitted .docx; reproduce with `cart evaluate` and `cart analyze`.)*

Figure 4 plots the detection-vs-budget curves: diversity-only and the cost/history/change-stage
baselines reach the 8/9 ≈ 0.889 ceiling almost immediately, random (median) climbs more gradually, and
the proposed selector plateaus lower because it defers cheap detectors on three events.

### 6.4 RQ3, Observability of historical regressions
We attempted five historical events and must distinguish a *demonstrated* observability gap from cases
that are merely unreproduced or under-powered at this scale. Of the five, **one (H1) is a built-from-
source demonstration that a real regression is invisible to a black-box output oracle**; the remaining
four are inconclusive and are *not* evidence that the oracles under-detect.

- **H1 (ElidePermutations, #14603), demonstrated observability gap.** Both buggy and fixed revisions
  were built from source. The fault sits in the `transpiler_contract_or_metadata` channel (Section
  2.2): it corrupts the `virtual_permutation_layout` property while leaving the layout-applied output
  unitary correct, so the output-only semantic oracle reports equivalence on the buggy build, even
  when the fix's own regression circuit is run through the full preset pass manager (with and without a
  coupling map). Per the production-pipeline rule the event is **rejected** (real fault, but
  production-unobservable). This is the one place the pilot establishes that black-box output oracles
  miss a contract/metadata-channel fault; the canonical reproduction uses the pass in isolation.
- **H3 (VF2Layout non-determinism, #14730), inconclusive (not reproduced).** The
  `determinism_or_reproducibility`-channel fault reproduces only under a *noisy device target* absent
  from our coupling-map backend; a strengthened, layout-sensitive determinism oracle observed
  determinism on our circuit. We cannot conclude anything about oracle sensitivity because the
  triggering condition was never created. Remains **blocked**. This is consistent with a large dynamic
  study that executed the Qiskit Terra suite 10,000 times across 23 releases and found genuine
  flakiness rare but often requiring thousands of runs to detect reliably, well beyond a typical CI
  budget [Kim2025].
- **H4 (VF2PostLayout no-op, #14120), inconclusive (under-powered).** The redundant-pass overhead
  stays below the 20% Stage-1 screen under single-sample timing on both small and larger opt-3
  circuits; this is a measurement-power limitation (exploratory performance on a laptop), not a
  demonstrated blind spot. Deferred to a controlled-hardware, multi-run protocol.
- **H2 (#14919) and H5 (#16285), not run.** H2 is expected to share H1's layout-property masking and
  H5 is an input-specific crash; neither has been reproduced, so neither contributes evidence.

By contrast, the controlled mutation cohort labels reliably (Table B). We therefore answer RQ3
narrowly: the pilot **demonstrates a single concrete observability gap**, a contract/metadata-channel
regression (H1) invisible to black-box output oracles, and leaves the determinism and small-overhead
channels **open**, having failed to reproduce or adequately power them on commodity hardware. We do
*not* claim that black-box oracles broadly under-detect; we claim that at least one important
manifestation channel is unobservable to them and that the others remain untested here. Section 6.6
quantifies how often such channels occur among real transpiler fixes.

### 6.6 Observability of real transpiler regressions: a repository-mining study
The H1 result raises a question the pilot cannot answer alone: how common are output-invisible
regressions in practice? We mined merged, changelog-listed bug-fix pull requests labelled
`mod: transpiler` from the Qiskit repository and classified each by the manifestation channel of the
fault it fixes (§2.2), following repository-mining practice for quantum-software bug characterization
[Yousuf2025] and empirical-reporting guidance for quantum-software testing [Li2026]. One author
classified **26 fixes** from titles, descriptions, and linked issues, recording a confidence flag; the
labels are released with the artifact (`data/observability_mining.csv`). **10 of 26 (38%; 41% excluding
low-confidence cases) fall in channels a black-box output-equivalence oracle cannot observe**,
corrupted layout/permutation contract metadata (7), non-determinism (2), and a dropped global phase (1,
invisible to equivalence-modulo-global-phase checks). The built-from-source H1 case is one instance of
the largest such class. The observability gap is therefore not an isolated curiosity: a substantial
minority of real transpiler regressions are unobservable to output-only oracles, motivating
fault-class-matched oracles (property/layout, determinism) as first-class CI checks.

**Table 8. Manifestation channels of 26 mined Qiskit transpiler bug-fixes ("observable" = detectable by
a black-box output-equivalence oracle).**

| Manifestation channel | Count | Observable? | Example PRs |
|---|:--:|:--:|---|
| output_semantic | 5 | yes | #16428, #16337, #13670 |
| compilation_failure | 6 | yes | #15626, #16285, #14998 |
| circuit_quality | 4 | yes | #14667, #13884 |
| performance | 1 | yes (if over screen) | #14120 |
| contract / metadata | 7 | **no** | #14939, #14919, #13945, #13833, #14603 |
| determinism / reproducibility | 2 | **no** | #14763, #14730 |
| global phase | 1 | **no** | #15943 |

*Threat: single-rater, title-and-description classification (construct validity); labels and confidence
flags are released for re-coding. The sample is recent merged fixes, not a complete census, so
percentages are indicative, not population estimates.*

## 7. Discussion
The pilot's central lesson is methodological rather than a horse-race outcome. Its most concrete
empirical finding is an **observability gap**: a real transpiler regression (H1) that lives in the
`transpiler_contract_or_metadata` channel, incorrect layout metadata that nonetheless leaves the
output unitary intact, is invisible to a black-box output oracle. We are careful not to over-generalize
from one event: the determinism and small-overhead channels (H3, H4) remain *open* in our data because
we could not reproduce or adequately power them on commodity hardware, not because we observed the
oracles failing. The honest reading is therefore a caution rather than a sweeping claim: equivalence
checking of compiled *outputs* is provably insufficient for at least one important class of compiler
regression, and the contract/metadata, determinism, and performance channels each plausibly need their
own oracle. A repository-mining study (§6.6) shows these output-invisible channels account for ≈ 38% of
recent real transpiler bug-fixes, so the gap is quantitatively material rather than anecdotal. This has the design consequences our methodology already encodes: a controlled mutation
cohort as a reliable labelling backbone while historical events mature; strict test-provenance
accounting (a regression test extracted from a fix did not exist when the bug was introduced, so it can
show a fault is real, a Secondary, retrospective claim, but must not count as evidence that a selector
would have caught the fault in real CI); and fault-class-matched oracles (property/layout comparison,
noisy-target determinism, multi-run performance on controlled hardware) in a scale-up.

The selection result is a **null result**, and we treat it as informative rather than disappointing.
At this scale the transparent `risk_score` selector did not beat the simple cost/diversity/history/
change-stage baselines or random ordering, and trailed them because its severity weighting can defer a
cheap detecting test (Section 6.3). An ablation isolates the cause: removing the severity term
`impact_prior` recovers baseline-level AUC (0.692 → 0.716), so the design is not wrong in principle but
mis-calibrated for a regime in which detection cost and fault severity are decoupled. More broadly, no
method separates because the detecting units are cheap and plentiful, so detection saturates within a
small fraction of the suite budget and there is almost no budget regime in which ordering, cost-aware
or otherwise, can matter. Whether the additional structure in `risk_score` helps is therefore an open question that only
a corpus whose detecting tests are expensive or sparse, with verified forward regressions, can answer;
the claim-scope rule (Section 4.10) correctly forbids any comparative-effectiveness claim from these
nine events.

## 8. Threats to Validity
We follow the standard software-engineering validity taxonomy.

**Construct validity.** The largest threat is oracle observability (Section 7): black-box oracles can
miss contract/metadata-channel faults (demonstrated for H1) and may miss determinism- and
performance-channel faults (untested here), so a "pass" does not certify fault-freeness. We mitigate by
separating cohorts, by an empirical (confirmation-based) false-positive rate, and by reporting which
oracle tier produced each label and which manifestation channel each historical fault occupies; the
provenance rule prevents post-fix tests from inflating the Primary claim.

**Internal validity.** Single-laptop timing is noisy; we calibrate cost with CPU process time, treat
performance as exploratory with a two-stage protocol, and exclude high-load runs. Reproducibility is
supported by write-once raw artifacts, fixed seeds, and labels regenerated from raw evidence. Test
non-determinism is a known confound in regression testing [Luo2014]; we treat determinism/
reproducibility as its own manifestation channel rather than folding it into correctness, and,
consistent with evidence that flaky tests are most detectable when newly added [Lam2020], confine
post-fix targeted triggers to the Secondary evaluation.

**External validity.** The corpus is small and specific to the Qiskit 2.x transpiler; results are
explicitly pilot-scoped and must not be generalized to other SDKs, versions, or larger suites without
the planned scale-up. The verified events are quality mutations, which may not represent the full
fault distribution.

**Conclusion validity.** With so few events, statistical comparison is under-powered; we therefore
avoid significance claims, report per-event outcomes alongside averages, and bind comparative claims
with the ≥ 3-forward-regression rule. The leakage-absence gate guards against optimistic bias from
information leakage.

## 9. Limitations and Future Work
The study is a feasibility pilot: zero historical events are verified through the production oracles,
the verified cohort is mutation-only, and the selector comparison yields a null result, at this scale
the proposed selector showed no advantage over simple baselines or random ordering, and, because the
detecting units are cheap and plentiful, detection saturates at a tiny budget fraction, leaving almost
no regime in which cost-aware ordering can separate methods (despite high overall cost variance;
Table D). The deferred
scale-up will (i) expand the corpus toward at least three verified *forward-regression* events and
deliberately include events whose detecting tests are expensive or sparse, so that cost-aware ordering
has a regime in which to separate methods (the present corpus fails to discriminate because cheap
detectors dominate, not because costs are uniform); (ii)
add fault-class-matched oracles, a property/layout oracle comparing `TranspileLayout` /
`routing_permutation`, a noisy-target determinism oracle, and three-run-median performance on
controlled hardware, to make currently-unobservable historical faults observable in a clearly
labelled retrospective track; (iii) introduce an optional logistic-regression / gradient-boosted-tree
comparison under identical anti-leakage rules; and (iv) trace selected fix-boundary events to their
true introducing commits via bisection, converting them to the forward cohort. Only after ≥ 3
forward-regression events are verified do comparative-effectiveness claims for temporal generalization
become admissible.

## 10. Conclusion
In this paper we studied whether regression-test selection and prioritization, long established for
classical software, can be realized for the quantum transpiler in a leakage-safe and cost-aware manner,
and what such an approach achieves at feasibility scale. We designed a methodology that separates change
events into non-pooled cohorts, applies tiered layout-aware oracles with an empirical false-positive
rate, scores tests with a transparent selector that distinguishes fault severity from detection
confidence, and is guarded by six implementation-validity gates and a strict claim-scope rule. We
realized the methodology in an open prototype and evaluated it on a Qiskit 2.x micro corpus.

Our empirical findings are reported without embellishment. Across nine controlled mutations the
transparent selector did not outperform the simple cost-, diversity-, history-, and change-stage
baselines, nor random ordering; a per-unit cost analysis shows that this null result arises because the
test units that detect the injected faults are cheap and plentiful, so detection saturates within a
small fraction of the budget regardless of ordering, and an ablation identifies the selector's severity
term as the specific component responsible, ruling out a mere tuning issue. Separately, one real
ElidePermutations regression that corrupts internal layout metadata is invisible to output-equivalence
oracles, and a repository-mining study of 26 real transpiler bug-fixes finds ≈ 38% lie in such
output-invisible channels, generalizing the single confirmed case, while the remaining reproduced
historical cases are reported as inconclusive rather than as evidence of oracle weakness.

Taken together, the study contributes a rigorous and reproducible evaluation methodology, an honest
feasibility baseline against which future selectors can be compared, and a concrete demonstration that
equivalence checking of compiled outputs is insufficient to observe an important class of
transpiler-contract faults. These outcomes do not constitute a comparative-effectiveness claim; rather,
they establish a credible foundation and a pre-specified path toward a larger empirical evaluation with
verified forward regressions, cost-heterogeneous corpora, and fault-class-matched oracles.

## 11. Artifact Availability
To support review and reproduction, the camera-ready will be accompanied by a DOI-archived snapshot
(e.g., Zenodo/OSF) and an anonymized repository link available at submission time, containing: the
prototype (`cart`) and CLI; the automated test suite and six validity gates; the static manifest and
mutation engine; the event ledger with exact candidate/baseline commit SHAs; the frozen change–stage
map, pre-declared thresholds, RNG seeds, and the frozen `risk_score` configuration (Table 7); a pinned
environment lock (`requirements.lock`); the write-once raw oracle artifacts and derived labels; the
generated `evaluation.json`; and an OSI-approved open-source license.

The frozen-configuration pilot of Section 6 is reproduced exactly by two commands:

```
python -m cart.cli ground-truth --unit-limit 64
python -m cart.cli evaluate --split all --random-seeds 20
```

These write Tables 3a–3d, the per-fraction random aggregates, the cost-distribution summary, and the
detection-vs-budget data of Figure 4 to a single `evaluation.json`. Building the historical events
(e.g., H1) additionally requires a Rust toolchain to compile the per-event Qiskit revisions from
source; the per-event recipe and reproduction command are given in Appendix A.

## Appendix A. Direct evidence for H1 (ElidePermutations, PR #14603)
H1 is the pilot's one demonstrated observability gap, so we record its evidence explicitly.

- **Revisions (built from source).** Candidate (buggy) `7c3890da` → baseline (fixed) `96fda188`;
  fix-boundary differential, PR #14603, fix-commit dated 2025-06-16.
- **Minimal trigger.** A circuit containing a `PermutationGate` together with two-qubit gates (the
  unit `trig-h1-elide-permutations`, drawn from the fix's own regression test), transpiled through the
  full preset pass manager at optimization level 3 on backends `none` and `line`.
- **Corrupted field.** The buggy `ElidePermutations` pass corrupts the `virtual_permutation_layout`
  property recorded in the `TranspileLayout` / output metadata; the layout-applied output unitary is
  left correct.
- **Oracle outcome.** The layout-normalized exact-unitary oracle reports EQUIVALENT (pass) on the
  buggy candidate, identical to the baseline, on both backends. The output-only oracle cannot
  distinguish buggy from fixed; the fault is visible only by comparing the recorded permutation
  property directly. Per the production-pipeline rule the event is rejected, not credited.
- **Reproduction.** Build both revisions with the per-event from-source runner, then run:
  `python -m cart.cli historical-run --event hist-elide-permutations-mapping --use-targeted`.
  The recorded per-run property values (baseline vs candidate `virtual_permutation_layout`) are written
  to the event's write-once raw artifact and included in the deposited archive.

## Abstract
*(EMSE narrative abstract, ~249 words. Note: the submitted .docx uses Springer author–year citations and an alphabetical reference list; this markdown source keeps [Key] tags internally.)*

Quantum compilers such as Qiskit's transpiler change frequently, and individual pass modifications can introduce correctness, circuit-quality, or compilation-performance regressions. Under a fixed continuous-integration budget, re-running a large suite of circuit–backend tests on every change is infeasible, which motivates cost-aware regression-test selection and prioritization for the transpiler, a setting that differs from classical regression testing because the oracle must decide circuit equivalence modulo qubit-layout permutation. In this paper we design a leakage-safe, cost-aware methodology for this problem and study it empirically through a feasibility prototype, cart, applied to Qiskit 2.x. The methodology separates change events into non-pooled cohorts (forward regressions, fix-boundary differentials, and controlled mutations), applies tiered layout-aware oracles, scores tests with a transparent risk_score selector, compares against five baselines (four classical heuristics plus a seeded random ordering) using detection-curve metrics, and enforces six implementation-validity gates together with a strict claim-scope rule. We evaluate on nine controlled mutation events over 32 circuit–backend test units (288 labels) and attempt to reproduce five real historical transpiler regressions from source. All validity gates pass and the prototype passes 57 automated tests. At this scale we find a null result: the proposed selector does not outperform the simple baselines or random ordering (negligible-to-small effect sizes), which an ablation traces to its severity-weighting term. A complementary repository-mining study of 26 real transpiler bug-fixes finds that ≈ 38% lie in channels invisible to output-equivalence oracles (layout/contract metadata, non-determinism, global phase), generalizing one built-from-source case we confirm directly. We frame the work as a reproducible feasibility study and outline a pre-specified path to a larger evaluation; all code and artifacts are released.

---

## References (working list; verified entries only)
- [Yoo2012] S. Yoo, M. Harman. "Regression testing minimization, selection and prioritisation: a survey." STVR 22(2):67–120, 2012. (VERIFIED, foundational survey)
- [Rothermel2001] G. Rothermel, R. Untch, C. Chu, M. J. Harrold. "Prioritizing test cases for regression testing." IEEE TSE 27(10):929–948, 2001. (VERIFIED)
- [Elbaum2002] S. Elbaum, A. Malishevsky, G. Rothermel. "Test case prioritization: a family of empirical studies." IEEE TSE 28(2):159–182, 2002. (VERIFIED)
- [Elbaum2001] S. Elbaum, A. Malishevsky, G. Rothermel. "Incorporating varying test costs and fault severities into test case prioritization" (cost-cognizant APFDc). ICSE 2001. (VERIFIED, confirm exact pages in revision)
- [Qiskit2024] A. Javadi-Abhari et al. "Quantum computing with Qiskit." arXiv:2405.08810, 2024. (VERIFIED)
- [Benchpress2025] P. D. Nation et al. "Benchmarking the performance of quantum computing software for quantum circuit creation, manipulation and compilation." Nature Computational Science, 2025. doi:10.1038/s43588-025-00792-y. (VERIFIED, confirm full author list in revision)
- [Machalica2019] M. Machalica, A. Samylkin, M. Porth, S. Chandra. "Predictive Test Selection." ICSE-SEIP 2019. arXiv:1810.05286. (VERIFIED, GBDT-based ML test selection, Meta/Facebook)
- [MorphQ2023] M. Paltenghi, M. Pradel. "MorphQ: Metamorphic Testing of the Qiskit Quantum Computing Platform." ICSE 2023. doi:10.1109/ICSE48619.2023.00202; arXiv:2206.01111. (VERIFIED)
- [QSTSurvey2024] "A Survey on Testing and Analysis of Quantum Software." arXiv:2410.00650, 2024. (VERIFIED, confirm authors/venue in revision)
- [MorphQpp2024] "MorphQ++: A Reproducibility Study of Metamorphic Testing on Quantum Compilers." Workshop on Replications and Negative Results, 2024. doi:10.1145/3695750.3695823. (VERIFIED)
- [Paltenghi2022] M. Paltenghi, M. Pradel. "Bugs in Quantum Computing Platforms: An Empirical Study." OOPSLA 2022; arXiv:2110.14560. (VERIFIED, confirm exact pages in revision)
- [QuCheck2025] G. Pontolillo et al. "QuCheck: A Property-based Testing Framework for Quantum Programs in Qiskit." arXiv:2503.22641, 2025. (VERIFIED, confirm full author list/venue in revision)
- [QEMI2026] "QEMI: A Quantum Software Stacks Testing Framework via Equivalence Modulo Inputs." arXiv:2602.09942, 2026; also Springer, doi:10.1007/978-3-032-22774-4_8. (VERIFIED, confirm authors/venue in revision)
- [Elbaum2014] S. Elbaum, G. Rothermel, J. Penix. "Techniques for improving regression testing in continuous integration development environments." ACM SIGSOFT FSE, 235–245, 2014. (VERIFIED via Consensus)
- [Elsner2021] D. Elsner, F. Hauer, A. Pretschner, S. Reimer. "Empirically evaluating readily available information for regression test optimization in continuous integration." ACM SIGSOFT ISSTA, 491–504, 2021. (VERIFIED via Consensus)
- [Spieker2017] H. Spieker, A. Gotlieb, D. Marijan, M. Mossige. "Reinforcement learning for automatic test case prioritization and selection in continuous integration." ACM SIGSOFT ISSTA, 12–22, 2017. (VERIFIED via Consensus)
- [PradoLima2022] J. A. Prado Lima, S. R. Vergilio. "A multi-armed bandit approach for test case prioritization in continuous integration environments." IEEE TSE 48(2):453–465, 2022. (VERIFIED via Consensus)
- [Pan2022] R. Pan, M. Bagherzadeh, T. A. Ghaleb, L. Briand. "Test case selection and prioritization using machine learning: a systematic literature review." Empirical Software Engineering 27(2):29, 2022. (VERIFIED via Consensus)
- [Barr2015] E. T. Barr, M. Harman, P. McMinn, M. Shahbaz, S. Yoo. "The oracle problem in software testing: a survey." IEEE TSE 41(5):507–525, 2015. (VERIFIED via Consensus)
- [QDiff2021] J. Wang, Q. Zhang, G. H. Xu, M. Kim. "QDiff: Differential testing of quantum software stacks." IEEE/ACM ASE, 692–704, 2021. (VERIFIED via Consensus)
- [QSPE2026] J. Ye et al. "QSPE: Enumerating skeletal quantum programs for quantum library testing." arXiv, 2026. (VERIFIED via Consensus)
- [Giallar2022] R. Tao, Y. Shi, J. Yao, X. Li, A. Javadi-Abhari, A. W. Cross, F. T. Chong, R. Gu. "Giallar: push-button verification for the Qiskit quantum compiler." ACM SIGPLAN PLDI, 641–656, 2022. (VERIFIED via Consensus)
- [Concolic2025] N. Choudhury et al. "Concolic testing for quantum compilers." IEEE ICCD, 2025. (VERIFIED via Consensus)
- [Burgholzer2021] L. Burgholzer, R. Wille. "Advanced equivalence checking for quantum circuits." IEEE TCAD 40(9):1810–1824, 2021. (VERIFIED via Consensus)
- [Bugs4Q2023] P. Zhao, J. Zhao, Z. Miao, S. Lan. "Bugs4Q: A benchmark of existing bugs to enable controlled testing and debugging studies for quantum programs." Journal of Systems and Software 205:111805, 2023. (VERIFIED via Consensus)
- [LintQ2024] M. Paltenghi, M. Pradel. "Analyzing quantum programs with LintQ: a static analysis framework for Qiskit." Proc. ACM Softw. Eng. (FSE) 1:1135–1157, 2024. (VERIFIED via Consensus)
- [Kim2025] D. Kim et al. "Detecting flakiness in quantum software: a dynamic testing approach." 2025. (VERIFIED via Consensus)
- [Lam2020] W. Lam, S. Winter, A. Wei, T. Xie, D. Marinov, J. Bell. "A large-scale longitudinal study of flaky tests." Proc. ACM Program. Lang. (OOPSLA) 4:1–29, 2020. (VERIFIED via Consensus)
- [Luo2014] Q. Luo, F. Hariri, L. Eloussi, D. Marinov. "An empirical analysis of flaky tests." ACM SIGSOFT FSE, 643–653, 2014. (VERIFIED via Consensus)
- [Peng2020] Q. Peng, A. Shi, L. Zhang. "Empirically revisiting and enhancing IR-based test-case prioritization." ACM SIGSOFT ISSTA, 324–336, 2020. (VERIFIED via Consensus)
- [Yousuf2025] M. M. Yousuf et al. "Characterizing bugs and quality attributes in quantum software: a large-scale empirical study." arXiv preprint, 2025. (VERIFIED via Consensus)
