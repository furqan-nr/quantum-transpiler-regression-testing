"""Targeted regression-trigger units (SEPARATE category; complements generic Benchpress units).

These are NOT generic circuit families. Each is the smallest deterministic circuit that exercises a
specific historical fault's bug path, taken from (or derived from) that fix PR's own regression
test, so its provenance is canonical. They are tagged `test_origin = "targeted_regression_trigger"`
and kept distinct from generic units in all data and reporting (METHODOLOGY Appendix D).

IMPORTANT: the H1–H3 faults existed only in dev commits between releases (never shipped in a release
wheel), so they cannot be confirmed against PyPI wheels — only the exact from-source candidate SHA
reproduces them. An event is called `verified` only after its targeted unit triggers the
buggy candidate build and NOT the fixed baseline build (the local from-source step).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Callable

from qiskit import QuantumCircuit
from qiskit.circuit.library import PermutationGate


@dataclass(frozen=True)
class TargetedUnit:
    test_id: str
    target_fault_id: str
    target_pass_or_component: str
    trigger_rationale: str
    oracle_type: str                       # semantic / property / structural
    expected_baseline_behavior: str
    expected_candidate_behavior: str
    backend_id: str                        # "none" => no coupling map
    opt_level: int
    test_available_sha: str = ""           # first commit at which this test existed (the fix)
    test_origin: str = "targeted_regression_trigger"
    test_provenance: str = "extracted_from_fix"   # pre_existing | extracted_from_fix | synthesized
    available_before_candidate: bool = False      # extracted from the FIX => after candidate => not CI-eligible

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---- minimal deterministic trigger circuits (canonical, from each fix's regression test) -------

def _h1_elide_permutations() -> QuantumCircuit:
    # PR #14603 regression test: swaps + a PermutationGate on overlapping qubits.
    qc = QuantumCircuit(5)
    qc.h(1)
    qc.swap(1, 2)
    qc.swap(4, 3)
    qc.append(PermutationGate([1, 2, 0]), [1, 2, 3])
    return qc


def _h2_final_layout_composition() -> QuantumCircuit:
    # PR #14919 spirit: an all-to-all circuit composed with its inverse => identity, so any routing
    # permutation must compose back to identity. Routed on a constrained map, multiple passes set
    # final_layout; a wrong composition breaks the identity (caught by the semantic oracle).
    n = 5
    qc = QuantumCircuit(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                qc.cx(i, j)
    qc.barrier()
    qc.compose(qc.inverse(), qc.qubits, inplace=True)
    return qc


def _h3_vf2_all_1q() -> QuantumCircuit:
    # PR #14730 regression test: a circuit whose active qubits carry only single-qubit gates.
    qc = QuantumCircuit(3)
    for i in range(3):
        qc.rx(3.14159, i)
    qc.measure_all()
    return qc


_BUILDERS: dict[str, Callable[[], QuantumCircuit]] = {
    "trig-h1-elide-permutations": _h1_elide_permutations,
    "trig-h2-final-layout-composition": _h2_final_layout_composition,
    "trig-h3-vf2-all-1q": _h3_vf2_all_1q,
}

TARGETED_UNITS: dict[str, TargetedUnit] = {
    "trig-h1-elide-permutations": TargetedUnit(
        test_id="trig-h1-elide-permutations",
        target_fault_id="qiskit-pr-14603-elide-permutations",
        target_pass_or_component="ElidePermutations (optimization)",
        trigger_rationale="PermutationGate over qubits overlapping prior swaps forces ElidePermutations "
                          "to update the qubit mapping; the buggy version mislabels it.",
        oracle_type="semantic",
        expected_baseline_behavior="Operator.from_circuit(transpiled) equiv Operator(original)",
        expected_candidate_behavior="NOT equivalent (wrong mapping / TranspileLayout)",
        backend_id="line", opt_level=3, test_available_sha="96fda18888de4492f37ccdb93faf15dc014c99eb"),
    "trig-h2-final-layout-composition": TargetedUnit(
        test_id="trig-h2-final-layout-composition",
        target_fault_id="qiskit-pr-14919-final-layout",
        target_pass_or_component="routing final_layout composition (SabreSwap/BasicSwap/LookaheadSwap)",
        trigger_rationale="An identity circuit (all-to-all CX then its inverse) routed on a constrained "
                          "map; multiple passes set final_layout, so a wrong composition breaks identity.",
        oracle_type="semantic",
        expected_baseline_behavior="transpiled equiv original (identity preserved)",
        expected_candidate_behavior="NOT equivalent (final_layout composed incorrectly)",
        backend_id="line", opt_level=3, test_available_sha="dfcc5c6ce87fa424c8fd7abf22baba9e8750fa66"),
    "trig-h3-vf2-all-1q": TargetedUnit(
        test_id="trig-h3-vf2-all-1q",
        target_fault_id="qiskit-pr-14730-vf2layout-determinism",
        target_pass_or_component="VF2Layout (layout) determinism",
        trigger_rationale="All active qubits carry only single-qubit gates, which exposed the "
                          "non-deterministic VF2Layout ordering even with a fixed seed.",
        oracle_type="property",   # determinism: repeated fixed-seed runs must agree
        expected_baseline_behavior="repeated fixed-seed transpilations are identical",
        expected_candidate_behavior="repeated runs differ (non-deterministic layout)",
        backend_id="heavy_hex", opt_level=1, test_available_sha="d33ef5335e05523e35a29530dbc389c52c8e7bc7"),
}


def build_targeted(test_id: str) -> QuantumCircuit:
    if test_id not in _BUILDERS:
        raise KeyError(f"unknown targeted trigger {test_id!r}; known: {sorted(_BUILDERS)}")
    return _BUILDERS[test_id]()


def units_for_fault(fault_id: str) -> list[TargetedUnit]:
    return [u for u in TARGETED_UNITS.values() if u.target_fault_id == fault_id]
