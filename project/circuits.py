"""circuits.py - Logical quantum circuit definitions."""

from math import pi

from qiskit import QuantumCircuit

def build_qft(n: int, *, do_swaps: bool = True) -> QuantumCircuit:
    """Standard n-qubit Quantum Fourier Transform circuit."""
    qc = QuantumCircuit(n, name=f"QFT-{n}")

    for target in range(n):
        qc.h(target)
        for control in range(target + 1, n):
            angle = pi / (2 ** (control - target))
            qc.cp(angle, control, target)

    if do_swaps:
        for i in range(n // 2):
            qc.swap(i, n - i - 1)

    return qc