#!/usr/bin/env python3
"""Validate SKILL.md frontmatter and print a repository manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml


NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class SkillValidationError(Exception):
    """Raised when one or more skills fail repository validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


def _skill_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for current, directories, files in os.walk(root, followlinks=False):
        directories[:] = sorted(
            directory
            for directory in directories
            if not directory.startswith(".")
            and directory != "tests"
            and not (Path(current) / directory).is_symlink()
        )
        if "SKILL.md" in files:
            paths.append(Path(current) / "SKILL.md")
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing YAML frontmatter")

    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing YAML frontmatter closing delimiter") from exc

    try:
        data = yaml.safe_load("\n".join(lines[1:closing]))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("YAML frontmatter must be a mapping")
    return data


def _validate_license_notices(root: Path) -> list[str]:
    """Keep verified redistribution notices from disappearing during updates."""
    manifest = root / ".license-manifest.json"
    if manifest.is_symlink():
        return [".license-manifest.json: notice manifest must be a regular file"]
    if not manifest.exists():
        return []
    try:
        data = json.loads(manifest.read_text())
        if data.get("version") != 1 or not isinstance(data.get("files"), list):
            raise ValueError("unsupported notice manifest")
        errors: list[str] = []
        seen: set[str] = set()
        for record in data["files"]:
            relative = record["path"]
            if not isinstance(relative, str) or not relative or relative in seen:
                raise ValueError("invalid or duplicate notice path")
            seen.add(relative)
            path = root / relative
            if (Path(relative).is_absolute() or ".." in Path(relative).parts
                    or not path.resolve().is_relative_to(root.resolve())):
                raise ValueError("notice path escapes Source")
            expected = record["sha256"]
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError("invalid notice SHA256")
            if path.is_symlink() or not path.is_file():
                errors.append(f"{relative}: verified license/notice is missing or not a regular file")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                errors.append(f"{relative}: verified license/notice changed; review its recorded origin")
        return errors
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [f".license-manifest.json: {exc}"]


def validate_repository(root: str | Path) -> list[dict[str, Any]]:
    """Return a sorted skill manifest, or raise for all validation errors."""
    root = Path(root)
    paths = _skill_paths(root)
    if not paths:
        raise SkillValidationError(["no SKILL.md files found"])

    errors: list[str] = _validate_license_notices(root)
    manifest: list[dict[str, Any]] = []
    names: dict[str, str] = {}

    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            data = _frontmatter(path)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            continue

        skill_errors: list[str] = []
        try:
            json.dumps(data)
        except (TypeError, ValueError):
            skill_errors.append("frontmatter must be JSON-serializable; quote YAML dates/timestamps")
        name = data.get("name")
        if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
            skill_errors.append("name must match [a-z0-9]+(-[a-z0-9]+)*")
        elif len(name) > 64:
            skill_errors.append("name must be at most 64 characters")
        elif name != path.parent.name:
            skill_errors.append(f"name '{name}' must match leaf directory '{path.parent.name}'")

        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            skill_errors.append("description must be a non-empty string")
        elif len(description) > 1024:
            skill_errors.append("description must be at most 1024 characters")

        license_text = data.get("license")
        if isinstance(license_text, str):
            reference = re.fullmatch(r"Complete terms in ([A-Za-z0-9_.-]+)", license_text.strip())
            if reference:
                notice = path.parent / reference.group(1)
                if (notice.is_symlink() or not notice.is_file()
                        or not notice.resolve().is_relative_to(path.parent.resolve())):
                    skill_errors.append(f"referenced license file is missing or unsafe: {reference.group(1)}")

        targets: list[str] = []
        metadata = data.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            skill_errors.append("metadata must be a mapping")
        elif isinstance(metadata, dict) and "targets" in metadata:
            candidate = metadata["targets"]
            if not isinstance(candidate, list) or not all(isinstance(item, str) for item in candidate):
                skill_errors.append("metadata.targets must be a list of strings")
            else:
                targets = candidate

        if isinstance(name, str):
            previous = names.get(name)
            if previous is not None:
                skill_errors.append(f"duplicate name '{name}' (already used by {previous})")
            else:
                names[name] = relative

        errors.extend(f"{relative}: {error}" for error in skill_errors)
        if not skill_errors:
            manifest.append(
                {
                    "name": name,
                    "path": relative,
                    "description": description,
                    "targets": targets,
                }
            )

    if errors:
        raise SkillValidationError(errors)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[2] / "skills", help="skill source root (default: repository skills/)")
    parser.add_argument("--json", action="store_true", help="print the manifest as JSON")
    args = parser.parse_args(argv)

    try:
        manifest = validate_repository(args.root)
    except SkillValidationError as exc:
        print("validation failed:", file=sys.stderr)
        for error in exc.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.json:
        json.dump(manifest, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        for skill in manifest:
            print(f"{skill['name']}\t{skill['path']}")
        print(f"validated {len(manifest)} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
