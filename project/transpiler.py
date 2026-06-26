"""transpiler.py - Transpilation helpers and metric extraction."""

import warnings
from collections import OrderedDict

from qiskit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit.transpiler import CouplingMap

warnings.filterwarnings("ignore")

BASIS_GATES  = ["cx", "u"]
OPT_LEVELS   = [0, 1, 2, 3]
SEED         = 42


def _basis_cx_count(logical: QuantumCircuit) -> int:
    """CX count needed by the logical circuit before topology routing."""
    baseline = transpile(
        logical,
        basis_gates=BASIS_GATES,
        optimization_level=0,
        seed_transpiler=SEED,
    )
    return baseline.count_ops().get("cx", 0)


def _format_ops(ops: OrderedDict) -> str:
    return "  ".join(f"{gate}={count}" for gate, count in ops.items())


def _extract_metrics(tc: QuantumCircuit, baseline_cx: int) -> dict:
    ops: OrderedDict = tc.count_ops()
    cx_count = ops.get("cx",   0)
    u_count = ops.get("u",    0)
    swap_count = ops.get("swap", 0)
    total_gates = sum(v for k, v in ops.items() if k not in ("measure", "barrier"))
    extra_cx = max(cx_count - baseline_cx, 0)
    swap_est = extra_cx // 3          # each SWAP decomposes into ~3 CX
    return {
        "depth":       tc.depth(),
        "cx":          cx_count,
        "u":           u_count,
        "swap":        swap_count,
        "swap_est":    swap_est,
        "total_gates": total_gates,
        "circuit":     tc,
        "ops":         dict(ops),
    }


def run_transpilation(logical: QuantumCircuit, topologies: dict) -> dict:
    """
    Transpile `logical` onto every topology at every optimisation level.
    """
    baseline_cx = _basis_cx_count(logical)
    results = {}
    for tname, topo in topologies.items():
        results[tname] = {}
        for opt in OPT_LEVELS:
            tc = transpile(
                logical,
                coupling_map=topo["map"],
                basis_gates=BASIS_GATES,
                optimization_level=opt,
                seed_transpiler=SEED,
            )
            results[tname][opt] = _extract_metrics(tc, baseline_cx)
    return results


def print_report(logical: QuantumCircuit, topologies: dict, results: dict) -> None:
    """Pretty-print a text summary table."""
    divider = "=" * 72
    lops = logical.count_ops()
    baseline_cx = _basis_cx_count(logical)
    print(divider)
    print(f"  {logical.name} Transpilation Report  |  basis: {BASIS_GATES}")
    print(divider)
    print(
        f"\nLogical circuit  →  depth={logical.depth()}  "
        f"{_format_ops(lops)}\n"
        f"Topology-free basis decomposition  →  cx={baseline_cx}\n"
    )
    hdr = f"{'Topology':<10}{'Opt':>4}  {'Depth':>6}  {'CX':>5}  {'U':>5}  {'SWAP≈':>6}  {'Total':>6}"
    print(hdr)
    print("-" * len(hdr))
    for tname, by_opt in results.items():
        short = topologies[tname]["short"]
        for opt, m in by_opt.items():
            print(
                f"{short:<10}{opt:>4}  {m['depth']:>6}  {m['cx']:>5}  "
                f"{m['u']:>5}  {m['swap_est']:>6}  {m['total_gates']:>6}"
            )
        print()
