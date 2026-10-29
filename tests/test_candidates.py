import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("candidate_report", ROOT / "scripts/candidate_report.py")
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / "local").mkdir(exist_ok=True)

    def setUp(self):
        self.data = json.loads((ROOT / "examples/candidates.synthetic.json").read_text(encoding="utf-8"))

    def test_total_metric_and_balanced_are_distinct(self):
        report = REPORT.analyze(self.data)
        self.assertEqual(report["best_J"], "best-total")
        self.assertEqual(report["best_by_metric"]["S21"], "best-s21")
        self.assertEqual(report["balanced"], "balanced")
        self.assertAlmostEqual(report["ranked"][0]["J"], 28/24)
        self.assertEqual(report["metric_improvement_percent"]["best-total"]["S21"], -50)

    def test_dominance_and_exclusions(self):
        report = REPORT.analyze(self.data)
        self.assertEqual(report["included_count"], 4)
        self.assertEqual(set(report["pareto"]), {"best-total", "best-s21", "balanced"})
        self.assertEqual([x["reason"] for x in report["excluded"]], ["not_successful", "duplicate"])

    def test_identity_mismatch_is_not_reused(self):
        self.data["candidates"][1]["sim_id"] = "another-mesh"
        self.data["candidates"].pop()  # remove duplicate so the same point is not still included
        report = REPORT.analyze(self.data)
        self.assertNotEqual(report["best_J"], "best-total")
        self.assertIn("identity_mismatch", [x["reason"] for x in report["excluded"]])

    def test_conflicting_duplicate_fails(self):
        self.data["candidates"][-1]["rmse"]["GD"] = 0.5
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            REPORT.analyze(self.data)

    def test_quality_filter_is_explicit(self):
        self.data.pop("baseline_id")
        report = REPORT.analyze(self.data, "precision_validated")
        self.assertEqual(report["included_count"], 1)
        self.assertEqual(report["best_J"], "balanced")

    def test_units_and_scales_fail_closed(self):
        bad = copy.deepcopy(self.data)
        bad["units"]["GD"] = "s"
        with self.assertRaises(ValueError):
            REPORT.analyze(bad)
        self.data["scales"]["GD"] = 0
        with self.assertRaises(ValueError):
            REPORT.analyze(self.data)

    def test_nonfinite_negative_boolean_and_missing_metrics_excluded(self):
        for invalid in (float("nan"), float("inf"), -1, True, None):
            with self.subTest(invalid=invalid):
                bad = copy.deepcopy(self.data)
                bad["candidates"][2]["rmse"]["GD"] = invalid
                report = REPORT.analyze(bad)
                self.assertIn("invalid_metrics", [x["reason"] for x in report["excluded"]])

    def test_zero_baseline_avoids_division(self):
        self.data["candidates"][0]["rmse"]["S21"] = 0
        report = REPORT.analyze(self.data)
        self.assertIsNone(report["metric_improvement_percent"]["balanced"]["S21"])

    def test_ineligible_baseline_and_empty_candidates_rejected(self):
        with self.assertRaisesRegex(ValueError, "baseline"):
            REPORT.analyze(self.data, "converged")
        self.data["candidates"] = []
        with self.assertRaisesRegex(ValueError, "No eligible"):
            REPORT.analyze(self.data)

    def test_cli_reads_without_changing_input_or_creating_outputs(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "local") as folder:
            path = Path(folder) / "input.json"
            path.write_text(json.dumps(self.data), encoding="utf-8")
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/candidate_report.py"), str(path)],
                                  cwd=folder, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["best_J"], "best-total")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            self.assertEqual([p.name for p in Path(folder).iterdir()], ["input.json"])

    def test_bad_json_cli_has_nonzero_exit(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "local") as folder:
            path = Path(folder) / "bad.json"
            path.write_text('{"incomplete":', encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/candidate_report.py"), str(path)],
                                  cwd=folder, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
