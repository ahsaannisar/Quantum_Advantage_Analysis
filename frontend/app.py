import matplotlib
matplotlib.use('Agg')

from flask import Flask, request
import matplotlib.pyplot as plt
import os
import pandas as pd
import time

from backend.search_module import classical_search, quantum_search
from backend.optimization_module import classical_maxcut, quantum_qaoa_simulated
from backend.ml_module import classical_ml, quantum_ml_simulated

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    result_html = ""

    if request.method == "POST":

        os.makedirs("frontend/static", exist_ok=True)
        os.makedirs("results", exist_ok=True)

        # ===============================
        # USER INPUT
        # ===============================
        size_input = request.form["sizes"]
        noise_input = request.form["noise"]

        try:
            sizes = [int(x.strip()) for x in size_input.split(",")]
            noise_levels = [float(x.strip()) for x in noise_input.split(",")]
        except:
            return "<h3>Invalid input format. Use comma separated values.</h3>"

        # ===============================
        # 1️⃣ SEARCH SCALABILITY
        # ===============================
        classical_times = []
        quantum_times = []

        for s in sizes:
            c_res, c_t = classical_search(s, s-1)
            q_res, q_t = quantum_search()
            classical_times.append(c_t)
            quantum_times.append(q_t)

        plt.figure()
        plt.plot(sizes, classical_times, marker='o')
        plt.plot(sizes, quantum_times, marker='o')
        plt.title("Scalability Comparison")
        plt.xlabel("Problem Size")
        plt.ylabel("Execution Time (seconds)")
        plt.legend(["Classical", "Quantum"])
        plt.tight_layout()
        plt.savefig("frontend/static/scalability.png")
        plt.close()

        # ===============================
        # 2️⃣ NOISE IMPACT
        # ===============================
        from qiskit_aer.noise import NoiseModel, depolarizing_error
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator

        noise_times = []

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

            noise_times.append(end - start)

        plt.figure()
        plt.plot(noise_levels, noise_times, marker='o')
        plt.title("Noise Impact on Execution Time")
        plt.xlabel("Noise Level")
        plt.ylabel("Execution Time (seconds)")
        plt.tight_layout()
        plt.savefig("frontend/static/noise.png")
        plt.close()

        # ===============================
        # 3️⃣ OPTIMIZATION
        # ===============================
        c_cut, c_time = classical_maxcut()
        q_cut, q_time = quantum_qaoa_simulated()

        opt_df = pd.DataFrame({
            "Algorithm": ["Classical MaxCut", "Quantum QAOA (Simulated)"],
            "Cut Value": [c_cut, q_cut],
            "Execution Time": [round(c_time,6), round(q_time,6)]
        })

        opt_table = opt_df.to_html(classes="table table-striped table-dark", index=False)

        # ===============================
        # 4️⃣ MACHINE LEARNING
        # ===============================
        c_acc, c_ml_time = classical_ml()
        q_acc, q_ml_time = quantum_ml_simulated()

        plt.figure()
        plt.bar(["Classical ML", "Quantum ML"], [c_ml_time, q_ml_time])
        plt.title("ML Training Time Comparison")
        plt.ylabel("Training Time (seconds)")
        plt.tight_layout()
        plt.savefig("frontend/static/ml.png")
        plt.close()

        ml_df = pd.DataFrame({
            "Model": ["Classical ML", "Quantum ML (Simulated)"],
            "Accuracy": [round(c_acc,3), round(q_acc,3)],
            "Training Time": [round(c_ml_time,6), round(q_ml_time,6)]
        })

        ml_table = ml_df.to_html(classes="table table-striped table-dark", index=False)

        # ===============================
        # 5️⃣ AUTO CONCLUSION
        # ===============================
        if sum(classical_times) < sum(quantum_times):
            conclusion = """
            For the tested problem sizes, classical algorithms outperform 
            quantum implementations due to simulator overhead and noise.
            """
        else:
            conclusion = """
            Quantum methods show scalability advantages as problem size increases.
            """

        result_html = f"""
        <div class="mt-5">

            <h2>📈 Scalability Analysis</h2>
            <img src="/static/scalability.png" class="img-fluid rounded shadow">

            <h2 class="mt-5">⚡ Noise Impact Analysis</h2>
            <img src="/static/noise.png" class="img-fluid rounded shadow">

            <h2 class="mt-5">🔍 Optimization Comparison</h2>
            {opt_table}

            <h2 class="mt-5">🤖 Machine Learning Comparison</h2>
            <img src="/static/ml.png" class="img-fluid rounded shadow">
            {ml_table}

            <h2 class="mt-5"> Conclusion</h2>
            <div class="alert alert-info">
                {conclusion}
            </div>

        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quantum Advantage Research Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-dark text-light">
        <div class="container mt-5">

            <div class="text-center mb-4">
                <h1 class="fw-bold">Quantum Advantage Research Platform</h1>
                <p class="lead">Evaluating When Quantum Algorithms Do Not Provide Practical Benefit</p>
            </div>

            <form method="POST" class="card p-4 bg-secondary shadow-lg">

                <div class="mb-3">
                    <label class="form-label">Enter Problem Sizes (comma separated)</label>
                    <input type="text" name="sizes" class="form-control" placeholder="8,16,32,64,128" required>
                </div>

                <div class="mb-3">
                    <label class="form-label">Enter Noise Levels (comma separated)</label>
                    <input type="text" name="noise" class="form-control" placeholder="0,0.05,0.1,0.2" required>
                </div>

                <button type="submit" class="btn btn-success btn-lg w-100">
                    Run Full Experimental Analysis
                </button>
            </form>

            {result_html}

            <div class="text-center mt-5 text-muted">
                <small>Academic Research Tool - Quantum Performance Evaluation</small>
            </div>

        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
