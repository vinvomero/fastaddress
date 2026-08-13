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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minfreq", type=float, default=0)
    ap.add_argument("--c1", type=float, default=0.1)
    ap.add_argument("--c2", type=float, default=0.01)
    ap.add_argument("--max-iterations", type=int, default=200)
    ap.add_argument("--out", default=str(ROOT / "model" / "usaddr_v2.crfsuite"))
    ap.add_argument(
        "--oversample-labeled",
        type=int,
        default=1,
        help="repeat upstream labeled.xml rows N times (rare-pattern class balance)",
    )
    args = ap.parse_args()

    trainer = pycrfsuite.Trainer(verbose=False)
    n = 0
    t0 = time.perf_counter()
    with open(CORPUS, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            feats = usaddress.tokens2features(r["tokens"])
            repeats = args.oversample_labeled if r.get("origin") == "labeled.xml" else 1
            for _ in range(repeats):
                trainer.append(feats, r["labels"])
                n += 1
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
    trainer.train(args.out)
    train_secs = time.perf_counter() - t0

    model_bytes = Path(args.out).read_bytes()
    corpus_hash = hashlib.sha256(CORPUS.read_bytes()).hexdigest()[:16]
    manifest = {
        "sequences": n,
        "oversample_labeled": args.oversample_labeled,
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
