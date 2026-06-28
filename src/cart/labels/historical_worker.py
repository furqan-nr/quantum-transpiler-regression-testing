"""Per-event worker — runs INSIDE a per-event from-source venv (its own Qiskit revision).

Transpiles one test unit with that venv's Qiskit and writes the output circuit (QPY) + timing,
or the natural exception if transpilation fails. Invoked as a subprocess by historical_runner with
PYTHONPATH=src so `cart.manifest.*` is importable; it imports only Qiskit + numpy-backed helpers
(no yaml/pandas), so it runs in the lean per-event venv.

Usage:
  python -m cart.labels.historical_worker --family qft --n 8 --backend line \
      --opt 1 --basis cx,rz,sx,x --seed 1234 --out /path/out
"""
from __future__ import annotations

import argparse
import json
import time
import traceback
from pathlib import Path


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="cart.labels.historical_worker")
    p.add_argument("--family", default=None)            # generic circuit family
    p.add_argument("--targeted", default=None)          # targeted-trigger unit id (alternative)
    p.add_argument("--n", type=int, default=0)
    p.add_argument("--backend", required=True)          # "none" => no coupling map
    p.add_argument("--opt", type=int, required=True)
    p.add_argument("--basis", default="cx,rz,sx,x")
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    basis = args.basis.split(",")

    import qiskit
    from qiskit.transpiler import generate_preset_pass_manager
    from cart.manifest.backends import coupling_map_for

    meta = {"qiskit_version": qiskit.__version__, "family": args.family,
            "targeted": args.targeted, "backend": args.backend, "opt": args.opt,
            "basis": basis, "seed": args.seed}

    if args.targeted:
        from cart.manifest.targeted import build_targeted
        circ = build_targeted(args.targeted)
    else:
        from cart.manifest.circuits import build
        circ = build(args.family, args.n, seed=args.seed, measured=False)
    cmap = None if args.backend == "none" else coupling_map_for(args.backend, circ.num_qubits)
    pm = generate_preset_pass_manager(optimization_level=args.opt, coupling_map=cmap,
                                      basis_gates=basis, seed_transpiler=args.seed)
    try:
        c0 = time.process_time()       # CPU process time — stable cost-calibration metric
        t0 = time.perf_counter()       # wall-clock — secondary reference
        tqc = pm.run(circ)
        meta["transpile_time_s"] = time.perf_counter() - t0
        meta["cpu_time_s"] = time.process_time() - c0
        from qiskit import qpy
        with open(out / "circuit.qpy", "wb") as fh:
            qpy.dump(tqc, fh)
        meta["status"] = "ok"
    except Exception as exc:  # natural transpilation failure (functional fault)
        meta["status"] = "error"
        meta["error_type"] = type(exc).__name__
        meta["error"] = str(exc)[:500]
        meta["traceback"] = traceback.format_exc()[-1500:]

    (out / "worker.json").write_text(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
