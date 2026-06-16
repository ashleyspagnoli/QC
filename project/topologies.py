"""topologies.py — Physical qubit topology definitions."""

from qiskit.transpiler import CouplingMap


def get_topologies(n_qubits: int) -> dict:
    """
    Return a dict of named CouplingMaps scaled to (at least) n_qubits.

    Keys
    ----
    "Linear Chain"   : worst-case 1-D chain
    "Heavy-Hex"      : IBM Falcon/Eagle production topology
    "Full Graph"     : ideal all-to-all baseline
    """
    return {
        "Linear Chain": {
            "map": CouplingMap.from_line(n_qubits, bidirectional=True),
            "color": "#E63946",
            "short": "Linear",
            "description": (
                "Qubits in a 1-D chain.\n"
                "Only nearest-neighbour CNOTs are native.\n"
                "Long-range gates need many SWAPs."
            ),
            "ibm_device": "ibmq_5_yorktown (early)",
        },
        "Heavy-Hex": {
            "map": CouplingMap.from_heavy_hex(3, bidirectional=True),  # ~7 qubits
            "color": "#2A9D8F",
            "short": "Heavy-Hex",
            "description": (
                "IBM's production topology (Falcon/Eagle/Heron).\n"
                "Sparse hex lattice reduces crosstalk.\n"
                "Moderate SWAP overhead for non-local gates."
            ),
            "ibm_device": "ibm_cairo / ibm_nazca",
        },
        "Full Graph": {
            "map": CouplingMap.from_full(n_qubits),
            "color": "#457B9D",
            "short": "Full Graph",
            "description": (
                "Every qubit connected to every other.\n"
                "Zero routing overhead — theoretical lower bound."
            ),
            "ibm_device": "Ideal / simulator",
        },
    }
