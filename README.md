# Quantum Advantage Analysis

Quantum Advantage Analysis is a Python learning project that explores classical algorithm execution times alongside small quantum circuit simulations and illustrative quantum-labelled placeholders. It provides a terminal workflow and a Flask web interface with charts and comparison tables.

The project asks: **what does the cost of running a classical algorithm look like next to the cost of a quantum simulator or a simulated overhead example?** Its current experiments are useful for exploring implementation overhead, but they do **not** establish quantum advantage, quantum scalability, or a general classical-versus-quantum performance ranking.

The existing algorithms, circuit gates, model configuration, shot counts, random behavior, and artificial delays are preserved. No replacement search algorithm, QAOA implementation, quantum ML model, or quantum factoring algorithm has been added.

## What the project actually runs

| Experiment | Existing implementation | What the result means |
| --- | --- | --- |
| Classical search | Creates `list(range(size))`, then checks `target in arr`. Both workflows use `target = size - 1`. | A Boolean result and the time spent checking list membership. List construction is outside the timer. |
| Quantum-labelled search | A fixed two-qubit circuit: Hadamard on both qubits, controlled-Z, Hadamard on both qubits, then measurement; 1,024 shots on `AerSimulator`. | Measurement counts and simulator execution time. The circuit accepts neither a search size nor a target and does not implement a complete Grover search. |
| Classical factorization | Trial division from `2` through `n - 1`, returning the first divisor pair. | One non-trivial factor pair, or `None` for a prime. This is not a full prime factor decomposition. Available in the terminal workflow. |
| Classical MaxCut | Exhaustively evaluates all 16 bit assignments of the four-node complete graph, `K4`. | The maximum number of crossing edges; the exact answer is `4`. |
| QAOA-labelled placeholder | Sleeps for 0.2 seconds, chooses a random partition of the same `K4`, and counts crossing edges. | A random cut value (`0`, `3`, or `4`) and elapsed time including the delay. No QAOA circuit or variational optimization runs. |
| Classical ML | Loads Iris, makes a random 70/30 train/test split, and fits `LogisticRegression(max_iter=200)`. | Test-set accuracy and model fitting time. Loading, splitting, and scoring are outside the timer. |
| Quantum ML placeholder | Loads/splits Iris, sleeps for 0.3 seconds, and returns `0.85 + random.uniform(-0.05, 0.05)`. | A generated accuracy value around `0.80–0.90` and elapsed time including the delay. No model is trained or evaluated. |
| Noise experiment | Runs a one-qubit Hadamard-and-measure circuit with depolarizing error attached to the Hadamard gate, using 1,000 shots. | Simulator execution time at each noise parameter. Measurement counts and accuracy are not reported. |

The quantum simulations run locally on a classical computer through Qiskit Aer. No quantum hardware, account, API key, or external dataset download is required. Iris is provided by scikit-learn.

## Project layout

```text
Quantum_Advantage_Analysis/
├── main.py                         # Interactive terminal workflow
├── requirements.txt                # Direct dependencies, pinned to tested versions
├── README.md
├── backend/
│   ├── __init__.py
│   ├── search_module.py            # List search and fixed two-qubit circuit
│   ├── factoring_module.py         # Classical trial division
│   ├── optimization_module.py      # Exact K4 MaxCut and random-cut placeholder
│   ├── ml_module.py                # Iris logistic regression and ML placeholder
│   └── noise_analysis.py           # One-qubit depolarizing-noise timing
├── frontend/
│   ├── __init__.py
│   ├── app.py                      # Flask route and experiment orchestration
│   ├── templates/
│   │   └── index.html              # Form, charts, tables, and interpretation
│   └── static/
│       ├── scalability.png         # Latest web search/circuit timing chart
│       ├── noise.png               # Latest web noise timing chart
│       ├── ml.png                  # Latest web ML/placeholder timing chart
│       └── web_graph.png           # Legacy asset; not used by the current page
├── results/
│   ├── performance_table.csv       # Latest terminal search timing table
│   └── search_graph.png            # Latest terminal search/circuit timing chart
└── tests/
    └── test_project.py             # Algorithm, input, web, and terminal regression checks
```

