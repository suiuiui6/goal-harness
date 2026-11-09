# Goal Harness

[![CI](https://github.com/suiuiui6/goal-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/suiuiui6/goal-harness/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Your coding agent says the tests passed. This shows what it actually proved.**

Goal Harness audits a delivery claim against evidence that can be re-checked: the command that ran, the code snapshot it ran on, the artifacts it produced, and whether any of that is still true for the current workspace.

```text
agent:  All tests passed. The delivery is complete.

goal-harness audit:
FAIL: DELIVERY_ARTIFACT_STALE at delivery.evidence[0].outputs[0]: output bytes or digest changed
FAIL: DELIVERY_SOURCE_STALE at delivery.evidence[E1].source_fingerprint

verdict: not-run - the recorded evidence does not describe this workspace
```

That output is produced by the repository itself. Reproduce it:

```bash
git clone https://github.com/suiuiui6/goal-harness.git
cd goal-harness-web-fullstack
python -m goal_harness demo
```

The demo creates a disposable workspace, records a passing run, edits the code afterwards, then audits the claim. It leaves the workspace in place so you can inspect `.codex/goal-state.json`.

## What it checks

| Evidence level | What it proves |
| --- | --- |
| `contract` | Structure, ownership, links and rule invariants hold |
| `event_replay` | A recorded tool or read event actually occurred |
| `fullstack_fixture` | Page, API, SQLite and auth behaviour in an isolated fixture |

Missing observed input stays `not-run`. A passing exit code alone is not delivery evidence.

## Quick start

```bash
python -m goal_harness validate --root .
python -m goal_harness capability-check --root .
python -m goal_harness delivery-audit --root .
python -m goal_harness demo
```

`validate` delegates to the Goal and Harness validators, `capability-check` reports the guard's enforcement mode, and `delivery-audit` runs the guard against the workspace state.

Windows enforcement is `audit-only-windows`: audits are required evidence, and unavailable lifecycle hooks are never described as mechanical blocking.

## Install

There is no PyPI package yet, deliberately. The CLI resolves its validators and guard from `source/`, so a wheel would install a command that cannot run. Clone the repository and use it in place:

```bash
git clone https://github.com/suiuiui6/goal-harness.git
cd goal-harness-web-fullstack
python -m pip install -e .
goal-harness demo
```

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for Windows, macOS and Linux.

## Repository layout

| Path | Contents |
| --- | --- |
| `goal_harness/` | Public CLI, including `demo` |
| `source/goal/` | Goal intake skill, pinned from `goal-skill` |
| `source/harness-engineering/` | Harness skill, pinned from `harness-engineering-skill` |
| `source/goal-enforcement/` | Guard, delivery contract and evidence rules |
| `fixtures/web-notes/` | Local page, API and SQLite fixture |
| `tests/`, `source/*/tests/` | Behavioural and contract tests |

## Relationship to the methodology

[harness-engineering-skill](https://github.com/suiuiui6/harness-engineering-skill) is the methodology and the seven-layer execution model. This repository is the runnable enforcement layer: pinned upstream sources, the delivery contract, the guard, the fixtures and the release evidence.

It is not a competing copy of either upstream. Both are pinned in `tools/source-integrations.json` and CI rejects unresolved or changed pins.

## Development

```bash
python -m pytest --rootdir . -p no:cacheprovider tests -q
python -m pytest --rootdir . -p no:cacheprovider source/goal-enforcement/tests -q
python -m pytest --rootdir . -p no:cacheprovider source/goal/scripts -q
python -m pytest --rootdir . -p no:cacheprovider source/harness-engineering/scripts -q
python -m goal_harness validate --root .
python tools/check_source_integrations.py --root . --online
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

MIT.
