# Project Plan: Cost-Aware Regression Testing for Qiskit Transpilation

This plan operationalises `METHODOLOGY.md` for an **initial ~3-month study** on a **single
16 GB laptop**. The methodology is the authoritative specification; where this plan adds detail,
it does so within the scope decisions recorded in `METHODOLOGY.md` Appendix A. Phases are executed
**in order**, no phase begins before the previous one passes its acceptance checks.

---

## 1. Objective and Success Definition

**Research claim under test.** A change-aware selector scored by
`expected_value = P(regression | change, circuit, backend) × impact / expected_cost` finds
regressions earlier than five baselines under the same CI budget.

**Initial-study success is *not* "the proposed selector wins."** Per Methodology §5.3, success is:

1. A reproducible micro-corpus pipeline (Phases 0–5) producing the methodology's metrics.
2. **All six implementation-validity gates pass.**
3. Results reported honestly, historical vs mutation separately, performance as exploratory,
   whatever the empirical outcome.

The selector beating baselines is the *finding*, not a precondition for completion.

**This is a feasibility / pilot study.** With 8–12 events it is not final evidence of universal
superiority. Report **per-event outcomes alongside averages**, and defer strong general claims to
the Phase 6 expansion.

---

## 2. Standing Guardrails (apply in every phase)

These restate the project rules and the methodology's leakage/reproducibility constraints. They
are checked continuously, not just at the end.

- **No leakage.** At selection time the selector uses only: candidate change metadata, manifest
  test metadata, baseline-version costs, and historical data strictly before `event_date`.
  Candidate transpilation runtime, candidate quality metrics, and candidate output labels are
  **never** inputs to ranking. (Methodology §4.3)
- **Temporal split is sacred.** No label, cost, or outcome from a test-split event appears in any
  training feature or historical aggregation. (Methodology §5.1)
- **Raw artifacts are immutable.** Everything under `data/raw/` is write-once. Derived data is
  regenerable and lives elsewhere. Never overwrite a raw oracle artifact.
- **Determinism.** Every selector run records its seed; same seed → identical ranking.
- **Two-layer environment.** Fixed harness and Benchpress revision for the study; Qiskit-under-test
  is built per event from its baseline and candidate source revisions (`environment/`).
- **Test-before-done.** Each phase ships unit tests plus a smoke test before it is declared
  complete.

---

## 3. Repository Layout

```
quantum-transpiler-regression-testing/
  METHODOLOGY.md
  PROJECT_PLAN.md
  environment/
    requirements.lock          # fixed HARNESS deps (write-once per study)
    ENV.md                     # Python ver, OS, CPU cores, RAM
    events/<event_environment_id>.lock   # per-event Qiskit build recipe (baseline+candidate)
  configs/
    budgets.yaml               # per-tier CI budgets (PR/Nightly/Release)
    seeds.yaml                 # per-event seeds
    thresholds.yaml            # PRE-DECLARED quality thresholds (τ_2q, τ_depth, ...) + sensitivity grid
    stage_map.yaml             # module/path -> canonical stage map (incl. passmanager_global, shared_utility_unknown)
    cutoff.yaml                # temporal split cutoff_date
  src/cart/                    # "cost-aware regression testing" package
    manifest/                  # Phase 0: test-unit enumeration + manifest
    events/                    # Phase 1: event table, mutation engine
    oracles/                   # Phase 2: tiered semantic/quality/perf oracles
    labels/                    # Phase 2: ground-truth labelling
    features/                  # topology (connectivity pressure), sensitivity
    selectors/                 # Phase 3 baselines + Phase 4 proposed selector
    metrics/                   # Phase 5: Recall@budget, TTFR, (N)APFDc, etc.
    gates/                     # validity gates (§5.3)
    cli.py                     # entrypoints per phase
  data/
    manifest_static/           # test_manifest_static — pure metadata (versioned)
    #   + targeted_triggers.json — SEPARATE targeted regression-trigger units (METHODOLOGY App. D),
    #     complement (do not replace) generic Benchpress units; never pooled in reporting
    profile_baseline/          # test_profile_baseline, keyed (event_id, baseline_sha, test_id, event_environment_id)
    events/                    # event table incl. split_group_id, event_environment_id
    raw/<event_id>/<test_id>/  # IMMUTABLE raw oracle artifacts
    derived/                   # labels, costs (regenerable from raw)
  results/<run_id>/            # per-run outputs + frozen config + seeds
  tests/                       # pytest unit tests
```

**Run isolation.** Every experiment writes to `results/<run_id>/` with a copy of the exact
config and seeds used, so any result traces back to the inputs that produced it.