`venv/`, if present, is a local environment rather than portable project source. The terminal workflow creates `results/` if it is missing; the web workflow creates its static output directory if needed. Output locations are resolved relative to the application files, independently of the shell's working directory.

## Setup from zero

The project was checked with **Python 3.14.0** and the versions in `requirements.txt`. Use Python 3.11 or newer for this dependency set; other Python versions have not been validated in this review.

From the project directory on macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

On Windows, create the environment with `py -m venv venv` and activate it in PowerShell with `venv\Scripts\Activate.ps1`, then run the same `python -m pip` commands.

The direct dependencies are Flask, Matplotlib, pandas, NetworkX, Qiskit, Qiskit Aer, and scikit-learn. Their supporting packages are installed by pip. The requirements file pins direct packages; it is not a complete lockfile for all transitive dependencies.

If a copied `venv` points to a Python installation on another computer, create a fresh environment for your machine instead of relying on that directory.

## Run the web interface

From the project root, with the environment active:

```bash
python -m flask --app frontend.app run
```

Open **http://127.0.0.1:5000**. Alternatively, `python -m frontend.app` starts the same application with Flask's development debugger enabled. Use module-based commands from the project root so Python can resolve the `backend` package.

Enter, for example:

```text
Problem sizes: 8,16,32,64,128
Noise levels:  0,0.05,0.1,0.2
```

Click **Run Full Experimental Analysis**. The request runs these steps in order:

1. For each requested size, time classical list search and another execution of the unchanged two-qubit circuit.
2. Run the one-qubit noise experiment for each requested depolarizing parameter.
3. Compare exact `K4` MaxCut with the existing random-partition placeholder.
4. Fit logistic regression on Iris and run the existing quantum ML placeholder.
5. Render three charts, the optimization and ML tables, and a conclusion describing the summed search/circuit times from this run.

The web interface does not perform factorization or export the terminal CSV. It retains submitted inputs and displays validation errors on the same page with HTTP status `400`.

### Input rules

- Problem sizes must be comma-separated positive integers. Empty entries, zero, negatives, and fractional sizes are rejected.
- Noise levels must be comma-separated finite numbers between `0` and `4/3`, inclusive, matching Qiskit Aer's one-qubit depolarizing-channel range. Enter `1.3333333333333333` for the upper endpoint; the form accepts numeric values, not expressions such as `4/3`.
- `NaN`, infinity, empty entries, and out-of-range noise values are rejected before any experiment starts.
- Surrounding whitespace is accepted. Entries run in the supplied order, including duplicates.

Each request runs synchronously. Search allocates a list proportional to the requested size, so begin with the small example values. The charts use shared filenames and are replaced by subsequent runs; this is a local demonstration, with no separate run storage or multi-user isolation. Chart URLs include a run identifier to prevent ordinary browser cache reuse, but do not preserve earlier chart versions.

The page loads Bootstrap styling from a CDN. An internet connection is needed for that styling; the experiments themselves execute locally.

## Run the terminal workflow

```bash
python main.py
```

The program asks for a search size and a number to factor. For example, enter `32` and then `15`.

It prints the classical search result, quantum measurement counts, their execution times, the factor pair `(3, 5)`, and the factorization time. It then prints and saves the search timing table and saves the comparison chart. A graphical environment also displays the chart.

Invalid integer input prompts again. Search size must be at least `1`; the number to factor must be at least `2`. For a prime such as `13`, the terminal explains that no non-trivial factor pair exists.

For a non-interactive graphics backend on macOS or Linux:

```bash
MPLBACKEND=Agg python main.py
```

The input prompts still appear, and the chart is saved without requiring a plot window.

Terminal output files:

