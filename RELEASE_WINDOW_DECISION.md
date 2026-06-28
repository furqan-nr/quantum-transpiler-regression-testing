# Release-Window Decision

**Purpose.** Choose the initial Qiskit release window for the pilot, per METHODOLOGY §0.1
(two-layer pinning: fixed harness + per-event Qiskit-under-test built from source). This document
evaluates candidate windows against four compatibility criteria, presents evidence, and
recommends one window. **It does not create the harness lockfile and does not begin Environment
Setup E1–E4**, those follow approval of this document.

**Date:** 2026-06-25. **Decision status:** **SELECTED, Window C (Qiskit 2.x current line)**,
driven by a target publication date of **early 2027** (see §4). Updated 2026-06-25 from the
initial proposal (which recommended 1.4.x) after the publication date was set.

---

## 1. Evaluation method

For each candidate window the four criteria from the task are:

1. **Build from source**, baseline and candidate revisions build from source (Rust toolchain).
2. **Benchpress smoke**, the selected Benchpress revision collects and runs a small smoke subset.
3. **Pass-manager instrumentation**, callback/instrumentation tracing of executed passes works.
4. **Oracle dependencies**, unitary/statevector equivalence and simulation deps work.

**What was tested empirically vs assessed from documentation.** The sandbox used for evidence is
Linux, **Python 3.10.12**, with PyPI wheel access but **no Rust toolchain**. Therefore criteria
**3 and 4 were tested empirically** (from released wheels); criterion **1 (from-source build) could
not be run here** and is assessed from official requirements, it is the single remaining gate to
confirm on the actual build machine during E3. Criterion **2** is assessed from Benchpress's
dependency manifest plus the empirical confirmation that the transpiler/PassManager API the smoke
subset relies on works on each window.

---

## 2. Candidate windows

| Window | Anchor (verified build tag) | Era | Rationale to consider |
|---|---|---|---|
| **A, Qiskit 1.2.x** | `1.2.4` | mid-2024 | Benchpress-paper era; dense, well-documented transpiler regressions. |
| **B, Qiskit 1.4.x** | `1.4.2` | early 2025 | Last/most-complete 1.x; opt-level-2 default (since 1.3); single stable dependency band. |
| **C, Qiskit 2.x current line (band 2.1 → latest stable minor)** | `2.4.2` (also tested `2.3.1`) | 2025–2026 | Current, actively-maintained major; ~12+ months of in-window history; no within-major API break (start at 2.1, after the 2.0 boundary). |

**Window C is defined as a band, not a single minor.** It spans **2.1 → the latest stable 2.x
minor at E1** (currently 2.4.x; anchor build/instrumentation at `2.4.2`). Semantic versioning
reserves breaking API changes for major versions, so the transpiler API is stable across the band
and the instrumentation/oracle code is portable (verified on 2.3.1 and 2.4.2). Starting at 2.1
(declared fully backward-compatible with 2.0) avoids straddling the 2.0 API-break boundary. It is
"one compatible window" in the METHODOLOGY §0.1 sense: one major, one harness toolchain (Rust ≥ the
highest MSRV in band), one pinned Python.

(“Anchor” = the exact release tag whose wheel was used for the empirical tests below. Per-event
`baseline_sha`/`candidate_sha` for specific historical regressions are identified in Phase 1 and
must fall **within** the chosen window.)

---

## 3. Evidence

### 3.1 Pass-manager instrumentation (criterion 3), TESTED, PASS on all three

Captured executed passes via `generate_preset_pass_manager(...).run(circuit, callback=...)` and
`transpile(..., callback=...)`. The callback receives the pass object, DAG, timing, property set,
and count; collecting `type(pass_).__name__` yields the **actually executed** pass list (satisfies
the §0.3 requirement to instrument rather than infer from filenames).

| Window | API used | Executed passes captured | Sample |
|---|---|---|---|
| A `1.2.4` | `PassManager.run(callback=)` | 38 | ContainsInstruction, UnitarySynthesis, HighLevelSynthesis, BasisTranslator |
| B `1.4.2` | `transpile(callback=)` + `PassManager.run(callback=)` | 44 | …, ElidePermutations, RemoveDiagonalGatesBeforeMeasure |
| C `2.3.1` | `transpile(callback=)` + `PassManager.run(callback=)` | 38 | …, ElidePermutations |
| **C `2.4.2` (selected anchor)** | `transpile(callback=)` + `PassManager.run(callback=)` | 38 | ContainsInstruction, UnitarySynthesis, HighLevelSynthesis, BasisTranslator |

The callback signature is stable across all three (keyword args), so the instrumentation code is
portable across the candidate windows.

### 3.2 Oracle dependencies (criterion 4), TESTED, PASS on all three

