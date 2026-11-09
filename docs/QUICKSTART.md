# Quick Start

## Requirements

- Python 3.11 or newer
- Git

The CLI is used from a repository checkout. There is no PyPI package yet because the validators and the guard are resolved from `source/`.

## Windows

```powershell
git clone https://github.com/suiuiui6/goal-harness-web-fullstack.git
cd goal-harness-web-fullstack
python -m pip install -e .
python -m goal_harness demo
python -m goal_harness validate --root .
```

Enforcement mode on Windows is `audit-only-windows`. Hooks that cannot be installed are reported as unavailable, not as blocking.

## macOS and Linux

```bash
git clone https://github.com/suiuiui6/goal-harness-web-fullstack.git
cd goal-harness-web-fullstack
python3 -m pip install -e .
python3 -m goal_harness demo
python3 -m goal_harness validate --root .
```

## What the demo does

1. Creates a disposable workspace.
2. Records a passing delivery claim with an artifact digest.
3. Edits the artifact after the run.
4. Audits the claim.

Expected result: `DELIVERY_ARTIFACT_STALE` and `DELIVERY_SOURCE_STALE`, with verdict `not-run`. The command exits `0` because the demo succeeded; the guard exit code is printed separately.

## Cleanup

The demo prints its workspace path. Delete that directory when you are done. With `--workspace <path>` you choose the location yourself.
