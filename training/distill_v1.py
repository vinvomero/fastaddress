"""Distill v1's behavior into training data (v3 recipe).

The adjudication showed v2 beat v1 only on the saint-name class and lost
everywhere else (landmarks, number-less streets, abbreviated place tokens,
post-directionals, USPS route boxes). Rather than chase each class with
hand-written synthetic data, teach the successor to imitate v1 on ordinary
input — v1's own parses become labels — and override only where v1 is
provably wrong.

Exclusions, in order of importance:
  1. Gold candidates and clean-eval rows (train/eval separation, non-negotiable)
  2. Saint-name-pattern rows: v1 is adjudicated WRONG there, so its labels must
     not be taught. Correct examples come from the synthetic generator instead.
  3. Rows where v1 crashes in tag() — its parse is unreliable by definition.

Usage: python training/distill_v1.py [--extra-cook-mail N]
Output: training/corpus/distilled.jsonl
"""

import argparse
import csv
import json
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

import usaddress

ROOT = Path(__file__).parent.parent
DATA = ROOT / "benchmark" / "data"
OUT = Path(__file__).parent / "corpus" / "distilled.jsonl"
EVAL_BIN = "C:/cargo-target/us-address-parser/release/eval_tag.exe"

# "113 ST MARKS PLACE" — leading number then ST then a word. v1 mislabels these.
SAINT_RE = re.compile(r"^\s*\d+\s+ST\.?\s+\w", re.IGNORECASE)


def norm(s):
    return "".join(c for c in s.upper() if c.isalnum())


def exclusions():
    ids = set()
    for p in (ROOT / "eval" / "gold" / "candidates.jsonl", ROOT / "eval" / "clean" / "clean.jsonl"):
        with open(p, encoding="utf-8") as f:
            for line in f:
                ids.add(norm(json.loads(line)["raw"]))
    return ids


def local_addresses():
    out = []
    for p in sorted(DATA.glob("*.csv")):
        with open(p, newline="", encoding="utf-8") as f:
            out += [r["raw_address"] for r in csv.DictReader(f)]
    return out


def fresh_cook_mail(n):
    """Extra messy free-text (owner mailing addresses) from a different slice."""
    params = urllib.parse.quote(
        "$select=mail_address_full,mail_address_city_name,mail_address_state,mail_address_zipcode_1"
        "&$where=year='2023' AND mail_address_full IS NOT NULL AND mail_address_zipcode_1 IS NOT NULL"
        f"&$limit={n}&$order=pin DESC", safe="$=&,()' ").replace(" ", "%20")
    url = f"https://datacatalog.cookcountyil.gov/resource/3723-97qp.json?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "distill/0.1"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        rows = json.load(resp)
    out = []
    for r in rows:
        line = " ".join(
            x for x in (
                (r.get("mail_address_full") or "").strip(),
                (r.get("mail_address_city_name") or "").strip(),
                (r.get("mail_address_state") or "").strip(),
                (r.get("mail_address_zipcode_1") or "").strip(),
            ) if x
        )
        if line:
            out.append(line)
    return out


def v1_parse_batch(addresses):
    with tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8", newline=""
    ) as tf:
        w = csv.writer(tf)
        w.writerow(["raw_address"])
        for a in addresses:
            w.writerow([a])
        tmp = tf.name
    proc = subprocess.run([EVAL_BIN, tmp], capture_output=True, text=True, encoding="utf-8", check=True)
    return [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]


def crashes(raw):
    try:
        usaddress.tag(raw)
        return False
    except usaddress.RepeatedLabelError:
        return True
    except Exception:
        return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra-cook-mail", type=int, default=25000)
    args = ap.parse_args()

    excl = exclusions()
    addresses = local_addresses()
    if args.extra_cook_mail:
        try:
            addresses += fresh_cook_mail(args.extra_cook_mail)
        except Exception as e:  # network optional; local data is enough to proceed
            print(f"extra fetch skipped: {e}")

    seen, kept = set(), []
    dropped = {"dup": 0, "eval_overlap": 0, "saint": 0, "crash": 0, "empty": 0}
    for a in addresses:
        k = norm(a)
        if not k:
            dropped["empty"] += 1
            continue
        if k in seen:
            dropped["dup"] += 1
            continue
        seen.add(k)
        if k in excl:
            dropped["eval_overlap"] += 1
            continue
        if SAINT_RE.match(a):
            dropped["saint"] += 1
            continue
        kept.append(a)

    parsed = v1_parse_batch(kept)
    rows = []
    for raw, p in zip(kept, parsed):
        if not p["tokens"]:
            dropped["empty"] += 1
            continue
        if crashes(raw):
            dropped["crash"] += 1
            continue
        rows.append({"tokens": p["tokens"], "labels": p["labels"], "origin": "distill-v1"})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} distilled sequences -> {OUT}")
    print("dropped:", json.dumps(dropped))


if __name__ == "__main__":
    main()
