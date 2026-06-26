"""topologies.py — Physical qubit topology definitions."""

from qiskit.transpiler import CouplingMap


def get_topologies(n_qubits: int) -> dict:
    """
    Return a dict of named CouplingMaps scaled to (at least) n_qubits.
    """
    return {
        "Linear Chain": {
            "map": CouplingMap.from_line(n_qubits, bidirectional=True),
            "color": "#E63946",
            "short": "Linear",
            "description": (
                "Qubits in a 1-D chain.\n"
                "Long-range gates need many SWAPs."
            ),
        },
        "Heavy-Hex": {
            # Here the parameter is the "distance" of the heavy-hex lattice, where the distance is the grid's 
            # size parameter that determines the hardware's capacity to detect and correct quantum errors.
            # The number of qubits is n_qubits = (5d^2 - 2d - 1) / 2, where d is the distance.
            "map": CouplingMap.from_heavy_hex(3, bidirectional=True),
            "color": "#2A9D8F",
            "short": "Heavy-Hex",
            "description": (
                "Sparse hex lattice reduces crosstalk.\n"
                "Moderate SWAP overhead for non-local gates."
            ),
        },
        "Full Graph": {
            "map": CouplingMap.from_full(n_qubits),
            "color": "#457B9D",
            "short": "Full Graph",
            "description": (
                "Every qubit connected to every other.\n"
                "Zero routing overhead — theoretical lower bound."
            ),
        },
    }
