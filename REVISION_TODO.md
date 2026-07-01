# Revision To-Do — Peer Review Response

Source: supervisor's editorial peer review of `paper/PAPER.docx` (handling editor + 3 referees).
**Decision: Major Revision.** Readiness now ≈ 58%, achievable ≈ 80% after revision.
Venue calibration from the review: QIP (IF ≈ 2.2) is a *good, realistic match* for a careful
feasibility study — do **not** aim this at a flagship SE venue. One revision cycle is feasible.

---

## 0. Strategic decision (make this FIRST, with supervisor)

The whole review hinges on one repositioning, then a path choice:

- **Path A — observability paper (RECOMMENDED, ~1 cycle).** Re-center on "how often do real
  transpiler regressions escape output-equivalence oracles, and what should CI assert instead?"
  Power the mining study, keep H1 as the build-from-source anchor, implement the property oracle,
  present selection as an explicit null baseline. Plays to the paper's real strengths.
- **Path B — selection paper (slower).** Build a cost-heterogeneous corpus with expensive oracle
  tiers + ≥ 3 verified forward regressions so RQ2 can produce a real answer. Substantial new work;
  reserve as the signposted follow-on.

> Core diagnosis to internalize: the value proposition is **inverted** — the weakest result
> (cost-aware selection, a null in a regime with ~1.65 CPU-s total cost where ordering *cannot*
> matter) is the headline, and the strongest (the ~38% output-invisibility measurement) is the
> supporting act. Fixing this is mostly **editorial**, not new theory.

The todo below is organized for **Path A**.

---

## ✅ Done in the editorial pass (30 Jun) — against current `PAPER.docx` + cover letter

- **C1 / C3b / M2** — title now leads with oracle observability; abstract rewritten (256→213 words) to lead
  with the finding + Wilson CI, methodology second, selection as an explicit documented null; contribution
  list reordered (observability #1); cover-letter title + framing synced.
- **C4 (editorial part)** — "tiered layout-aware oracles" softened to "layout-aware oracles" in the headline
  claims. *(Full pipeline wiring still open — see below.)*
- **I1** — Table 6 75th-percentile filled (**0.0343**); CV-heterogeneity narrative qualified as immaterial.
- **I2** — Figures 1–3 now cited (§5, §4.2, §4.5); all four figures referenced in order.
- **I3** — empirical FP rate reported as a number (**0.068**) in §6.2.
- **I4** — Wilson 95% CI **[22%, 57%]** on the 38%; κ 95% CI **[0.38, 0.97]**; H1 dual role disclosed + 9/25
  leave-one-out robustness.
- **I5** — ref [36] flagged as a preprint where the claim depends on it.
- **I6** — detection-uplift ("all 10 of 26 become observable") + concrete Qiskit-CI assertion recommendation.
- **I7 / I8** — vacuous-temporal-split threat (§8 Internal) and H2/H3/H5-not-reproducible caveat (§8 External).
- **I9** — risk_score weights stated to be hand-set; framed as a documented heuristic baseline, not a method.
- **I10** — equivalence-checking contrast sharpened in §2.3 (output equivalence as an incomplete criterion).
- **I11** — AI-use statement made specific (drafting vs. code vs. analysis).
- **M1 / M3** — the 4× "cheap detectors saturate" repetition consolidated to back-references; long H4 sentence
  split; `cart` expanded once ("cost-aware regression testing").

### ⏳ Remaining (experimental — needs your builds/compute)

- **C2** — expand the mining study from 26 to ≥ 60–100 fixes; re-run the Wilson/κ CIs; build-validate a subset.
- **C4 (full)** — wire the property/layout oracle into the pipeline (generalize `verify_h1_isolated.py`) and
  re-run H1 (and H2) through it.
- **Sync** — update README, `CITATION.cff`, and the Zenodo record to the new title.

---

## 1. CRITICAL — required before resubmission

- [ ] **C1. Reposition around observability.** Make §6.6 + H1 the primary contribution; demote the
  selection study to a secondary, explicitly-labelled null/feasibility baseline. Revise **title**,
  **abstract**, and **contribution list** to match. *(Editorial; highest leverage. Title still leads
  with "Regression Testing" — move oracle observability to the front.)*
- [ ] **C2. Power the mining study.** Enlarge n from 26 to **≥ 60–100** transpiler fixes; report a
  **Wilson 95% CI** on the proportion (review estimates ~[21%, 58%] for 10/26) and a **CI on κ**;
  add a third rater or audited adjudication; **disclose H1's dual role** (it both motivates the
  taxonomy and is counted in the prevalence); **build-from-source-validate a subset** of "invisible"
  labels as was done for H1. *(Experimental + stats; the biggest single lift.)*
- [ ] **C3. Resolve the RQ2 dilemma.** Either (a) scale selection into a true cost-pressure regime
  (expensive oracle tiers + sparse/costly detectors + ≥ 3 verified forward regressions) — Path B — or
  (b) **drop selection to a documented null** and stop framing it as a research question with a
  verdict. For Path A, choose (b). *(Decision → editorial for Path A.)*
