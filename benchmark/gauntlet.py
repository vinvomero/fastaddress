"""U5: the dev-tier gauntlet — every check, one command, no partial blessings.

Runs, in order: clean+gold-1 (full_check), the human-only full-set margin, the
16-state scan, the 32-state holdout, and the spent 20-county split — and
refuses to bless a candidate unless every one is green. Partial evaluation is
how two false "no regressions" claims happened; this driver makes partial
impossible to do by accident.

Also owns binding-draw legality: --draw-binding N samples N never-used
counties, checks them against every county in eval/SPLITS.md, refuses
overlap, and prints the ledger entry that must be appended BEFORE the run.

Usage:
  python benchmark/gauntlet.py --candidate model/usaddr_v32.crfsuite
  python benchmark/gauntlet.py --draw-binding 20 --seed 20260816
"""

import argparse
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEDGER = ROOT / "eval" / "SPLITS.md"


def run(title, cmd, expect=None):
    print("=" * 78)
    print(title)
    print("=" * 78)
    r = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip()
    print(out)
    if r.returncode != 0:
        print(f"[exit {r.returncode}]")
        print((r.stderr or "").strip()[:800])
        return False
    if expect and not all(e in out for e in expect):
        print(f"MISSING EXPECTED MARKER(S): {[e for e in expect if e not in out]}")
        return False
    print()
    return True


def ledger_counties():
    """Every 5-digit county FIPS mentioned anywhere in the ledger."""
    text = LEDGER.read_text(encoding="utf-8")
    return set(re.findall(r"\b(\d{5})\b", text))


def gauntlet(candidate, judged_parse):
    ok = True
    ok &= run("1. CLEAN GATE + ALL ADJUDICATED RECORDS",
              ["benchmark/full_check.py", "--candidate", candidate])
    margin = ["benchmark/full_set_margin.py", "--candidate", candidate, "--human-only"]
    if judged_parse:
        margin += ["--judged-parse", judged_parse]
    ok &= run("2. GOLD-1 FULL-SET MARGIN (human-reviewed only)", margin,
              expect=["margin >= +3.0 pp : PASS"])
    ok &= run("3. 16-STATE SCAN (spent; dev tier)",
              ["benchmark/national_scan.py", "--candidate", candidate],
              expect=["net national improvement : PASS", "no state worse than 3:1  : PASS"])
    ok &= run("4. 32-STATE HOLDOUT (spent; dev tier)",
              ["benchmark/holdout_scan.py", "--candidate", candidate],
              expect=["net improvement      : PASS", "no state worse 3:1   : PASS"])
    ok &= run("5. 20-COUNTY FINAL SPLIT (spent; dev tier)",
              ["benchmark/final_validation.py", "--candidate", candidate],
              expect=["net improvement      : PASS", "no state worse 3:1   : PASS"])
    print("=" * 78)
    print(f"GAUNTLET VERDICT: {'ALL GREEN — candidate may proceed to a binding draw' if ok else 'RED — not eligible for a binding attempt'}")
    return ok


def draw_binding(n, seed):
    sys.path.insert(0, str(ROOT / "training"))
    import build_vocab_inventories as bvi
    fips = bvi.enumerate_counties()
    used = ledger_counties()
    pool = [f for f in fips if f not in used and not f.startswith(("72", "78"))]
    rng = random.Random(seed)
    draw = sorted(rng.sample(pool, n))
    overlap = set(draw) & used
    if overlap:
        raise SystemExit(f"REFUSED: drawn counties overlap the ledger: {sorted(overlap)}")
    print(f"binding draw (seed {seed}): {len(pool)} unused counties in pool")
    print("\n".join(draw))
    print("\nAppend to eval/SPLITS.md 'Binding attempts' BEFORE running, including the seed,")
    print("the >=20-divergents threshold, and at least one U1 hard-class geography — the draw")
    print("above is uniform; REPLACE one county with a stratified hard-class county and note it.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate")
    ap.add_argument("--judged-parse", default="model/usaddr_v19.crfsuite")
    ap.add_argument("--draw-binding", type=int)
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    if a.draw_binding:
        if a.seed is None:
            raise SystemExit("--draw-binding requires --seed (recorded in the ledger)")
        draw_binding(a.draw_binding, a.seed)
        return
    if not a.candidate:
        raise SystemExit("pass --candidate or --draw-binding")
    sys.exit(0 if gauntlet(a.candidate, a.judged_parse) else 1)


if __name__ == "__main__":
    main()