| Window | `Operator.equiv` (unitary, modulo global phase) | `Statevector.equiv` |
|---|---|---|
| A `1.2.4` | True | True |
| B `1.4.2` | True | True |
| C `2.3.1` | True | True |
| **C `2.4.2` (selected anchor)** | True | True |

`qiskit.quantum_info.Operator`/`Statevector` ship in Qiskit core (no extra dependency) and provide
the modulo-global-phase comparison the exact-oracle tier needs. Sampled/observable simulation uses
`qiskit-aer` (a standard wheel; listed in `environment/requirements.harness.in`); Aer install was
not exercised in the sandbox due to the per-call time limit and is confirmed in E3.

### 3.3 Benchpress smoke (criterion 2), assessed, LOW RISK

Benchpress's `requirements.txt` (fetched from `Qiskit/benchpress@main`) is **minimal and does not
pin Qiskit**:

```
pytest
pytest-memray
wrapt_timeout_decorator
packaging>=20
```

Implications:
- The harness (pytest + Benchpress) is **decoupled** from the Qiskit version, exactly the
  two-layer model in METHODOLOGY §0.1. Any of the three windows satisfies Benchpress's own deps.
- Benchpress uses standard **pytest collection**, aligning with the Phase 0 manifest enumeration
  (“pytest collection or a Benchpress adapter”).
- Residual risk: individual Benchpress *test bodies* call a specific Qiskit transpiler API; on a
  very new or very old Qiskit some tests may use changed APIs. The core API the smoke subset needs
  (`transpile`, `generate_preset_pass_manager`, `CouplingMap`, `quantum_info`) was confirmed
  working on all three windows (§3.1–3.2), so a small smoke subset is expected to collect and run.
  Full collection is confirmed in E3.

### 3.4 Build from source (criterion 1), NOT verifiable in sandbox; per-window risk

Qiskit requires a **Rust toolchain** to build from source (Rust became a build dependency in the
terra→1.0 transition). Documented requirements: `pip >= 19`, `setuptools-rust >= 1.9`, and a Rust
compiler; rustworkx requires Rust ≥ 1.64; Qiskit core’s minimum supported Rust version (MSRV) is
not part of the back-compat guarantee and **rises at minor/major releases**. From Qiskit 2.0,
building requires a 64-bit platform.

The sandbox has **no Rust**, so no from-source build was performed here. Per-window risk:

| Window | From-source build risk | Notes |
|---|---|---|
| A `1.2.x` | Low | Mature deps; older, well-understood MSRV; widest wheel/build history. |
| B `1.4.x` | Low | Last 1.x; one stable MSRV across the 1.3→1.4 band → simplest single-window build. |
| C `2.3.x` | Low–Medium | Higher MSRV; 64-bit-only; newer build deps, must match harness toolchain. |

This is the **one gate to confirm in E3** before locking: build `baseline_sha` and `candidate_sha`
for at least one event in the chosen window from source against the fixed harness.

### 3.5 Support / maintenance context

- **1.x**, `1.4` is the last 1.x minor line; 1.x bug-fix support ended Oct 2025 and **security
  support ended ~April 2026** (i.e., already closed as of this date). Acceptable for an *offline,
  pinned, build-from-source research pilot*, we are not deploying and do not need upstream patches.
- **2.x**, current actively maintained major (2.3 stable; 2.4.x latest patch line; 2.5 in rc).
  Qiskit 3.0 is likely later in 2026, which would shorten 2.x’s “current” status during the pilot.

---

## 4. Recommendation

### 4.0 Decision driver: publication in early 2027

The target submission date (**early 2027**) is the deciding factor and overrides the initial
1.4.x recommendation. A paper published in 2027 that studies an **end-of-life** Qiskit line invites
a direct reviewer objection: Qiskit 1.x bug-fix support ended Oct 2025 and **security support ended
~April 2026**, by submission the 1.4 line would be ~9–12 months out of support. Because the
method’s entire value proposition is *CI relevance for real transpiler development*, demonstrating
it on an unmaintained line undercuts external validity. Choosing the **current, maintained 2.x
line** keeps the published results relevant to the Qiskit developers and CI pipelines the work
targets.

Timeline fit: the 3-month pilot (≈ Jun–Sep 2026) plus write-up lands comfortably before early 2027,
and the 2.x line has accumulated ~12+ months of development (2.0 Mar 2025 → 2.4 Apr 2026), giving
ample in-window historical regressions, the original "few settled regressions" concern for 2.x no
longer holds in mid-2026.

### 4.1 Selected window: C, Qiskit 2.x current line (band 2.1 → latest stable minor; anchor `2.4.2`)

Supported by evidence, not assumption:

1. **Publication relevance.** Current, actively-maintained major at submission; avoids the EOL
   objection that 1.x would draw in 2027. (§3.5)
