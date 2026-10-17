#!/usr/bin/env python3
"""Validate this repository and its targets, then preview (or --apply) global sync."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

ENTRYPOINT = Path('/usr/local/bin/skillshare')
PINNED_BINARY = Path('/opt/ai/skillshare/releases/0.25.13/skillshare')
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / 'skills'


def check_binary(entry: Path = ENTRYPOINT, expected: Path = PINNED_BINARY) -> Path:
    resolved = entry.resolve()
    if resolved != expected or not resolved.is_file():
        raise ValueError(f'unexpected skillshare binary: {resolved}; expected {expected}')
    version = subprocess.check_output([str(resolved), 'version'], text=True).strip()
    if version != 'skillshare v0.25.13':
        raise ValueError(f'unreviewed skillshare version: {version}')
    return resolved


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def check_targets(config: dict, root: Path, skills: list[dict]) -> None:
    root = root.resolve()
    source = Path(config['sources']['skills']).expanduser().resolve()
    if source != root:
        raise ValueError(f'configured source is not the dedicated skills directory: {source}')
    if config.get('follow_source_links', False):
        raise ValueError('source links must remain disabled until separately audited')
    targets = []
    for name, target in config.get('targets', {}).items():
        sc = target.get('skills', {})
        if sc.get('enabled') is False:
            continue
        if sc.get('mode', config.get('mode', 'merge')) != 'merge':
            raise ValueError(f'{name}: only reviewed merge mode is supported')
        if sc.get('target_naming', config.get('target_naming', 'flat')) != 'standard':
            raise ValueError(f'{name}: this repository requires standard naming')
        path = Path(sc['path']).expanduser().resolve()
        if _overlaps(path, root) or any(path != other and _overlaps(path, other) for other in targets):
            raise ValueError(f'{name}: source/target or target/target overlap: {path}')
        targets.append(path)
        # Check every source name conservatively, including currently filtered names.
        for skill in skills:
            entry = path / skill['name']
            expected = (root / skill['path']).parent.resolve()
            if entry.is_symlink() and entry.resolve() == expected:
                continue
            if entry.exists() or entry.is_symlink():
                raise ValueError(f'{name}: unmanaged source-name collision: {entry}')
        manifest_file = path / '.skillshare-manifest.json'
        managed = json.loads(manifest_file.read_text()).get('managed', {}) if manifest_file.exists() else {}
        expected_names = {skill['name'] for skill in skills}
        for obsolete in set(managed) - expected_names:
            entry = path / obsolete
            if entry.exists() or entry.is_symlink():
                if not entry.is_symlink() or root not in entry.resolve().parents:
                    raise ValueError(f'{name}: obsolete managed entry is not an old source link: {entry}')
        if path.exists():
            for entry in path.iterdir():
                if entry.is_symlink() and not entry.exists():
                    dest = entry.resolve()
                    if entry.name not in managed or root not in dest.parents:
                        raise ValueError(f'{name}: unmanaged broken link would be pruned: {entry}')
    if not targets:
        raise ValueError('no enabled targets configured')


def main() -> int:
    from validate_skills import SkillValidationError, validate_repository

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='apply after preflight; default is dry-run')
    args = parser.parse_args()
    root = SOURCE_ROOT
    config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    try:
        skills = validate_repository(root)
        config = yaml.safe_load((config_home / 'skillshare/config.yaml').read_text())
        check_targets(config, root, skills)
        binary = check_binary()
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, SkillValidationError, subprocess.CalledProcessError) as exc:
        print(f'preflight blocked: {exc}', file=sys.stderr)
        return 1
    command = [str(binary), 'sync', '-g']
    if not args.apply:
        command.append('--dry-run')
    print(f'Preflight OK: {len(skills)} source skills. Running {" ".join(command)}', flush=True)
    return subprocess.run(command, cwd=Path.home(), check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
