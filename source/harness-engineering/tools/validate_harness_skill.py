#!/usr/bin/env python3
"""Validate the canonical Harness Engineering tree.

The earlier generation of this repository was validated by a script that
assumed SPEC.md, PHASES.md and CHECKS.md at the root. That generation is now
archived under docs/archive/, so this validator targets the current layout:
SKILL.md plus core/, adapters/, references/, goal/ and deployment/.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_SKILL_FILES = (
    "SKILL.md",
    "core/flow.md",
    "core/layer-details.md",
    "core/checklists.md",
    "core/exit-and-reentry.md",
    "core/capability-model.md",
    "adapters/claude-code/host-map.md",
    "adapters/claude-code/assembly.md",
    "adapters/codex/host-map.md",
    "adapters/codex/assembly.md",
    "references/methodology.md",
    "references/agent-templates/chatbot-planner.md",
    "references/agent-templates/chatbot-coder.md",
    "references/agent-templates/chatbot-debugger.md",
    "references/agent-templates/chatbot-reviewer.md",
)

REQUIRED_REPOSITORY_FILES = (
    "README.md",
    "README.zh-CN.md",
)

REQUIRED_COMPANION_FILES = (
    "goal/SKILL.md",
    "goal/references/protocol.json",
    "goal/scripts/validate_goal_skill.py",
    "deployment/AGENTS.md",
)

REQUIRED_LAYERS = tuple(f"Layer {index}" for index in range(7))

SCAN_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml"}
SKIP_DIRECTORIES = {".git", "__pycache__", ".pytest_cache", "archive", "evals", "node_modules", "tools"}
LEGACY_MARKERS = ("superpowers/", "D:/graghRAG-agent")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return values
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return None


def validate_required(root: Path, installed: bool = False) -> list[str]:
    required = REQUIRED_SKILL_FILES
    if not installed:
        required = (*required, *REQUIRED_REPOSITORY_FILES, *REQUIRED_COMPANION_FILES)
    return [f"missing required file: {relative}" for relative in required if not (root / relative).is_file()]


def validate_entry(root: Path) -> list[str]:
    entry = root / "SKILL.md"
    if not entry.is_file():
        return []
    text = entry.read_text(encoding="utf-8")
    errors: list[str] = []
    frontmatter = parse_frontmatter(text)
    if frontmatter is None:
        return ["SKILL.md must start with YAML frontmatter delimited by ---"]
    if frontmatter.get("name") != "harness-engineering":
        errors.append("SKILL.md frontmatter name must be harness-engineering")
    if len(frontmatter.get("description", "")) < 40:
        errors.append("SKILL.md frontmatter description must be non-trivial")
    for layer in REQUIRED_LAYERS:
        if layer not in text:
            errors.append(f"SKILL.md does not mention {layer}")
    return errors


def _markdown_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts[:-1]):
            continue
        files.append(path)
    return files


def validate_links(root: Path) -> list[str]:
    errors: list[str] = []
    for path in _markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            relative = target.split("#", 1)[0].strip()
            if not relative or relative.startswith("/"):
                continue
            if not (path.parent / relative).exists():
                errors.append(f"{path.relative_to(root)}: broken link {target}")
    return errors


def validate_no_legacy_paths(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        parts = path.relative_to(root).parts
        if any(part in SKIP_DIRECTORIES for part in parts[:-1]):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in LEGACY_MARKERS:
            if marker in text:
                errors.append(f"{path.relative_to(root)}: legacy reference {marker}")
    return errors


def validate(root: Path, installed: bool = False) -> list[str]:
    return [
        *validate_required(root, installed),
        *validate_entry(root),
        *validate_links(root),
        *validate_no_legacy_paths(root),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Harness Engineering tree")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument(
        "--installed",
        action="store_true",
        help="validate an installed skill copy without READMEs, goal/ or deployment/",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    errors = validate(root, installed=args.installed)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: harness-engineering structure valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
