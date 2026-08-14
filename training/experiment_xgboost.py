"""Experiment: can gradient-boosted trees (XGBoost) replace the CRF?

The architectural difference that matters: a CRF labels the WHOLE SEQUENCE
jointly, so it can learn that a street type follows a street name and a ZIP
follows a state. XGBoost classifies each token INDEPENDENTLY — it can only see
sequence structure through whatever neighbor features we hand it.

This trains XGBoost on the exact same features the CRF sees (including the
previous:/next: context features) and scores it on the same clean eval set, so
the comparison isolates the architecture rather than the feature engineering.

Usage: python training/experiment_xgboost.py
"""

import json
import time
from pathlib import Path

import numpy as np
import usaddress
import xgboost as xgb
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).parent.parent
CORPUS = Path(__file__).parent / "corpus" / "corpus.jsonl"
SYNTH = Path(__file__).parent / "corpus" / "synth.jsonl"
CLEAN = ROOT / "eval" / "clean" / "clean.jsonl"
MAX_SEQ = 40000  # keep the experiment to a few minutes


def flatten(features):
    """pycrfsuite-style nested dicts -> flat {name: value} for DictVectorizer."""
    out = {}
    for k, v in features.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                out[f"{k}:{k2}"] = str(v2)
        else:
            out[k] = str(v)
    return out


def load(path, cap=None):
    X, y = [], []
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            feats = usaddress.tokens2features(r["tokens"])
            for tok_feats, label in zip(feats, r["labels"]):
                X.append(flatten(tok_feats))
                y.append(label)
            n += 1
            if cap and n >= cap:
                break
    return X, y


def main():
    print("loading corpus...")
    X, y = load(CORPUS, cap=MAX_SEQ)
    Xs, ys = load(SYNTH, cap=MAX_SEQ // 2)
    X += Xs
    y += ys
    print(f"{len(X)} labeled tokens")

    vec = DictVectorizer(sparse=True)
    Xv = vec.fit_transform(X)
    le = LabelEncoder()
    yv = le.fit_transform(y)
    print(f"feature dimensions: {Xv.shape[1]}, classes: {len(le.classes_)}")

    t0 = time.perf_counter()
    clf = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.3,
        tree_method="hist",
        n_jobs=8,
        objective="multi:softmax",
        num_class=len(le.classes_),
    )
    clf.fit(Xv, yv)
    train_s = time.perf_counter() - t0
    print(f"trained in {train_s:.0f}s")

    # Score on the clean eval set, full-address exact match (same metric as the gate)
    rows = [json.loads(l) for l in open(CLEAN, encoding="utf-8") if l.strip()]
    exact, total = 0, 0
    t0 = time.perf_counter()
    for r in rows:
        feats = usaddress.tokens2features(r["tokens"])
        Xr = vec.transform([flatten(f) for f in feats])
        pred = le.inverse_transform(clf.predict(Xr))
        total += 1
        if list(pred) == r["labels"]:
            exact += 1
    infer_s = time.perf_counter() - t0

    print()
    print(f"XGBoost clean-set exact match: {exact}/{total} = {exact/total*100:.2f}%")
    print(f"  (CRF v19 and the incumbent both score 159/159 = 100.00%)")
    print(f"inference: {total/infer_s:,.0f} addresses/sec single-process "
          f"(CRF v19 measured ~96,000/sec in Rust)")
    booster_bytes = len(clf.get_booster().save_raw())
    print(f"model size: {booster_bytes/1e6:.1f} MB raw booster "
          f"(+ {Xv.shape[1]:,}-entry vectorizer vocabulary) vs CRF 257 KB")


if __name__ == "__main__":
    main()
