import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def noise_comparison():
    noise_levels = [0, 0.05, 0.1, 0.2]
    results = []

    for level in noise_levels:
        noise_model = NoiseModel()
        error = depolarizing_error(level, 1)
        noise_model.add_all_qubit_quantum_error(error, ['h'])

        sim = AerSimulator(noise_model=noise_model)
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()

        start = time.time()
        sim.run(qc, shots=1000).result()
        end = time.time()

        results.append(end - start)

    return noise_levels, results