2. **Instrumentation and oracles verified** on both `2.3.1` and the selected anchor `2.4.2`
   (§3.1–3.2); callback API is identical to 1.x, so instrumentation code is portable.
3. **No within-major API break.** Starting the band at 2.1 (fully backward-compatible with 2.0)
   means one stable transpiler API across the window; the 2.0 boundary is excluded.
4. **Sufficient historical-regression density.** ~12+ months of 2.x transpiler development provides
   documented regressions whose baseline/candidate both fall in-window.
5. **Harness still Qiskit-decoupled** (§3.3), so Benchpress runs unchanged.

At E1, anchor to the **latest stable 2.x minor** available then (currently 2.4.x; 2.5 is in rc,
do not pin an rc). Allow baseline *parent* commits to reach back within the 2.x band as needed.

### 4.2 Fallbacks
- **If 2.x historical regressions are harder to reproduce than expected in Phase 1**, supplement
  with controlled mutations on a 2.x base (METHODOLOGY §1.4–1.5) before widening the window,
  keeping results on the current line.
- **Window B (`1.4.x`) is the contingency only** if a 2.x from-source build proves infeasible on the
  laptop’s toolchain in E3; if used, the paper must explicitly justify the legacy line.

### 4.3 Implication for Qiskit 3.0
Qiskit 3.0 is likely to ship in late 2026. If it lands before submission, the pinned 2.x study is
still a *recent, until-recently-current, and supported* line (previous major keeps 6-month bug /
1-year security support), which remains defensible. Re-anchoring the pilot to 3.0 mid-study is **not**
advised, it would cross a major API break and reset the from-source build/instrumentation
validation. Note 3.0 coverage as Phase 6 future work instead.

---

## 5. Known limitations of this recommendation

- **From-source build is unconfirmed** (no Rust in the evaluation sandbox). E3 must build one
  event’s baseline+candidate from source before the lock is finalized. 2.x has a **higher Rust MSRV**
  than 1.x and is **64-bit-only**, install a recent Rust toolchain meeting the highest MSRV in the
  2.1→2.4 band; if it conflicts with the laptop toolchain, fall back to Window B (§4.2).
- **MSRV may rise across the 2.x band.** Pin the harness Rust to satisfy the newest in-window minor;
  older in-window builds remain compatible with a newer Rust.
- **Python pin pending.** Evidence was gathered on Python 3.10; the harness Python is fixed in E1
  and must be one supported across 2.1–2.4 and by `qiskit-aer` (recommend 3.11 or 3.12, confirm).
- **Specific event SHAs not yet enumerated.** Concrete `baseline_sha`/`candidate_sha` per historical
  regression are selected in Phase 1 and must fall within the 2.x window; this document fixes only the
  window and its verified build anchor (`2.4.2`).
- **Benchpress full collection unconfirmed** beyond the shared core API; confirm a smoke subset in
  E3.
- **Qiskit 3.0 timing risk** (§4.3): if 3.0 ships before submission, note 2.x as the
  until-recently-current line; do not re-anchor mid-study.

---

## 6. Decision checklist

- [x] **Selected: Window C, Qiskit 2.x current line** (band 2.1 → latest stable minor; anchor
  `2.4.2`), driven by the early-2027 publication date (§4.0).
- [ ] Confirm harness Python version to pin in E1 (recommend 3.11 or 3.12).
- [ ] Authorize E3 to validate the 2.x from-source build (the one unverified gate, incl. Rust MSRV
  + 64-bit) before locking; fall back to Window B only if that build fails.

> Next step (held pending your go-ahead): Environment Setup E1–E4, build the fixed harness,
> generate `environment/requirements.lock`, define the per-event 2.x build recipe, and confirm the
> from-source build + statevector feasibility. Per your earlier instruction, I will not generate the
> lockfile or begin E1–E4 without explicit approval.

---

## Sources

- [Qiskit releases](https://github.com/Qiskit/qiskit/releases) · [Qiskit roadmap](https://github.com/Qiskit/qiskit/wiki/Roadmap)
- [Qiskit SDK version strategy](https://quantum.cloud.ibm.com/docs/en/open-source/qiskit-sdk-version-strategy)
- [Install the Qiskit SDK from source](https://docs.quantum.ibm.com/guides/install-qiskit-source) · [Rust now required to build terra](https://github.com/Qiskit/feedback/discussions/23)
- [Qiskit/benchpress](https://github.com/Qiskit/benchpress) · [benchpress requirements.txt](https://raw.githubusercontent.com/Qiskit/benchpress/main/requirements.txt) · [Benchpress paper (Nature Comput. Sci.)](https://www.nature.com/articles/s43588-025-00792-y)
- Empirical tests: local sandbox (Linux, Python 3.10.12), Qiskit `1.2.4`, `1.4.2`, `2.3.1` wheels, instrumentation + oracle results in §3.1–3.2.
