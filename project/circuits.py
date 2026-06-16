"""circuits.py - Logical quantum circuit definitions."""

from math import pi

from qiskit import QuantumCircuit


def build_ghz(n: int) -> QuantumCircuit:
    """Standard n-qubit GHZ state: H on q0, then a CNOT chain."""
    qc = QuantumCircuit(n, name=f"GHZ-{n}")
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc


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

    qc.measure_all()
    return qc


def build_w_state(n: int) -> QuantumCircuit:
    """
    Approximate W-state for reference (uses a standard decomposition).
    Not used in the main analysis but exported for experimentation.
    """
    qc = QuantumCircuit(n, name=f"W-{n}")
    qc.x(0)
    for i in range(n - 1):
        theta = 2 * __import__("math").acos((1 / (n - i)) ** 0.5)
        qc.ry(theta, i)
        qc.cx(i, i + 1)
        qc.cx(i + 1, i)
    qc.measure_all()
    return qc
