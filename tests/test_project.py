import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from backend.factoring_module import classical_factor
from backend.ml_module import classical_ml, quantum_ml_simulated
from backend.noise_analysis import noise_comparison
from backend.optimization_module import classical_maxcut, quantum_qaoa_simulated
from backend.search_module import classical_search, quantum_search
from frontend.app import app


ROOT = Path(__file__).resolve().parents[1]


class AlgorithmTests(unittest.TestCase):
    def test_search_found_missing_and_invalid_sizes(self):
        self.assertTrue(classical_search(8, 7)[0])
        self.assertFalse(classical_search(8, 8)[0])
        for size in (0, -1, 1.5, True):
            with self.subTest(size=size), self.assertRaises(ValueError):
                classical_search(size, 0)

    def test_quantum_search_shots_and_existing_circuit(self):
        from qiskit_aer import AerSimulator

        simulator = AerSimulator()
        with patch.object(simulator, "run", wraps=simulator.run) as run:
            with patch("backend.search_module.AerSimulator", return_value=simulator):
                counts, elapsed = quantum_search()
        self.assertEqual(sum(counts.values()), 1024)
        self.assertTrue(set(counts).issubset({"00", "01", "10", "11"}))
        self.assertGreaterEqual(elapsed, 0)
        circuit = run.call_args.args[0]
        operations = [
            (instruction.operation.name, [
                circuit.find_bit(qubit).index for qubit in instruction.qubits
            ])
            for instruction in circuit.data
        ]
        self.assertEqual(operations, [
            ("h", [0]), ("h", [1]), ("cz", [0, 1]),
            ("h", [0]), ("h", [1]), ("barrier", [0, 1]),
            ("measure", [0]), ("measure", [1]),
        ])

    def test_factorization_composite_prime_and_invalid(self):
        self.assertEqual(classical_factor(15)[0], (3, 5))
        self.assertEqual(classical_factor(35)[0], (5, 7))
        self.assertIsNone(classical_factor(13)[0])
        self.assertIsNone(classical_factor(2)[0])
        for number in (0, 1, -15, 2.5, True):
            with self.subTest(number=number), self.assertRaises(ValueError):
                classical_factor(number)

    def test_maxcut_and_existing_placeholder(self):
        self.assertEqual(classical_maxcut()[0], 4)
        cut, elapsed = quantum_qaoa_simulated()
        self.assertIn(cut, (0, 3, 4))
        self.assertGreaterEqual(elapsed, 0.2)

    def test_ml_and_existing_placeholder(self):
        accuracy, elapsed = classical_ml()
        self.assertTrue(0 <= accuracy <= 1)
        self.assertGreaterEqual(elapsed, 0)
        accuracy, elapsed = quantum_ml_simulated()
        self.assertAlmostEqual(min(max(accuracy, 0.8), 0.9), accuracy)
        self.assertGreaterEqual(elapsed, 0.3)

    def test_noise_defaults_and_supported_boundaries(self):
        levels, times = noise_comparison()
        self.assertEqual(levels, [0, 0.05, 0.1, 0.2])
        self.assertEqual(len(times), len(levels))
        self.assertTrue(all(elapsed >= 0 for elapsed in times))
        self.assertEqual(noise_comparison([0, 1, 4 / 3])[0], [0, 1, 4 / 3])

    def test_noise_rejects_invalid_parameters(self):
        for levels in ([], [-0.1], [2], [float("nan")], [float("inf")]):
            with self.subTest(levels=levels), self.assertRaises(ValueError):
                noise_comparison(levels)


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_renders_template(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="sizes"', response.data)
        self.assertNotIn(b"{{", response.data)

    def test_invalid_input_never_starts_experiments(self):
        invalid = [
            {}, {"sizes": "8"}, {"noise": "0"},
            {"sizes": "", "noise": "0"},
            {"sizes": "8,", "noise": "0"},
            {"sizes": "1.5", "noise": "0"},
            {"sizes": "0,-1", "noise": "0"},
            {"sizes": "8", "noise": ""},
            {"sizes": "8", "noise": "nan"},
            {"sizes": "8", "noise": "inf"},
            {"sizes": "8", "noise": "-0.1"},
            {"sizes": "8", "noise": "2"},
            {"sizes": '<script>alert("x")</script>', "noise": "0"},
        ]
        with patch("frontend.app.classical_search") as search:
            for data in invalid:
                with self.subTest(data=data):
                    response = self.client.post("/", data=data)
                    self.assertEqual(response.status_code, 400)
                    self.assertIn(b'role="alert"', response.data)
                    self.assertNotIn(b"<script>", response.data)
            search.assert_not_called()

    def test_full_analysis_serves_charts_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            static_dir = Path(directory) / "static"
            previous_cwd = Path.cwd()
            previous_static_folder = app.static_folder
            try:
                os.chdir(directory)
                app.static_folder = str(static_dir)
                response = self.client.post(
                    "/", data={"sizes": " 8,16 ", "noise": "0,0.05,1.3333333333333333"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"cannot demonstrate quantum advantage", response.data)
                self.assertIn(b"Random Partition", response.data)
                self.assertIn(b"Random Accuracy", response.data)
                sources = re.findall(rb'<img src="([^"]+)"', response.data)
                self.assertEqual(len(sources), 3)
                for source in sources:
                    self.assertIn(b"?v=", source)
                    image = self.client.get(source.decode())
                    self.assertEqual(image.status_code, 200)
                    self.assertEqual(image.mimetype, "image/png")
                    self.assertTrue(image.data.startswith(b"\x89PNG\r\n\x1a\n"))
                    image.close()
                self.assertFalse((Path(directory) / "frontend").exists())
            finally:
                app.static_folder = previous_static_folder
                os.chdir(previous_cwd)


class CommandLineTests(unittest.TestCase):
    def test_import_does_not_prompt_or_write_results(self):
        with tempfile.TemporaryDirectory() as directory:
            environment = dict(os.environ, PYTHONPATH=str(ROOT))
            result = subprocess.run(
                [sys.executable, "-c", "import main"], cwd=directory,
                env=environment, input="", text=True, capture_output=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertFalse((Path(directory) / "results").exists())

    def test_cli_validates_inputs_and_creates_missing_output_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            shutil.copy2(ROOT / "main.py", project / "main.py")
            shutil.copytree(
                ROOT / "backend", project / "backend",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            result = subprocess.run(
                [sys.executable, str(project / "main.py")],
                cwd=directory, input="bad\n0\n8\n1\n13\n", text=True,
                env=dict(os.environ, MPLBACKEND="Agg"),
                capture_output=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Please enter an integer of at least 1.", result.stdout)
            self.assertIn("Please enter an integer of at least 2.", result.stdout)
            self.assertIn("Prime; no non-trivial factor pair.", result.stdout)
            self.assertTrue((project / "results" / "search_graph.png").is_file())
            table = (project / "results" / "performance_table.csv").read_text()
            self.assertEqual(len(table.splitlines()), 3)
            self.assertFalse((Path(directory) / "results").exists())


if __name__ == "__main__":
    unittest.main()