- `results/performance_table.csv`: two rows, with `Algorithm` and `Execution Time` columns. Time is measured in seconds. The `Quantum Search` row retains its original label but represents the fixed circuit described above.
- `results/search_graph.png`: a bar chart of those two elapsed times.

These files are overwritten on each successful terminal run. Factorization is printed but is not included in the CSV. Existing committed images and CSV values are example artifacts, not reproducible benchmarks.

## Reading the results correctly

Elapsed durations use `time.perf_counter()`, a monotonic high-resolution timer. Each reported measurement covers the same operation boundaries as the original experiment. Circuit construction and simulator/noise-model setup remain outside the quantum timers; `.run(...).result()` remains inside them.

The classical search grows with the entered size, while the quantum-labelled search repeatedly runs the same circuit. Their outputs also have different meanings: a membership Boolean versus sampled bitstrings. Comparing these timings cannot demonstrate an equivalent-task quantum speedup or a scaling crossover.

Similarly, the QAOA and quantum ML timings include fixed sleep delays. Their random outputs are illustrative placeholders, so comparing them to exact MaxCut or fitted logistic regression is not a real quantum optimization or ML benchmark. The Iris split, placeholder outputs, and circuit sampling remain unseeded, as in the original implementation; values can change between runs.

The noise experiment measures runtime only. It does not measure fidelity, error rates, or accuracy, and runtime need not increase monotonically with the noise parameter. The search experiment does not use this noise model, so its timing differences cannot be attributed to the separate noise experiment.

There are no repeated-trial statistics, warm-up controls, confidence intervals, hardware benchmarks, or matched classical/quantum workloads. Small durations also depend on machine load and simulator overhead. The current project can describe the observed run, but it cannot prove that quantum methods generally provide or fail to provide practical benefit.

## Validation

Run the regression checks from the project root:

```bash
MPLBACKEND=Agg python -m unittest discover -s tests -v
python -m pip check
```

On Windows PowerShell, set `$env:MPLBACKEND = "Agg"` before running the unittest command.

The tests cover search results and validation, the preserved quantum gate sequence and shot count, factorization, exact MaxCut, placeholder output ranges and delays, ML execution, noise defaults and boundaries, invalid web submissions, template rendering, a complete web analysis with served PNGs, import behavior, and terminal execution with a missing results directory from another working directory. Tests use temporary output directories so they do not replace the project's saved results.

## Maintenance fixes in this review

- Connected Flask to `frontend/templates/index.html`; previously, the route returned a separate inline page and ignored the template.
- Added validation for missing, malformed, non-positive, non-finite, and out-of-range inputs to prevent incorrect runs and simulator errors.
- Made output paths independent of the launch directory and ensured missing output directories are created.
- Put the terminal workflow behind a `main()` entry point so importing it does not prompt or run experiments.
- Switched elapsed-time measurements to a high-resolution monotonic clock and retained small non-zero values in web timing tables.
- Reused the existing backend noise experiment in the web workflow, preserving the same circuit and shot count.
- Used separate figure objects for web charts and added cache refresh parameters to chart URLs.
- Corrected labels and conclusions to distinguish real computations from fixed circuits and simulated placeholders.
- Added the tested dependency list and regression checks without changing the existing model or algorithm choices.

## Troubleshooting

- **`No module named 'backend'`:** run the web application from the project root using `python -m flask --app frontend.app run`, rather than executing `frontend/app.py` directly.
- **Missing package:** activate the intended environment and run `python -m pip install -r requirements.txt` using that same interpreter.
- **Port 5000 is in use:** use `python -m flask --app frontend.app run --port 5001`, then open `http://127.0.0.1:5001`.
- **No graphical display:** use `MPLBACKEND=Agg` for the terminal workflow. The web route saves its figures without opening a GUI.
- **Matplotlib cache is not writable:** set `MPLCONFIGDIR` to a writable directory before starting the application or tests.
- **Different results on another run:** random splits, sampling, random placeholders, and runtime variation are expected in this implementation.
