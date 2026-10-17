#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

BEGIN = "# --- talk-normal BEGIN ---"
END = "# --- talk-normal END ---"
SKILL_DIR = Path(__file__).resolve().parent.parent
PROMPT = SKILL_DIR / "prompt.md"
SOUL = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / "SOUL.md"


def split_block(text: str) -> tuple[str, str, str] | None:
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        return None
    before, rest = text.split(BEGIN, 1)
    middle, after = rest.split(END, 1)
    return before, middle, after


def desired_block() -> str:
    body = PROMPT.read_text().strip("\n")
    return f"{BEGIN}\n{body}\n{END}"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-talk-normal")
    tmp.write_text(text)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--remove", action="store_true")
    args = parser.parse_args()
    text = SOUL.read_text() if SOUL.exists() else "# Hermes Agent Persona\n"
    parts = split_block(text)

    if args.check:
        ok = parts is not None and f"{BEGIN}\n{parts[1].strip(chr(10))}\n{END}" == desired_block()
        print(f"talk-normal synchronized={str(ok).lower()} blocks={text.count(BEGIN)} soul={SOUL}")
        return 0 if ok else 1

    if args.remove:
        if parts is None:
            if text.count(BEGIN) == 0 and text.count(END) == 0:
                print(f"talk-normal already absent: {SOUL}")
                return 0
            raise SystemExit("refusing to edit malformed talk-normal markers")
        before, _, after = parts
        atomic_write(SOUL, (before.rstrip() + "\n" + after.lstrip()).rstrip() + "\n")
        print(f"talk-normal removed: {SOUL}")
        return 0

    block = desired_block()
    if parts is None:
        if text.count(BEGIN) or text.count(END):
            raise SystemExit("refusing to edit malformed talk-normal markers")
        updated = text.rstrip() + "\n\n" + block + "\n"
    else:
        before, _, after = parts
        updated = before.rstrip() + "\n\n" + block + "\n" + after.lstrip()
    atomic_write(SOUL, updated)
    print(f"talk-normal synchronized: {SOUL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
