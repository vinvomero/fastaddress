"""Train a v2 CRF model (plan M-U4). One-time build tooling.

Uses the exact v1 feature pipeline (usaddress.tokens2features at the pinned
version) so training features match the Rust engine's serialized attributes
bit-for-bit. Emits model/usaddr_v2.crfsuite + a training manifest.

Usage: python training/train.py [--minfreq N] [--c1 X] [--c2 X] [--out PATH]
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

import pycrfsuite
import usaddress

ROOT = Path(__file__).parent.parent
CORPUS = Path(__file__).parent / "corpus" / "corpus.jsonl"
SYNTH = Path(__file__).parent / "corpus" / "synth.jsonl"
DISTILLED = Path(__file__).parent / "corpus" / "distilled.jsonl"
AUGMENTED = Path(__file__).parent / "corpus" / "augmented.jsonl"
TIGER = Path(__file__).parent / "corpus" / "tiger.jsonl"
ERRCLASS = Path(__file__).parent / "corpus" / "errclass.jsonl"
NATIONAL = Path(__file__).parent / "corpus" / "national.jsonl"
REALTEXT = Path(__file__).parent / "corpus" / "realtext.jsonl"
REALTEXT2 = Path(__file__).parent / "corpus" / "realtext2.jsonl"
REALTEXT2_NO2A = Path(__file__).parent / "corpus" / "realtext2_no2a.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minfreq", type=float, default=0)
    ap.add_argument("--c1", type=float, default=0.1)
    ap.add_argument("--c2", type=float, default=0.01)
    ap.add_argument("--max-iterations", type=int, default=200)
    # Default deliberately points at scratch, never at the shipping artifact:
    # a grid invocation that forgets --out must not replace model/usaddr_v2.
    ap.add_argument("--out", default=str(ROOT / "model" / "candidates" / "scratch.crfsuite"))
    ap.add_argument(
        "--oversample-labeled",
        type=int,
        default=1,
        help="repeat upstream labeled.xml rows N times (rare-pattern class balance)",
    )
    ap.add_argument(
        "--distant-cap",
        type=int,
        default=None,
        help="cap distant-supervised rows per county source (dilution control)",
    )
    ap.add_argument(
        "--synth",
        type=int,
        default=0,
        help="include training/corpus/synth.jsonl N times (pattern-targeted data)",
    )
    ap.add_argument(
        "--distill",
        type=int,
        default=0,
        help="include training/corpus/distilled.jsonl N times (v1-imitation data)",
    )
    ap.add_argument(
        "--augment",
        type=int,
        default=0,
        help="include training/corpus/augmented.jsonl N times (shape-preserving v1-win data)",
    )
    ap.add_argument(
        "--tiger",
        type=int,
        default=0,
        help="include training/corpus/tiger.jsonl N times (Census-authoritative street splits)",
    )
    ap.add_argument(
        "--errclass",
        type=int,
        default=0,
        help="include training/corpus/errclass.jsonl N times (adjudication-derived error classes)",
    )
    ap.add_argument(
        "--national",
        type=int,
        default=0,
        help="include training/corpus/national.jsonl N times (U3 coverage-floor corpus; supersedes --errclass)",
    )
    ap.add_argument(
        "--realtext",
        type=int,
        default=0,
        help="include training/corpus/realtext.jsonl N times (RT-U1 aligned real owner-mail text; dev holdout already carved out)",
    )
    ap.add_argument(
        "--realtext2",
        type=int,
        default=0,
        help="include training/corpus/realtext2.jsonl N times (G2B-U2 extended-ladder hard classes; hard dev holdout already carved out)",
    )
    ap.add_argument(
        "--drop-rung-2a",
        action="store_true",
        help="use the realtext2 variant without rung 2a (omitted-suffix rows): gold-2b "
             "attempt 1 attributed 19 of 47 losses to StreetNamePostType -> StreetName",
    )
    args = ap.parse_args()

    trainer = pycrfsuite.Trainer(verbose=False)
    n = 0
    by_origin = {}
    t0 = time.perf_counter()

    def feed(path, distant_cap=None):
        nonlocal n
        distant_seen = {}
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                origin = r.get("origin", "?")
                if distant_cap and origin.endswith("-ds"):
                    c = distant_seen.get(origin, 0)
                    if c >= distant_cap:
                        continue
                    distant_seen[origin] = c + 1
                feats = usaddress.tokens2features(r["tokens"])
                repeats = args.oversample_labeled if origin == "labeled.xml" else 1
                for _ in range(repeats):
                    trainer.append(feats, r["labels"])
                    n += 1
                by_origin[origin] = by_origin.get(origin, 0) + repeats

    feed(CORPUS, distant_cap=args.distant_cap)
    if args.synth and SYNTH.exists():
        for _ in range(args.synth):
            feed(SYNTH)
    if args.distill and DISTILLED.exists():
        for _ in range(args.distill):
            feed(DISTILLED)
    if args.augment and AUGMENTED.exists():
        for _ in range(args.augment):
            feed(AUGMENTED)
    if args.tiger and TIGER.exists():
        for _ in range(args.tiger):
            feed(TIGER)
    if args.errclass and ERRCLASS.exists():
        for _ in range(args.errclass):
            feed(ERRCLASS)
    if args.national and NATIONAL.exists():
        for _ in range(args.national):
            feed(NATIONAL)
    if args.realtext and REALTEXT.exists():
        for _ in range(args.realtext):
            feed(REALTEXT)
    if args.realtext2 and REALTEXT2.exists():
        src = REALTEXT2_NO2A if args.drop_rung_2a and REALTEXT2_NO2A.exists() else REALTEXT2
        for _ in range(args.realtext2):
            feed(src)
    feat_secs = time.perf_counter() - t0
    print(f"appended {n} sequences in {feat_secs:.0f}s")

    trainer.set_params(
        {
            "c1": args.c1,
            "c2": args.c2,
            "max_iterations": args.max_iterations,
            "feature.minfreq": args.minfreq,
            "feature.possible_transitions": True,
        }
    )
    t0 = time.perf_counter()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    trainer.train(args.out)
    train_secs = time.perf_counter() - t0

    model_bytes = Path(args.out).read_bytes()
    corpus_hash = hashlib.sha256(CORPUS.read_bytes()).hexdigest()[:16]
    manifest = {
        "sequences": n,
        "by_origin": by_origin,
        "oversample_labeled": args.oversample_labeled,
        "distant_cap": args.distant_cap,
        "synth_repeats": args.synth,
        "distill_repeats": args.distill,
        "augment_repeats": args.augment,
        "tiger_repeats": args.tiger,
        "errclass_repeats": args.errclass,
        "national_repeats": args.national,
        "realtext_repeats": args.realtext,
        "realtext2_repeats": args.realtext2,
        "drop_rung_2a": args.drop_rung_2a,
        "params": {
            "algorithm": "lbfgs",
            "c1": args.c1,
            "c2": args.c2,
            "max_iterations": args.max_iterations,
            "feature.minfreq": args.minfreq,
            "feature.possible_transitions": True,
        },
        "corpus_sha256_16": corpus_hash,
        "usaddress_feature_version": "0.5.16",
        "model_bytes": len(model_bytes),
        "model_sha256_16": hashlib.sha256(model_bytes).hexdigest()[:16],
        "train_seconds": round(train_secs, 1),
        "out": str(Path(args.out).name),
    }
    mpath = Path(__file__).parent / f"MANIFEST-{Path(args.out).stem}.json"
    mpath.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
