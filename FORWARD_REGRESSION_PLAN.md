# Forward-Regression Verification Plan (toward ≥ 1 verified event before 31 July 2026)

Actionable extension of `data/events/PROVENANCE_BACKLOG.md`. Goal: convert the paper from **0 verified
forward-regression events** to **at least one**, since that is the single biggest reviewer lever.

## What one verified forward event buys you (and the honest ceiling)

It would (a) validate the **Primary-CI eligibility rule** on a *real* event — today it is only exercised
synthetically on the mutation cohort; (b) give the selection evaluation **≥ 1 real CI-shaped event**
instead of mutations only; and (c) directly answer the reviewer concern "zero real forward regressions."

It does **not** unlock temporal-generalization or comparative-effectiveness claims — the claim-scope
rule still requires **≥ 3** verified forward_regression events. So frame any single result as
"the pipeline is now validated on a real forward regression," nothing stronger.

## Current state (5 historical events)

| Event | Cohort | Channel | Status | Why stuck |
|---|---|---|---|---|
| H1 ElidePermutations (#14603) | fix_boundary | contract/metadata | rejected | output-invisible to the black-box oracle (corrupts `virtual_permutation_layout`, not the unitary) |
| H2 final_layout (#14919) | fix_boundary | contract/metadata | not run | expected to share H1's masking |
| H3 VF2Layout determinism (#14730) | fix_boundary | determinism | blocked | needs a noisy `Target` your coupling-map backend lacks |
| **H4 VF2PostLayout no-op (#14120)** | **forward_regression** | performance | blocked | no-op overhead < 20% screen on the ≤ 8-qubit corpus, single-sample timing |
| H5 VF2Layout panic (#16285) | fix_boundary | compilation_failure | not run | input/target-specific crash |

Only **H4 is already a forward regression** (no commit tracing needed). H1 is already built and fully
characterized. H5 is the only crash (binary, trivially detectable once reproduced).

## Recommended paths, ranked by effort-to-payoff

### Path A — Primary: make H4 detectable in the right regime

**Key insight (validated against Qiskit issue #14867 / #14120):** the no-op VF2PostLayout overhead is
large specifically for **highly symmetric circuits mapped to large coupling maps at optimization level
3** — the exact regime your ≤ 8-qubit, small-backend corpus never exercised. The fault is real; the
pilot simply didn't hit the regime where it shows. Steps:

1. **Pre-declare and freeze a performance protocol *before* measuring** (leakage-safe): ≥ 5-run median
   CPU process time; a robust effect size (Mann–Whitney U + Cliff's δ) with a bootstrap CI; detection
   rule = median slowdown ≥ a justified threshold **and** the CI excludes 0. Commit it as a new
   `performance.stage2` block in `configs/thresholds.yaml` plus a one-paragraph note, and do **not**
   adjust it after seeing results.
2. **Add generic test units in the high-overhead regime:** symmetric families (GHZ, and a larger
   symmetric circuit) on a **large** heavy-hex coupling map (e.g., 27–127 qubits), opt-level 3. These
   are `pre_existing` generic workloads (not `extracted_from_fix`), so they are **Primary-CI eligible**.
3. **Run multi-run timing** for the event on a quiet machine (close apps, pin the process, disable
   turbo/throttle where feasible):
   `python -m cart.cli historical-run --event hist-vf2postlayout-noop --unit-limit 16`
4. **If the slowdown is robust** → H4 becomes a verified, *detected* forward regression. Set its
   `reproducibility_status` to `verified` in `events.json`, re-run the gates and metrics
   (`python -m cart.cli evaluate --split all --random-seeds 20`), and update the manuscript: Table C,
   §6.3, §6.5, and §9 now report **one verified forward regression** and the eligibility rule validated
   on a real event.
5. **If still below a defensible threshold** → report it cleanly as "genuinely below detection at
   commodity scale," which is a sharper, more useful statement than the current "under-powered."

*Effort:* low–moderate (already built and already forward). *Risk:* single-machine timing noise,
mitigated by multi-run + effect size. **Best effort/reward — do this first.**

### Path B — Highest narrative value: trace H1 to forward + a minimal property oracle

H1 is already built and characterized and is the backlog's #1 tracing candidate. Steps:

1. **Bisect to the introducing commit** (recipe in `PROVENANCE_BACKLOG.md`):
   `git log --follow -p -- qiskit/transpiler/passes/optimization/elide_permutations*`, then
   `git bisect` between the PermutationGate-support commit and the parent of `96fda188`, using a
   scripted reproduction as the bisect test, to find the introducing commit `I`.
2. Record `baseline = I^`, `candidate = I`, `event_date = I` timestamp, `pair_orientation = forward`,
   `evaluation_cohort = forward_regression`; move the event out of the fix-boundary cohort.
3. **Add a minimal property/layout oracle** comparing `virtual_permutation_layout` /
   `routing_permutation` (a clearly-labelled deviation that lives only in the **Secondary retrospective**
   track, never the Primary CI claim).
4. Re-run the per-event runner; the property oracle now *detects* the forward regression.

*Payoff:* upgrades your headline observability finding from fix-boundary to **forward/CI orientation**
and yields a verified forward event (detected by the property oracle). *Effort:* moderate (bisection is
fiddly; the oracle is small). Detection is via a *new* oracle, so it strengthens the observability story,
not the Primary selection story.

### Path C — Backstop: reproduce the H5 crash (real functional fault)

A crash is binary, so detection is rock-solid once reproduced — no timing or statistics. Steps:

1. Build the two pinned revisions (`f0fae6f3` buggy parent → `0b2cdf2b` fix).
2. Reproduce the panic: construct a `Target` with **no reported error rates** so the VF2Layout fallback
   heuristic yields a ≥ 1.0 error (the #16285 trigger). Confirm the panic on the buggy build and a clean
   transpile on the fix.
3. Even as `fix_boundary`, this replaces the synthetic `incomplete_basis_translation` fallback with a
   **real historical functional event**. Optionally bisect to the introducing commit for a *detected
   forward* functional regression.

*Effort:* moderate (target-specific reproduction). *Reliability:* high once the target condition is met.

## Leakage-safety & honesty guardrails

- Pre-declare, freeze, and version any new threshold, oracle, protocol, or test unit **before** looking
  at held-out outcomes; the leakage-absence gate must still pass.
- New generic units (Path A) are `pre_existing` → Primary-CI eligible. New oracles (Path B) → Secondary
  retrospective only.
- ≥ 3 forward events remain required for any temporal-generalization claim. One event = "validated on a
  real forward regression."

## Suggested sequence before 31 July

1. **Path A first** — lowest effort, already built; if the slowdown lands you have your verified forward
   event and a manuscript update.
2. **Path B in parallel** — highest narrative payoff regardless of A, because it reinforces the
   observability headline in forward orientation.
3. **Path C** as the guaranteed-detectable backstop and to upgrade the functional event from synthetic
   to real.

Landing A (and ideally B) flips the paper from "0 verified forward events" to "1–2 verified forward
events plus a forward-orientation observability demonstration" — the most acceptance-relevant
improvement available before the deadline.

## Reference commands (grounded in `cart`)

```
# Run one event from per-event from-source venvs (needs the Rust toolchain; see environment/ENV.md)
python -m cart.cli historical-run --event hist-vf2postlayout-noop --unit-limit 16
python -m cart.cli historical-run --event hist-elide-permutations-mapping --use-targeted

# Validate the ledger with real SHAs, then re-run gates + metrics after a verification
python -m cart.cli events validate --require-ready
python -m cart.cli evaluate --split all --random-seeds 20
```
