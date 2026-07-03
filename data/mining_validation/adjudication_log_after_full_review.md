# Adjudication log — rater disagreements (seed corpus, n=26)

Decisions for the 7 PRs where Rater 1 and Rater 2 differed. 'ADJUDICATED' = settled; 'PROPOSED' = applied to `corpus.csv` pending your review; 'PARTIAL' = observable settled, channel pending; 'OPEN' = needs author/developer input. Edit freely.

| PR | title | R1 | R2 | decision (channel/observable) | status & reason |
|---|---|---|---|---|---|
| 14603 | Fix ElidePermutations pass in the presence of  | contract_metadata/no | output_semantic/yes | contract_metadata/no | ADJUDICATED: built-from-source H1 evidence — output oracle passes buggy build; metadata (virtual_permutation_layout) corrupted. |
| 14938 | Fix VF2 layout allocation with idle qubits | circuit_quality/yes | contract_metadata/no | contract_metadata/no | PROPOSED: R1 flagged quality-vs-metadata ambiguous; layout-applied output correct -> contract_metadata/no. |
| 13820 | Delegate BasePass.__call__ to PassManager.run | contract_metadata/no | compilation_failure/yes | compilation_failure/yes | PROPOSED: direct BasePass.__call__ raises -> functional failure, observable. |
| 15258 | Fix reuse of ConsolidateBlocks instances | output_semantic/yes | compilation_failure/yes | ?/yes | PARTIAL: both raters observable=yes (final=yes). Channel pending: output_semantic (R1) vs compilation_failure (R2) — needs author check of reuse-of-instances effect. |
| 14667 | Restore correct max_trials behaviour for VF2La | circuit_quality/yes | performance/yes | ?/yes | PARTIAL: both observable=yes (final=yes). Channel pending: circuit_quality (R1) vs performance (R2). |
| 13874 | Use average gate fidelity in the commutation c | circuit_quality/yes | output_semantic/yes | ?/yes | PARTIAL: both observable=yes (final=yes). Channel pending: circuit_quality (R1) vs output_semantic (R2). |
| 14041 | Fix deepcopy/pickle of DAGCircuit variable IO  | compilation_failure/yes | contract_metadata/no | ?/? | OPEN: borderline transpiler scope (DAGCircuit deepcopy/pickle, serialization). Needs author adjudication; left blank. |

---

## Binary adjudication review (2026-06-29)

The following decisions are evidence-based and supersede only the **binary-status** portions of earlier
`PROPOSED`/`OPEN` records. Raw rater labels remain unchanged.

| PR | channel / observable | updated status | evidence summary |
|---|---|---|---|
| 14603 | contract_metadata / no | ADJUDICATED (retained) | Prior built-from-source H1 oracle result: layout-applied output oracle passes the buggy build; `virtual_permutation_layout` is corrupt. |
| 13833 | contract_metadata / no | ADJUDICATED | Regression path compiles successfully; incomplete final routing permutation later makes `final_index_layout` raise `KeyError`. |
| 14041 | contract_metadata / no | ADJUDICATED_LOW_CONFIDENCE | deepcopy/pickle reconstructs Var output nodes as input nodes; no transpilation crash was evidenced. Codebook v2 edge-of-scope rule applies. |
| 13820 | compilation_failure / yes | ADJUDICATED | Direct pass invocation skipped `requires`; regression test requires the dependency to run before the transformation executes. |
| 14938 | contract_metadata / no | ADJUDICATED | Idle qubits were absent from `Layout`; the compiled output mapping is not the issue, but `TranspileLayout` consumers can fail after compilation. |

Direct evidence links are recorded in `three_rater_audit_adjudicated_binary.csv` and
`binary_adjudication_evidence.md`.
---

## Channel adjudication review (2026-06-29)

These decisions settle the remaining channel disputes using PR/issue evidence and the ordered
Codebook v2 rules. Raw rater labels remain unchanged.

| PR | final channel / observable | corpus disposition | status | reason |
|---|---|---|---|---|
| 15875 | compilation_failure / yes | include | ADJUDICATED | Unsupported instructions remained in nested control-flow blocks; linked report records AerError at execution. |
| 14667 | compilation_failure / yes | include | ADJUDICATED_MULTI_TRIGGER | `None` also caused unbounded search, but the evidenced negative-`max_trials` trigger raised an error; crash/rejection rule takes priority. |
| 13874 | output_semantic / yes | include | ADJUDICATED | Linked reproducer shows `Operator(qc).equiv(tqc)` is false for a small-angle RY circuit. |
| 15258 | compilation_failure / yes | include | ADJUDICATED | Linked reproducer records a Rust `PanicException` while transpiling multiple circuits. |
| 14120 | performance / yes (diagnostic only) | exclude_not_bugfix | EXCLUDED_NOT_BUGFIX | It implements a feature request, not a bug fix. Runtime overhead is documented; no demonstrated worse emitted circuit. |

The authoritative traceability record is `three_rater_audit_adjudicated_channels.csv`;
the supporting rationale is in `channel_adjudication_evidence.md`.
