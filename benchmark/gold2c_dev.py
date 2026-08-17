"""Gold-2c dev tier: score a candidate against human-approved label sequences.

Absolute labels, so any candidate scores without new human review. DEV ONLY --
pre-registered as never citable in a claim (PROTOCOL2, 2026-08-17). Reports
overall exact-match plus a per-class breakdown, because an average hides the
class-level damage that decided gold-2b.

Usage: python benchmark/gold2c_dev.py --candidate model/candidates/v50.crfsuite
"""
import argparse, collections, csv, json, random, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))
from binpath import bin_path

def tag(raws, model=None):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as tf:
        w = csv.writer(tf); w.writerow(["raw_address"])
        for r in raws: w.writerow([r])
        tmp = tf.name
    cmd = [bin_path("eval_tag"), tmp] + (["--model", model] if model else [])
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]

def klass(tokens, labels):
    ls = set(labels)
    if "Recipient" in ls: return "recipient"
    if ls & {"USPSBoxType", "USPSBoxGroupType"}: return "box"
    if "NotAddress" in ls: return "junk"
    if "StreetNamePostType" in ls: return "suffix-present"
    if "StreetName" in ls: return "suffix-omitted"
    return "other"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    a = ap.parse_args()
    gold = json.loads((ROOT / "eval" / "gold2c" / "approved_labels.json").read_text(encoding="utf-8"))
    raws = sorted(gold)
    v1 = tag(raws); cand = tag(raws, a.candidate)
    by = collections.defaultdict(lambda: [0, 0, 0])
    contrib = []
    b_ok = c_ok = 0
    for raw, p, c in zip(raws, v1, cand):
        want = gold[raw]["labels"]
        k = klass(gold[raw]["tokens"], want)
        pk = p["labels"] == want; ck = c["labels"] == want
        b_ok += pk; c_ok += ck
        by[k][0] += pk; by[k][1] += ck; by[k][2] += 1
        if pk != ck: contrib.append(1 if ck else -1)
    n = len(raws); net = sum(contrib)
    rng = random.Random(20260822)
    pop = contrib + [0]*(n-len(contrib))
    boots = sorted(sum(rng.choices(pop, k=n))/n*100 for _ in range(10000))
    print(f"gold-2c DEV: {n} human-approved records")
    print(f"exact match   v1 {b_ok}/{n} ({b_ok/n*100:.1f}%)   candidate {c_ok}/{n} ({c_ok/n*100:.1f}%)")
    print(f"head-to-head  {contrib.count(1)} candidate / {contrib.count(-1)} v1   net {net:+d}"
          f"   95% CI [{boots[250]:+.2f}, {boots[9750]:+.2f}] pp")
    print("\nby class (v1 -> candidate, of n):")
    for k in sorted(by):
        b, c, t = by[k]
        print(f"   {k:16} {b:3} -> {c:3}  of {t:3}   {'+' if c>b else '-' if c<b else '='}{abs(c-b)}")
    print("\nDEV ONLY -- never a claim (PROTOCOL2 2026-08-17)")

if __name__ == "__main__":
    main()
