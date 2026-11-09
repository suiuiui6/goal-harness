import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_demo_reports_stale_evidence_instead_of_success(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "goal_harness",
            "demo",
            "--keep",
            "--workspace",
            str(tmp_path / "demo"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output = result.stdout
    assert "All tests passed" in output
    assert "DELIVERY_ARTIFACT_STALE" in output
    assert "DELIVERY_SOURCE_STALE" in output
    assert "verdict: not-run" in output


def test_demo_is_listed_in_help():
    result = subprocess.run(
        [sys.executable, "-B", "-m", "goal_harness", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "demo" in result.stdout
