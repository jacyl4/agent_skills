#!/usr/bin/env python3
"""Copy reviewed local skill payloads without overwriting the authoritative source."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import shutil
import yaml

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def fingerprint(root: Path) -> str:
    """Hash complete regular-file payloads; refuse links and special files."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"not a regular skill directory: {root}")
    digest = hashlib.sha256()
    for current, directories, files in os.walk(root, followlinks=False):
        directories.sort()
        for name in sorted(directories + files):
            path = Path(current) / name
            if path.is_symlink():
                raise ValueError(f"symlink payload needs separate review: {path}")
            if not path.is_dir() and not path.is_file():
                raise ValueError(f"special file needs separate review: {path}")
        for name in sorted(files):
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            digest.update(relative.encode() + b"\0")
            digest.update(str(path.stat().st_mode & 0o777).encode() + b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def copy_reviewed(source: Path, destination: Path, expected: str,
                  targets: tuple[str, ...] = ()) -> dict:
    """Stage a new skill after a hash check; never modify the original."""
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"destination already exists: {destination}")
    before = fingerprint(source)
    if before != expected:
        raise ValueError(f"source changed since review: {source}")
    skill = source / "SKILL.md"
    text = skill.read_text()
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"invalid frontmatter: {skill}")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict) or not isinstance(data.get("name"), str) or not NAME.fullmatch(data["name"]):
        raise ValueError(f"invalid skill name: {skill}")
    if destination.name != data["name"]:
        raise ValueError(f"destination must use frontmatter name: {skill}")
    if not isinstance(data.get("description"), str) or not data["description"].strip():
        raise ValueError(f"missing description: {skill}")
    if targets:
        metadata = data.setdefault("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError(f"invalid metadata: {skill}")
        existing = metadata.get("targets")
        if existing is not None and existing != list(targets):
            raise ValueError(f"target scope conflict: {skill}")
        metadata["targets"] = list(targets)
    shutil.copytree(source, destination)
    try:
        if fingerprint(destination) != before or fingerprint(source) != before:
            raise ValueError(f"payload changed during copy: {source}")
        if targets:
            (destination / "SKILL.md").write_text(
                "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip()
                + "\n---" + parts[2])
    except Exception:
        # Only the newly-created, exact destination is removed.
        shutil.rmtree(destination)
        raise
    return {"source": str(source), "destination": str(destination),
            "original_sha256": before, "managed_sha256": fingerprint(destination),
            "targets": list(targets)}
