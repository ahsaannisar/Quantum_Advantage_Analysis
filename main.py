import matplotlib.pyplot as plt
import pandas as pd
from backend.search_module import classical_search, quantum_search
from backend.optimization_module import classical_maxcut
from backend.factoring_module import classical_factor

print("\n===== Quantum Advantage Analysis =====")

# ---- SEARCH INPUT ----
size = int(input("\nEnter search size (e.g. 32, 64, 128): "))
target = size - 1

c_result, c_time = classical_search(size, target)
q_result, q_time = quantum_search()

print("\n--- SEARCH RESULTS ---")
print("Classical Output:", c_result)
print("Classical Time:", c_time)
print("Quantum Output:", q_result)
print("Quantum Time:", q_time)

# ---- FACTORIZATION INPUT ----
num = int(input("\nEnter number to factor (e.g. 15, 21, 35): "))
factors, f_time = classical_factor(num)

print("\n--- FACTORIZATION RESULTS ---")
print("Factors:", factors)
print("Time:", f_time)

# ---- CREATE TABLE ----
data = {
    "Algorithm": ["Classical Search", "Quantum Search"],
    "Execution Time": [c_time, q_time]
}

df = pd.DataFrame(data)
print("\n--- PERFORMANCE TABLE ---")
print(df)

df.to_csv("results/performance_table.csv", index=False)

# ---- CREATE GRAPH ----
plt.bar(["Classical", "Quantum"], [c_time, q_time])
plt.title("Search Time Comparison")
plt.ylabel("Execution Time (seconds)")
plt.savefig("results/search_graph.png")
plt.show()
