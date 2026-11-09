"""Reproduce the claim-vs-evidence gap on a disposable workspace."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

AGENT_CLAIM = "All tests passed. The delivery is complete."


def _sha256(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def _find_guard() -> Path | None:
    candidates = [
        Path.cwd() / "source" / "goal-enforcement" / "scripts" / "goal_guard.py",
        Path(__file__).resolve().parents[1] / "source" / "goal-enforcement" / "scripts" / "goal_guard.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _delivery(artifact: Path, size: int, digest: str) -> dict:
    return {
        "schema_version": 1,
        "profile": "web-fullstack",
        "contract": {
            "revision": 1,
            "outcome": "The demo application reports its own success.",
            "actors": ["owner"],
            "flows": ["run the application", "read the reported status"],
            "non_goals": ["production deployment"],
            "constraints": ["keep the workspace disposable"],
            "unknowns": [],
            "delivery_target": "local-runnable",
            "approval": {
                "revision": 1,
                "confirmation_id": "demo-approval-1",
                "source": "demo://approval/1",
                "recorded_at": "2026-11-09T00:00:00+00:00",
            },
        },
        "slices": [
            {
                "slice_id": "demo",
                "outcome": "The application runs.",
                "criterion_ids": ["demo.runs"],
                "depends_on": [],
                "surfaces": {
                    name: {
                        "applicability": "reused",
                        "rationale": "Not changed by this demo.",
                        "evidence_ids": [],
                    }
                    for name in ("data", "api", "ui", "authorization", "deployment")
                },
            }
        ],
        "criteria": [
            {
                "criterion_id": "demo.runs",
                "slice_id": "demo",
                "outcome": "The application runs without error.",
                "revision": 1,
                "required": True,
                "status": "pass",
                "applicability_rationale": "Required for the demo claim.",
                "verification": {
                    "entry_id": "agent-self-report",
                    "cwd": ".",
                    "kind": "command",
                    "entry": ["python", "-B", "app.py"],
                    "environment_keys": [],
                },
                "evidence_ids": ["E1"],
                "judgment": {
                    "result": "pass",
                    "reason": "The agent reported success.",
                    "source": "demo://agent-report",
                    "at": "2026-11-09T00:00:02+00:00",
                    "evidence_ids": ["E1"],
                    "invalidation_count": 0,
                },
            }
        ],
        "evidence": [
            {
                "evidence_id": "E1",
                "criterion_id": "demo.runs",
                "revision": 1,
                "provenance": "observed_execution",
                "entry_id": "agent-self-report",
                "cwd": ".",
                "started_at": "2026-11-09T00:00:01+00:00",
                "finished_at": "2026-11-09T00:00:02+00:00",
                "observer": "demo-runner",
                "result": "pass",
                "exit_code": 0,
                "source_fingerprint": {
                    "algorithm": "sha256-manifest-v1",
                    "value": "0" * 64,
                    "scope": "regular-files-excluding-governance",
                    "captured_at": "2026-11-09T00:00:01+00:00",
                },
                "environment": {
                    "facts": {"python": sys.version.split()[0]},
                    "observed_at": "2026-11-09T00:00:01+00:00",
                    "source": "demo-runner",
                    "status": "observed",
                },
                "isolation": {
                    "mode": "isolated-snapshot",
                    "snapshot_id": "snapshot-E1",
                    "source_digest": digest,
                    "observer": "demo-runner",
                },
                "outputs": [{"path": artifact.name, "sha256": digest, "bytes": size}],
                "invalidation_count": 0,
            }
        ],
        "invalidations": [],
    }


def run_demo(keep: bool = False, workspace_path: str | None = None) -> int:
    guard = _find_guard()
    if guard is None:
        print(
            "The demo needs the repository checkout: goal_harness demo reads "
            "source/goal-enforcement/scripts/goal_guard.py.\n"
            "Clone the repository and run it from the repository root.",
            file=sys.stderr,
        )
        return 2

    workspace = Path(workspace_path) if workspace_path else Path(tempfile.mkdtemp(prefix="goal-harness-demo-"))
    workspace.mkdir(parents=True, exist_ok=True)
    artifact = workspace / "app.py"
    artifact.write_text("print('v1 tests passed')\n", encoding="utf-8")
    size, digest = _sha256(artifact)
    delivery_path = workspace / "delivery.json"
    delivery_path.write_text(json.dumps(_delivery(artifact, size, digest), indent=2), encoding="utf-8")

    python = sys.executable
    init = subprocess.run(
        [
            python,
            "-B",
            str(guard),
            "initialize-state",
            "--workspace",
            str(workspace),
            "--goal",
            "Reproduce a false success claim",
            "--mode",
            "maintenance",
            "--start-layer",
            "6",
            "--rationale",
            "disposable demo workspace",
            "--delivery-file",
            str(delivery_path),
        ],
        capture_output=True,
        text=True,
    )
    if init.returncode != 0:
        print(init.stdout.strip())
        print(init.stderr.strip(), file=sys.stderr)
        return init.returncode

    # The agent keeps editing after recording "evidence".
    artifact.write_text("print('v2 rewritten after the test run')\n", encoding="utf-8")

    # The agent then records acceptance in its own state file.
    state_path = workspace / ".codex" / "goal-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["scope_result"] = "accepted"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    audit = subprocess.run(
        [python, "-B", str(guard), "audit", "--workspace", str(workspace)],
        capture_output=True,
        text=True,
    )

    print("agent:  " + AGENT_CLAIM)
    print()
    print("goal-harness audit:")
    body = (audit.stdout + audit.stderr).strip()
    print(body if body else "(no output)")
    print()
    if audit.returncode == 0:
        print("verdict: pass")
    else:
        print("verdict: not-run - the recorded evidence does not describe this workspace")
    print(f"guard exit: {audit.returncode}")
    print(f"workspace: {workspace}" + ("" if keep else " (delete it when done)"))
    return 0
