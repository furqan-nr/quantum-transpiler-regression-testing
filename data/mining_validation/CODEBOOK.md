# Mining classification codebook, transpiler-fix manifestation channels

This codebook governs the independent classification of merged Qiskit transpiler
bug-fix pull requests (label `mod: transpiler`) used in the observability study.
A second rater should classify **independently**, using only the PR title,
description, and linked issues, **without** seeing Rater 1's labels.

## Two judgments per PR

### 1. `manifestation_channel`, the channel through which the fixed fault could be detected
Assign exactly one:

- **output_semantic**, the bug makes the compiled circuit compute a *different
  unitary / different measured output* (e.g. unsafe cancellation, wrong commutation,
  wrong control modifiers, wrong routing of control flow).
- **compilation_failure**, the bug causes a crash, exception, panic, or rejected
  input during transpilation (functional failure), rather than a wrong output.
- **circuit_quality**, the output is semantically correct but *worse* (more 2-qubit
  gates, larger depth, worse layout), a quality regression, not a correctness one.
- **performance**, the bug only affects *compile-time cost* (slower or more memory),
  output and quality unchanged.
- **contract_metadata**, the bug corrupts an internal transpiler **contract or
  metadata** property (e.g. `TranspileLayout`, `final_layout`,
  `virtual_permutation_layout`, `routing_permutation`, circuit `name`) while the
  *layout-applied output unitary remains correct*.
- **determinism**, the bug makes output **non-deterministic** across fixed-seed runs
  (same input, varying result), without a single run being "wrong".
- **global_phase**, the bug drops/alters the **global phase**, which is invisible to
  any equivalence check performed *modulo global phase*.

### 2. `observable_by_output_oracle`, yes / no
Answer **the headline question**: *Could a black-box output-equivalence oracle that
compares the compiled circuit's output map, modulo global phase and modulo qubit-layout
permutation, detect this fault?*

- **yes**, output_semantic, compilation_failure, circuit_quality, performance
  (a wrong/absent output, a crash, a measurably worse circuit, or a measurable slowdown
  are all observable in principle).
- **no**, contract_metadata, determinism, global_phase
  (these leave the layout-applied output map intact, so an output-only oracle cannot see
  them). This **`no` set is the study's key quantity** (output-invisible channels).

## `confidence`, high / medium / low
- **high**, title/description make the channel unambiguous.
- **medium**, channel is clear but some interpretation is needed.
- **low**, genuinely borderline (e.g. an enhancement vs. a fix, or a metadata-vs-quality
  ambiguity); record the reasoning in `notes`.

## Borderline rules (decide consistently)
- A metadata property is corrupted **but** the applied output could differ →
  prefer `contract_metadata` only if the *layout-applied output unitary is correct*;
  otherwise `output_semantic`.
- API/serialization plumbing fixes at the edge of transpiler scope → `compilation_failure`
  if they manifest as a crash; `contract_metadata` if they only affect a property; mark
  `low` confidence.
- "Idle/uncoupled qubit" layout fixes → `circuit_quality` if they change layout quality,
  `compilation_failure` if they cause an edge-case crash.

## Output
Fill `data/mining_validation/rater2_sheet.csv` (channel, observable, confidence, notes),
then run `compute_kappa.py` to obtain Cohen's kappa on both judgments. Reconcile any
disagreements in a short adjudication note and report the agreed labels plus kappa.