---

## 4. Environment Setup (precedes Phase 0)

**Two-layer environment** (Methodology §0.1). The *harness* is fixed for the whole study; *Qiskit
is built per event* from its baseline/candidate source. A globally pinned Qiskit is incompatible
with historical reproduction.

| Step | Action | Artifact |
|---|---|---|
| E1 | Create the fixed **harness** env (Python, Benchpress, oracle harness, deps), no Qiskit pinned here. | `environment/requirements.lock` |
| E2 | Record Python version, OS, CPU core count, total RAM. | `environment/ENV.md` |
| E3 | Define the per-event Qiskit **build recipe** (from-source build of `baseline_sha`/`candidate_sha`); choose the initial compatible Qiskit release window. | `environment/events/<event_environment_id>.lock` |
| E4 | Confirm statevector feasibility on this machine for the sampled-SV tier (≤20–22 qubits). | note in `ENV.md` |

Acceptance: a fresh checkout + `requirements.lock` reproduces the importable harness; one event's
baseline and candidate Qiskit both build from source against the harness and transpile a trivial
circuit end to end.

---

## 5. Phase-by-Phase Plan

Each phase lists **goal → key tasks → deliverables/artifacts → acceptance checks → smoke test**.

### Phase 0, Compatibility and Test Manifest

- **Goal.** The `test_manifest_static` metadata artifact **and a working instrumentation
  capability** (pass-manager tracing + cost/memory measurement), proven by a small smoke profile.
  The authoritative per-event baseline profile is **not** built here, events do not yet exist.
- **Key tasks.** Enumerate test units via pytest collection / Benchpress adapter (not AST alone);
  populate `test_manifest_static` metadata (incl. `declared_pass_stages`); implement and validate
  the instrumented transpile harness (captures `executed_pass_stages` via pass-manager
  callback, **not** filename inference, plus cost, routing, peak memory); run it on a 3–5
  test-unit **smoke profile** to prove it works.
- **Deliverables.** `data/manifest_static/*`; instrumentation harness in `src/cart/manifest/`; a
  small smoke profile under `results/<run_id>/smoke_profile/`.
- **Acceptance.** Static metadata fields all present; instrumentation records measured cost +
  *actually executed* passes on the smoke subset; static manifest regenerable from one command.
- **Smoke test.** The 3–5 test-unit smoke profile runs end to end and shows `executed_pass_stages`
  diverging from `declared_pass_stages` where expected.

### Phase 1, Micro Event Dataset

- **Goal.** 8–12 change events as `(baseline_revision, candidate_revision, change_metadata,
  fault_id)`, each with a unique `fault_id`.
- **Key tasks.**
  - **Historical-first** (Methodology §1.4): identify reproducible regressions from the Qiskit
    issue tracker / release notes; capture `baseline_sha`/`candidate_sha`.
  - **Mutations only to fill gaps**: use permitted mutation types (§1.5) to cover regression
    types history can't supply; tag `fault_source = mutation`. (Do **not** use barrier removal as
    a semantic mutation.)
  - Assign `event_date`, `train_or_test`, `fault_type`, `fault_source`, `event_environment_id`,
    and **`split_group_id = base_revision + mutation_family`** for every event. Event dates follow
    §1.1: historical = candidate commit timestamp; mutation = **base revision timestamp** (not the
    authoring day).
- **Deliverables.** `data/events/events.(parquet|csv)`; mutation engine in `src/cart/events/`.
- **Acceptance.** Every event has a unique `fault_id`; historical vs mutation distinguishable via
  `fault_source`; every event has a `split_group_id` and `event_environment_id`; the table
  enforces a temporal field for the split; no event labels every release-tag diff as a regression.
- **Smoke test.** Reproduce one historical event and one mutation event from raw shas end to end.

### Phase 2, Ground-Truth Execution

- **Goal.** Per event: the **per-event baseline profile** (`test_profile_baseline`, keyed by
  `(event_id, baseline_sha, test_id, event_environment_id)`) **and** a reproducible `label` for
  every `(event_id, test_id)` pair, backed by raw artifacts.
