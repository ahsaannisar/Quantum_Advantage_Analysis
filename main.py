from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from backend.search_module import classical_search, quantum_search
from backend.factoring_module import classical_factor


RESULTS_DIR = Path(__file__).resolve().parent / "results"


def read_integer(prompt, minimum):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print(f"Please enter an integer of at least {minimum}.")
            continue
        if value >= minimum:
            return value
        print(f"Please enter an integer of at least {minimum}.")


def main():
    print("\n===== Quantum Advantage Analysis =====")

    size = read_integer("\nEnter search size (e.g. 32, 64, 128): ", 1)
    target = size - 1
    c_result, c_time = classical_search(size, target)
    q_result, q_time = quantum_search()

    print("\n--- SEARCH RESULTS ---")
    print("Classical Output:", c_result)
    print("Classical Time:", c_time)
    print("Quantum Circuit Counts:", q_result)
    print("Quantum Simulator Time:", q_time)
    print("The quantum circuit is fixed at two qubits and does not use the search size or target.")

    num = read_integer("\nEnter number to factor (e.g. 15, 21, 35): ", 2)
    factors, f_time = classical_factor(num)
    print("\n--- FACTORIZATION RESULTS ---")
    print("Factors:", factors if factors is not None else "Prime; no non-trivial factor pair.")
    print("Time:", f_time)

    df = pd.DataFrame({
        "Algorithm": ["Classical Search", "Quantum Search"],
        "Execution Time": [c_time, q_time],
    })
    print("\n--- PERFORMANCE TABLE ---")
    print(df)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "performance_table.csv", index=False)

    fig, ax = plt.subplots()
    ax.bar(["Classical Search", "Fixed Quantum Circuit"], [c_time, q_time])
    ax.set_title("Search and Fixed Circuit Execution Times")
    ax.set_ylabel("Execution Time (seconds)")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "search_graph.png")
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