- [ ] **C4. Align oracle claims with implementation.** The structural fallback above 12 qubits is not
  a semantic check, and the property/layout oracle that catches H1 is deferred — so "tiered
  layout-aware oracles" is largely unimplemented in the evaluated pipeline. Either **wire the
  property/layout oracle into the pipeline** (generalize the existing `scripts/verify_h1_isolated.py`
  prototype) and re-run H1 (and H2 if it shares the masking) through it, **or** remove "tiered
  layout-aware oracles" from the headline contributions and confine claims to the exact-unitary tier.
  *(Experimental or editorial.)*

---

## 2. IMPORTANT

- [ ] **I1. Table 6 fix.** The **75th-percentile cell is empty (`—`) — CONFIRMED** in the current
  file. Fill it (compute from the per-unit cost data). Also drop or plainly qualify the
  CV ≈ 1.85 "heterogeneity" narrative — heterogeneity within a 1.65-second suite is immaterial.
- [ ] **I2. Figure numbering.** **CONFIRMED: only "Figure 4" is cited; Figures 1–3 are never
  referenced.** Ensure all figures exist and are cited in order (renumber, or add the missing
  citations / figures).
- [ ] **I3. Report the empirical FP rate as a number.** **CONFIRMED: defined in §4.4 but never
  quantified** anywhere in the results. Report the actual value (and n) from the pilot.
- [ ] **I4. Add CIs throughout small-n results.** Replace prose hedges with numbers: Wilson CI on
  the 38% (10/26), CI on κ = 0.68 (from the dual-rater data), and keep the existing AUC bootstrap CI.
- [ ] **I5. Stabilize preprint references.** Ref **[36] reads "Preprint (venue/DOI to be confirmed)"**
  yet supports the flakiness/10,000-runs claim; [25], [35], [37] are arXiv. Stabilize them, or soften
  any claim resting *solely* on a non-refereed source.
- [ ] **I6. Quantify detection uplift + concrete CI recommendation.** Using the mining data, state
  e.g. "**10 of 26 currently-invisible fixes would become observable**" with fault-class-matched
  oracles, and recommend *which* properties Qiskit CI should assert (`TranspileLayout`,
  `final_layout`, `routing_permutation`, `virtual_permutation_layout`) and at what cost. Generalize
  the H1 isolated-pass check into this recommendation. *(Turns a descriptive finding into one with
  teeth — review calls this out twice.)*
- [ ] **I7. Surface the "vacuous temporal split" as an explicit threat (§8).** All 9 mutations share
  the 2.4.2 base, so nothing trains and "leakage-safe" is demonstrated where there is nothing to leak.
- [ ] **I8. Reproducibility-scope caveat.** State plainly that H2/H3/H5 are **not reproducible as
  submitted** because they were not run.
- [ ] **I9. risk_score honesty.** Present it as a **documented heuristic baseline, not a method**;
  the criticality weights (GHZ 1.0/QFT 1.5/QAOA 1.3/Clifford 1.2), oracle_confidence weights, and
  per-oracle costs are hand-set — justify, learn, or explicitly flag as ad hoc. Note the ablation
  shows the severity term is harmful and the rest inert, and it loses to random (0.692 vs 0.783).
- [ ] **I10. Deepen equivalence-checking coverage (§2.3, §3).** Engage decision-diagram-based and
  other tractable equivalence-checking lines; add a paragraph contrasting the observability finding
  with the literature's implicit assumption that **output** equivalence is the right correctness
  criterion — "that is where your contribution bites."
- [ ] **I11. AI-use statement.** Add one sentence specifying *which* artifacts were AI-assisted
  (drafting vs. code vs. analysis).

---

## 3. MINOR polishing

- [ ] **M1. Cut repetition.** The "cheap detectors saturate early, so ordering can't matter" point
  appears ~4× (§6.3, §7, §9, §10). Consolidate to once, with emphasis.
- [ ] **M2. Shorten the abstract; lead with the validated finding + interval** (observability gap +
  Wilson CI first; methodology second; selection as an explicit null).
- [ ] **M3. Split overlong sentences** (e.g., the §6.5 H4 bullet, 40+ words). Standardize the
  prototype name **`cart`** (define + expand once on first use).

---

## Recommended one-cycle sequence (Path A)

1. C1 reposition (title/abstract/contributions) + M2 abstract + C3(b) demote selection. *(editorial)*
2. C2 expand mining to ≥ 60–100 + Wilson/κ CIs + adjudication + H1 dual-role + subset build-validation.
3. C4 implement the property/layout oracle into the pipeline; re-run H1 (and H2); I3 report FP rate.
4. I6 quantify detection uplift + concrete Qiskit-CI assertion recommendation.
5. I1/I2/I5 fix Table 6, figures, preprint refs; I4 add CIs everywhere.
6. I7/I8 add the two missing threats; M1/M3 trim repetition and long sentences; I11 AI sentence.

Executed well: ~58% → ~80% readiness for a strong quantum-software venue.

---

## Already in hand (lowers the lift)

- Abstract already partly repositioned (leads with methodology + observability); H4 **verified** and
  H1 **detected in isolation** are already in the manuscript; the **isolated-pass property prototype**
  (`scripts/verify_h1_isolated.py`) is ready to generalize for C4/I6; 64-test count already updated.
- The editorial cluster (C1, C3b, I1, I2, I3, I4, I6, I7, I8, I11, M1–M3) can mostly be drafted
  against the current `PAPER.docx` now; the experimental lifts are C2 (mining expansion) and C4
  (oracle wiring), which need your builds/compute.
