"""Locate release binaries portably.

Order: $CARGO_TARGET_DIR (cargo's own override, honored by our builds) ->
the repo's default target/. Whichever actually contains the binary wins, so
the scripts work both on machines that redirect the target dir and on a fresh
clone that just ran `cargo build --release`.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXE = ".exe" if os.name == "nt" else ""


def bin_path(name: str) -> str:
    candidates = []
    env = os.environ.get("CARGO_TARGET_DIR")
    if env:
        candidates.append(Path(env) / "release" / f"{name}{EXE}")
    candidates.append(ROOT / "target" / "release" / f"{name}{EXE}")
    # Legacy layout used by this project's original dev machine.
    candidates.append(Path("C:/cargo-target/us-address-parser/release") / f"{name}{EXE}")
    for c in candidates:
        if c.exists():
            return str(c)
    sys.stderr.write(
        f"warning: {name}{EXE} not found; run `cargo build --release` first "
        f"(searched: {', '.join(str(c) for c in candidates)})\n"
    )
    return str(candidates[0])
