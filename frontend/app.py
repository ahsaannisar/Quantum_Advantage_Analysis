import math
from pathlib import Path
import time

from flask import Flask, render_template, request
from matplotlib.figure import Figure
import pandas as pd

from backend.search_module import classical_search, quantum_search
from backend.noise_analysis import noise_comparison
from backend.optimization_module import classical_maxcut, quantum_qaoa_simulated
from backend.ml_module import classical_ml, quantum_ml_simulated

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


@app.route("/", methods=["GET", "POST"])
def home():
    size_input = request.form.get("sizes", "")
    noise_input = request.form.get("noise", "")
    context = {"size_input": size_input, "noise_input": noise_input}

    if request.method == "POST":
        try:
            sizes = [int(x.strip()) for x in size_input.split(",")]
            noise_levels = [float(x.strip()) for x in noise_input.split(",")]
            if any(size <= 0 for size in sizes):
                raise ValueError
            if any(
                not math.isfinite(level) or not 0 <= level <= 4 / 3
                for level in noise_levels
            ):
                raise ValueError
        except ValueError:
            context["error"] = (
                "Use comma-separated positive integers for problem sizes and finite "
                "numbers between 0 and 4/3 for noise levels (e.g. 0,0.05,0.1,0.2)."
            )
            return render_template("index.html", **context), 400

        static_dir = Path(app.static_folder)
        static_dir.mkdir(parents=True, exist_ok=True)

        # The existing quantum circuit stays fixed at two qubits for every size.
        classical_times = []
        quantum_times = []
        for size in sizes:
            _, c_time = classical_search(size, size - 1)
            _, q_time = quantum_search()
            classical_times.append(c_time)
            quantum_times.append(q_time)

        fig = Figure()
        ax = fig.subplots()
        ax.plot(sizes, classical_times, marker="o", label="Classical Search")
        ax.plot(sizes, quantum_times, marker="o", label="Fixed 2-Qubit Circuit")
        ax.set_title("Search Size and Fixed Circuit Execution Times")
        ax.set_xlabel("Classical Search Size")
        ax.set_ylabel("Execution Time (seconds)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(static_dir / "scalability.png")

        noise_levels, noise_times = noise_comparison(noise_levels)
        fig = Figure()
        ax = fig.subplots()
        ax.plot(noise_levels, noise_times, marker="o")
        ax.set_title("Noise Parameter and Simulator Execution Time")
        ax.set_xlabel("Depolarizing Parameter")
        ax.set_ylabel("Execution Time (seconds)")
        fig.tight_layout()
        fig.savefig(static_dir / "noise.png")

        c_cut, c_time = classical_maxcut()
        q_cut, q_time = quantum_qaoa_simulated()
        opt_df = pd.DataFrame({
            "Algorithm": ["Classical MaxCut", "QAOA Placeholder (Random Partition)"],
            "Cut Value": [c_cut, q_cut],
            "Execution Time (seconds)": [c_time, q_time],
        })
        context["opt_table"] = opt_df.to_html(
            classes="table table-striped table-dark", index=False,
            float_format=lambda value: f"{value:.6g}",
        )

        c_acc, c_ml_time = classical_ml()
        q_acc, q_ml_time = quantum_ml_simulated()
        fig = Figure()
        ax = fig.subplots()
        ax.bar(["Classical ML", "Quantum ML Placeholder"], [c_ml_time, q_ml_time])
        ax.set_title("Model Fit and Placeholder Execution Times")
        ax.set_ylabel("Execution Time (seconds)")
        fig.tight_layout()
        fig.savefig(static_dir / "ml.png")

        ml_df = pd.DataFrame({
            "Model": ["Classical ML", "Quantum ML Placeholder (Random Accuracy)"],
            "Accuracy": [round(c_acc, 3), round(q_acc, 3)],
            "Execution Time (seconds)": [c_ml_time, q_ml_time],
        })
        context["ml_table"] = ml_df.to_html(
            classes="table table-striped table-dark", index=False,
            float_format=lambda value: f"{value:.6g}",
        )

        if sum(classical_times) < sum(quantum_times):
            context["conclusion"] = (
                "The summed classical search time was lower than the summed "
                "fixed-circuit simulator time in this run."
            )
        elif sum(classical_times) > sum(quantum_times):
            context["conclusion"] = (
                "The summed fixed-circuit simulator time was lower than the summed "
                "classical search time in this run."
            )
        else:
            context["conclusion"] = "The summed search and simulator times were equal in this run."
        context["run_id"] = time.time_ns()

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
