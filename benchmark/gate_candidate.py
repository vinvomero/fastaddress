"""Run every gate a candidate model must face, in one command.

Collects the checks that were previously run separately and easy to run
incompletely -- which is how this project twice published a "no regressions"
claim that was blind to the records it never looked at.

  1. Clean gate            -- upstream held-out set, must not regress
  2. All adjudicated       -- every judged record, from every round
  3. Full-set gold margin  -- the pre-registered +3.0pp bar, all verdicts
  4. Same margin, human-reviewed verdicts only -- what the protocol actually counts

Usage:
  python benchmark/gate_candidate.py --candidate model/usaddr_v20.crfsuite \\
      --judged-parse model/usaddr_v19.crfsuite
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(title, cmd):
    print("=" * 78)
    print(title)
    print("=" * 78)
    r = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip())
    if r.returncode != 0:
        print(f"[exit {r.returncode}]")
        if r.stderr:
            print(r.stderr.strip()[:1500])
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--judged-parse", default=None,
                    help="model whose parses the reviewers actually saw; without it, a third "
                         "reading cannot be distinguished from an approved one")
    args = ap.parse_args()

    run("1+2. CLEAN GATE AND EVERY ADJUDICATED RECORD",
        ["benchmark/full_check.py", "--candidate", args.candidate])

    margin = ["benchmark/full_set_margin.py", "--candidate", args.candidate]
    if args.judged_parse:
        margin += ["--judged-parse", args.judged_parse]

    run("3. FULL-SET GOLD MARGIN (all verdicts — diagnostic only)", margin)
    run("4. FULL-SET GOLD MARGIN (human-reviewed only — this is the gate)", margin + ["--human-only"])

    print("Reminder: PROTOCOL.md counts only human-reviewed verdicts. Section 4 is the gate "
          "result; section 3 is diagnostic and must not be quoted as a gate pass.")


if __name__ == "__main__":
    main()