- **Key tasks.**
  - **Per-event baseline profiling** (§0.3, §2): run the Phase-0 instrumented harness against each
    event's actual `baseline_sha` to populate `baseline_cost_s`, `oracle_cost_s`,
    `executed_pass_stages`, `routing_observations`, `peak_memory_mb`.
  - **Semantic oracle tiers** (§2.2): exact unitary ≤10–12 q; sampled-SV ≤20–22 q; property/
    structural for larger circuits, **larger circuits retained**, not dropped. Apply layout
    normalisation before any statevector comparison. Record `oracle_strength`, `oracle_cost_s`,
    `layout_normalization_applied`.
  - **Quality** (§2.3): compute Δ 2Q count and Δ depth separately; apply the Pareto rule with
    **pre-declared thresholds** (`τ_2q`, `τ_depth`, `τ_depth_improve`, `τ_2q_improve` in
    `configs/thresholds.yaml`, fixed from training/pre-registration before held-out evaluation).
  - **Topology feature** (§2.4): compute **connectivity pressure** per test unit.
  - **Oracle applicability** (§2.2): use unitary/statevector oracles only for circuits without
    measurement/reset/classical control; otherwise distribution/observable/metamorphic/structural.
    Record the `confirmed` flag for warnings to support the empirical oracle FP rate (§2.6).
  - **Performance** (§2.5): two-stage protocol, Stage-1 screening (3 runs vs threshold),
    Stage-2 confirmation (7–10 runs, bootstrap CI / Hodges–Lehmann) on suspected regressions
    only. Compute `normalized_load`; flag/rerun runs with `normalized_load > 0.3`. **Treated as
    exploratory** for the micro corpus but fully recorded.
  - Record `total_cost_s = transpilation_time_s + oracle_cost_s`.
- **Deliverables.** Immutable `data/raw/<event_id>/<test_id>/`; `data/profile_baseline/*`
  (event-keyed); `data/derived/labels.*`; `src/cart/oracles/`, `src/cart/labels/`,
  `src/cart/features/`.
- **Acceptance.** Every pair records `fault_id_detected`, `oracle_strength`, `oracle_artifact`,
  `label` (§2.6); labels reproduce from raw artifacts; quality reports both metrics; performance
  events carry stage-1/stage-2 evidence.
- **Smoke test.** Run all three oracle tiers on one small circuit each; confirm a known mutation
  is detected and a no-op change is not.

### Phase 3, Baselines

- **Goal.** Five baselines, all honouring the same per-event budget: random, cheapest-first,
  diversity-only, history-only, change-stage heuristic.
- **Deliverables.** `src/cart/selectors/baselines.py`; per-event selections in `results/<run_id>/`.
- **Acceptance.** Each baseline never exceeds the declared budget; history-only and any historical
  aggregation use **only** data before `event_date`.
- **Smoke test.** Run all five on one event under a tiny budget; confirm budget compliance and
  that history-only ignores future events.

### Phase 4, Proposed Transparent Selector

- **Goal.** The interpretable **`risk_score`** selector (no ML; not a probability) of Methodology
  §4.1, with the split budget (exploration reserve + main allocation) and diversity constraint.
- **Key tasks.** Implement the `risk_score` components, keeping **`impact_prior` (severity)** and
  **`oracle_confidence` (detectability)** as separate factors; load the stage map from
  `configs/stage_map.yaml`; reserve **10–20% of budget for stage-independent exploration** and
  route `passmanager_global` / `shared_utility_unknown` changes there; apply the `ε` floor; use the
  cold-start fallback (`historical_stage_conditioned_impact = 1.0`); record per-event seeds. No
  candidate `fault_type`, runtime, quality, or label is ever an input (§4.3).
- **Deliverables.** `src/cart/selectors/proposed.py`; selections + seeds in `results/<run_id>/`.
- **Acceptance.** Selector uses only §4.3-permitted inputs (leakage check); never exceeds budget;
  same seed → identical ranking.
- **Smoke test.** Run on one event; assert reproducibility across two runs with the same seed and
  a leakage assertion that candidate outcomes are absent from the feature vector.

### Phase 5, Held-Out Evaluation

- **Goal.** Metrics on the temporal test split, plus all six validity gates.
- **Key tasks.**
  - Apply the temporal split (`cutoff.yaml`) at **`split_group_id` level**, no group split across
    train/test; groups straddling the cutoff go wholly to test (§5.1).
  - Compute primary metrics: **Recall@budget**, **(normalized) TTFR**, **detection rate @
    5/10/20/40% budget**, **AUC of detection-vs-budget**; plus selection overhead, empirical
    oracle FP rate (confirmation-based), diversity coverage. Report **APFDc only for events with
    multiple independent faults under one ordering**, not merely because a split has ≥3 faults.
  - Report **historical vs mutation separately**; report Correctness and Quality as primary
    groups and Performance as exploratory.
  - Run **sensitivity analysis** over the quality (and perf) thresholds.
  - Run the six **implementation-validity gates** (§5.3).
