# Scale-Up Protocols — C2 (power the mining study) and C4 (wire the property oracle)

The two experimental Criticals from the peer review (Path A). Both build on tooling that already exists
in the repo; each ends with concrete acceptance criteria and the manuscript edits to make afterward.

---

## C2 — Power the observability mining study (26 → ≥ 60 fixes)

**Goal.** Raise the mined sample to n ≥ 60 (target 60–100), add a third rater with audited adjudication,
build-validate a subset of "invisible" labels, and re-report the proportion and κ with intervals.
**Reuses:** `data/mining_validation/CODEBOOK.md`, the rater sheets, and the new `scripts/mining_stats.py`.

### C2.1 — Expand the sample
- **Inclusion rule (record it):** merged PRs labelled `mod: transpiler` that are *bug fixes* (not
  features/enhancements), across the Qiskit 2.x line; extend into 1.x only if needed to reach 60–100.
- **Enumerate candidates** from a local clone, pager-free:
  ```
  git -C environment\_builds\hist-vf2post-14120-base\qiskit --no-pager log --oneline --grep="Fix" -i -- qiskit/transpiler/ | head -300
  ```
  Better still, harvest the **"Bug Fixes"** sections of the 2.x release notes (each entry links its PR);
  that list is already curated as fixes.
- Add each fix as a Rater-1 row in `data/observability_mining.csv`, classified per `CODEBOOK.md`.

### C2.2 — Independent classification (three raters)
- Rater 1 → `data/observability_mining.csv`; Rater 2 → `data/mining_validation/rater2_sheet.csv`;
  **Rater 3 (new)** → `data/mining_validation/rater3_sheet.csv` (copy rater2's header).
- Each rater uses only PR title/description/linked issues, never another rater's labels.

### C2.3 — Audited adjudication
- Merge into `data/mining_validation/dual_rater_labels.csv` (`r1_*`/`r2_*` columns; add `r3_*`).
- Resolve every disagreement by a **documented** rule: majority of the three raters, or discussion with
  the rationale recorded in `note`. (This is the "third rater / audited adjudication" the review asks for.)

### C2.4 — Build-validate a subset of "invisible" labels
- Pick **k ≥ 5** fixes labelled output-invisible (`contract_metadata` / `determinism` / `global_phase`).
- For each, confirm empirically (as for H1) that the output oracle cannot see it, reusing existing tools:
  ```
  python scripts\find_introducing_commit.py --token <fn/symbol> --file <path>       # get SHAs
  python scripts\add_forward_event.py --event-id <id> --env-id <env> --fault-type semantic --pr <PR> --reference "<title>" --introducing-sha <SHA>
  .\environment\setup\build_qiskit_event.ps1 -Sha <baseline> -EventEnvId <env>-base -Force
  .\environment\setup\build_qiskit_event.ps1 -Sha <candidate> -EventEnvId <env>-cand -Force
  python scripts\verify_h1_isolated.py --event <id> --pass <Pass> --trigger <trigger>   # or the property route (C4)
  ```
- Record how many labels the build-from-source check confirms.

### C2.5 — Recompute the statistics
```
python scripts\mining_stats.py --rater3 data\mining_validation\rater3_sheet.csv
```
Reports: output-invisible proportion + **Wilson 95% CI**; **Cohen's κ** (R1 vs R2), binary + channel,
each with **95% CI**; **Fleiss' κ** across the three raters. (Verified to reproduce the current numbers:
38.5% [22%, 57%]; κ binary 0.68 [0.38, 0.97], channel 0.67 [0.45, 0.88].)

### C2 — acceptance criteria
n ≥ 60 · proportion + Wilson CI · Cohen's κ + CI · Fleiss' κ (3 raters) · ≥ 5 invisible labels
build-validated. **Then update §6.6 and Table 17** with the new n, proportion + CI, and κ + CI.

---

## C4 — Wire the property/layout oracle into the pipeline

**Goal.** Make the property/isolated-pass oracle a first-class *Secondary-track* check in the runner and
run **H1 and H2** through it. **Reuses:** `src/cart/oracles/property_layout.py`, the worker
`--isolated-pass` mode, and `scripts/verify_h1_isolated.py` (already detects H1). H2's trigger
(`trig-h2-final-layout-composition`) already exists.

**Implemented in the runner (30 Jun).** `run_targeted_event` now has an `oracle_type="contract"` branch
that runs the pass in isolation on both builds and flags a divergence (differing output, differing
`property_set`, or an asymmetric error) as `contract_metadata_fail` on the Secondary track;
`trig-h1-elide-permutations` is retyped to it (`isolated_pass="ElidePermutations"`). H1 now routes
through the property oracle automatically:

```
python -m pytest -q tests/test_targeted.py          # confirm the suite stays green first
python -m cart.cli historical-run --event hist-elide-permutations-mapping --use-targeted
# expect {contract_metadata_fail: 1} on the real buggy/fixed builds; {pass: 1} on the fixed anchor
```

### C4.1 — Build H2 from source
H2 = `hist-final-layout-composition` (PR #14919; candidate `14df5941…`, baseline `dfcc5c6c…`, env-id
`hist-finallayout-14919`):
```
.\environment\setup\build_qiskit_event.ps1 -Sha dfcc5c6ce87fa424c8fd7abf22baba9e8750fa66 -EventEnvId hist-finallayout-14919-base -Force
.\environment\setup\build_qiskit_event.ps1 -Sha 14df5941a5915a2b517cdf9bc014a6838e752f92 -EventEnvId hist-finallayout-14919-cand -Force
```

### C4.2 — Route contract/metadata events through the property oracle
In `src/cart/labels/historical_runner.py::run_targeted_event`, add a branch so that units whose
`oracle_type` is `"property"`/`"contract"` (or whose fault channel is `contract_metadata`) are evaluated
by the **isolated-pass differential** (the logic in `verify_h1_isolated.py`: run the pass alone in both
builds; a diverging output, a diverging `property_set`, or an asymmetric error = detected) rather than the
output semantic oracle, and emit the label `contract_metadata_fail` on the **Secondary** track with a
standard write-once raw artifact. Retype the H1/H2 targeted units to this path (H2's is currently
`"semantic"`; like H1 it is masked by the full pipeline, so it needs the isolated/property differential).

### C4.3 — Run H1 + H2
```
python scripts\verify_h1_isolated.py --event hist-elide-permutations-mapping          # H1 (already DIVERGENT)
python scripts\verify_h1_isolated.py --event hist-final-layout-composition --trigger trig-h2-final-layout-composition --pass <pass>
```
Report the **empirical FP rate** of the property oracle over these events.

> **Caveat on H2.** #14919 concerns routing passes *composing* `final_layout`, not a single pass, so the
> clean single-pass isolation that works for H1 (ElidePermutations) may not reproduce H2. If it does not,
> validate H2 instead by comparing the recorded `final_layout` / `routing_permutation` between builds via
> the property oracle's `extract_layout_props` (worker `--capture-layout`), i.e. the
> `scripts/verify_h1_property.py` route. Treat H2 as more uncertain than H1.

### C4 — acceptance criteria
H1 and H2 each evaluated by the pipeline-integrated property oracle (Secondary track), producing a
standard raw artifact + label. **Then update Table C and §6.5** (H1 already noted; add H2), and report the
property oracle's FP rate.

---

## Sequencing note
C2 and C4 are independent and can run in parallel. C4 is the smaller lift (H2 builds + one integration
branch; H1 already works). C2 is the larger lift (data collection + a third rater), but it is what most
strengthens the paper's now-headline contribution, so prioritize C2 if you can only do one.
