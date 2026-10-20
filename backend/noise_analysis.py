import time
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def noise_comparison(noise_levels=None):
    if noise_levels is None:
        noise_levels = [0, 0.05, 0.1, 0.2]
    noise_levels = list(noise_levels)
    if not noise_levels or any(
        not math.isfinite(level) or not 0 <= level <= 4 / 3
        for level in noise_levels
    ):
        raise ValueError("Noise levels must be finite numbers between 0 and 4/3.")
    results = []

    for level in noise_levels:
        noise_model = NoiseModel()
        error = depolarizing_error(level, 1)
        noise_model.add_all_qubit_quantum_error(error, ['h'])

        sim = AerSimulator(noise_model=noise_model)
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()

        start = time.perf_counter()
        sim.run(qc, shots=1000).result()
        end = time.perf_counter()

        results.append(end - start)

    return noise_levels, results
