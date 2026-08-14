"""Write the protocol's `status` field back from the verdict files.

PROTOCOL.md specifies a per-record status (`prelabeled` / `llm_reviewed` /
`adjudicated`) and rules that "only adjudicated records enter gate arithmetic".
That field was never driven: every one of the 1,500 gold records still reads
`prelabeled`, because adjudication was in practice tracked in separate verdict
files keyed by raw address, carrying a `human_reviewed` boolean.

Two sources of truth for the same fact is how a claim quietly detaches from its
evidence. The verdict files are the real record, so this projects them onto the
field the protocol actually names:

    human_reviewed: true   -> adjudicated
    verdict present only   -> llm_reviewed
    no verdict             -> prelabeled  (unchanged)

Run after each adjudication round. `--check` exits non-zero if the file is out
of sync without writing, so it can gate a commit.

Usage: python tools/sync_gold_status.py [--check]
"""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
GOLD = ROOT / "eval" / "gold" / "candidates.jsonl"
VERDICTS = ROOT / "eval" / "gold" / "verdicts-merged.json"


def status_for(info):
    if info is None:
        return "prelabeled"
    return "adjudicated" if info.get("human_reviewed") else "llm_reviewed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing, exit 1 if stale")
    args = ap.parse_args()

    merged = json.loads(VERDICTS.read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in open(GOLD, encoding="utf-8-sig") if l.strip()]

    changed = []
    for r in rows:
        want = status_for(merged.get(r["raw"]))
        if r.get("status") != want:
            changed.append((r["raw"], r.get("status"), want))
            if not args.check:
                r["status"] = want

    counts = Counter(status_for(merged.get(r["raw"])) for r in rows)
    print("status distribution implied by the verdict files:")
    for k in ("adjudicated", "llm_reviewed", "prelabeled"):
        print(f"  {k:14} {counts.get(k, 0)}")
    print(f"\nrecords whose stored status disagrees: {len(changed)}")
    for raw, was, want in changed[:5]:
        print(f"   {was} -> {want}  {raw[:56]}")

    if args.check:
        if changed:
            print("\nSTALE — run without --check to sync")
            raise SystemExit(1)
        print("\nin sync")
        return

    with open(GOLD, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"\nwrote {GOLD}")


if __name__ == "__main__":
    main()
