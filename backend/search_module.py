import time
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def classical_search(size, target):
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise ValueError("Search size must be a positive integer.")
    arr = list(range(size))
    start = time.perf_counter()
    found = target in arr
    end = time.perf_counter()
    return found, end - start

def quantum_search():
    sim = AerSimulator()
    qc = QuantumCircuit(2)
    qc.h([0,1])
    qc.cz(0,1)
    qc.h([0,1])
    qc.measure_all()

    start = time.perf_counter()
    result = sim.run(qc, shots=1024).result()
    end = time.perf_counter()

    counts = result.get_counts()
    return counts, end - start