- **Deliverables.** `results/<run_id>/metrics.*`; gate report; sensitivity tables;
  `src/cart/metrics/`, `src/cart/gates/`.
- **Acceptance (all must hold).** Budget compliance; reproducibility; leakage absence; label
  reproducibility; metric correctness vs ≥2 hand-computed examples; oracle coverage complete.
- **Smoke test.** Hand-compute Recall@budget and TTFR on a 2–3 test toy example; assert the metric
  code matches.

### Phase 6, Scale-Up and Optional ML *(deferred; planned, not in initial study)*

Retained in `METHODOLOGY.md` as the planned scale-up. Executed only after Phase 5 gates pass and
more compute is available: expand corpus + suite, re-run everything, re-verify gates, then the
optional logistic-regression / GBT comparison under the same leakage rules.

---

## 6. Indicative Schedule (~12 weeks)

| Week | Focus | Exit criterion |
|---|---|---|
| 0 | Environment setup (E1–E4) | Harness reproduces; one event's per-event Qiskit builds + transpiles |
| 1–2 | Phase 0 static manifest + instrumentation capability | Static metadata populated; instrumented smoke profile passes |
| 3–4 | Phase 1 events (historical hunt + mutation gap-fill) | 8–12 events, unique fault_ids, sources tagged |
| 5–6 | Phase 2 per-event baseline profiling + oracles/labels (semantic/quality) | Event-keyed profiles built; labels reproduce from raw; coverage complete |
| 7 | Phase 2 performance (two-stage) + connectivity-pressure feature | Stage-1/2 evidence recorded; load normalisation in place |
| 8 | Phase 3 baselines | Five baselines budget-compliant |
| 9 | Phase 4 proposed selector | Leakage + reproducibility asserted |
| 10 | Phase 5 metrics | Recall@budget, TTFR, FP rate, overhead computed |
| 11 | Validity gates + sensitivity analysis | All six gates pass |
| 12 | Write-up + full reproducibility pass | Clean re-run from raw reproduces results |

Buffer is intentionally light; the most common slip is Phase 1 historical reproduction (see risks).

---

## 7. Data-Leakage Control Checklist (audited each phase)

- [ ] Selector feature builder imports no candidate runtime, quality, or label fields.
- [ ] `impact_prior` and `oracle_confidence` use no candidate `fault_type`; computed from pre-execution signals only.
- [ ] Historical aggregations filter strictly on `event_date < current event_date`.
- [ ] Train/test split applied at `split_group_id` level; no group spans both splits.
- [ ] Train/test split applied before any feature aggregation; no test-split data in training.
- [ ] A unit test asserts that injecting candidate outcomes does not change any ranking.

## 8. Reproducibility Checklist (Definition of Done)

- [ ] `requirements.lock` + `ENV.md` committed; fresh env reproduces.
- [ ] Every `results/<run_id>/` contains its frozen config and seeds.
- [ ] All raw oracle artifacts present, hashed, and write-once.
- [ ] Labels regenerate from raw artifacts byte-for-byte (or hash-stable).
- [ ] Metric code validated against ≥2 hand-computed examples.
- [ ] All six §5.3 validity gates pass and are logged in the gate report.

---

## 9. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Historical regressions hard to reproduce (old envs, commit hunting) | High | High | Time-box each to ~1 day; fall back to a mutation that covers the same regression type; document the gap. |
| Per-event Qiskit source builds fail/slow against the fixed harness | Medium | High | Restrict historical events to one compatible release window; cache builds by `event_environment_id`; verify build in Phase 0 smoke before committing an event. |
| Too few distinct faults for APFDc | Medium | Medium | Lead with Recall@budget and TTFR (methodology-primary); report APFDc only when ≥3 fault_ids/split. |
| Noisy single-laptop performance timing | High | Medium | Two-stage protocol + `normalized_load` gating; performance labelled exploratory. |
| Statevector memory blow-up | Low | High | Width-bounded exact oracles; sampled-SV ≤20–22 q; property/structural above. |
| Accidental leakage via history features | Medium | High | Automated leakage unit test (§7) in CI for every selector. |
| Scope creep into Phase 6 | Medium | Medium | Phase gate: Phase 6 starts only after all Phase 5 gates pass. |

---

## 10. Next Recommended Task

**Begin Environment Setup (Section 4, steps E1–E4):** create the fixed harness env
(`requirements.lock`, `ENV.md`), define the per-event Qiskit build recipe and initial release
window, and confirm statevector feasibility, then proceed to Phase 0 (static manifest +
calibrated baseline profile). Do not start Phase 1 work until the Phase 0 manifests pass their
acceptance checks.
