import time
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def classical_search(size, target):
    arr = list(range(size))
    start = time.time()
    found = target in arr
    end = time.time()
    return found, end - start

def quantum_search():
    sim = AerSimulator()
    qc = QuantumCircuit(2)
    qc.h([0,1])
    qc.cz(0,1)
    qc.h([0,1])
    qc.measure_all()

    start = time.time()
    result = sim.run(qc, shots=1024).result()
    end = time.time()

    counts = result.get_counts()
    return counts, end - start
