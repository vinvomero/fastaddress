"""Model-selection surface: the opt-in `model=` keyword on every public function.

Passes against BOTH wheel builds:
  - feature build (--features model-v2): model="v2" works and diverges from v1
    on a known-divergent address;
  - default build: model="v2" raises ValueError("model 'v2' not available in
    this build") and everything else is identical.

Run after installing the built wheel: python crates/python/tests/test_model_select.py
"""

import sys

import fastaddress

# v2 reads "S" as part of the PlaceName (S Barrington is the actual village
# name); v1 reads it as StreetNamePostDirectional.
DIVERGENT = "9 WALNUT LN S BARRINGTON IL 60010"

ADDRESSES = [
    "123 N Main St Apt 4B Springfield IL 62704",
    "PO BOX 5410 CHICAGO IL 60680",
    "123 Main St, Chicago, IL 60614",
    DIVERGENT,
    "",
]

CRASH_CLASS = "59 ST JAMES PLACE NEW YORK NY 10038"


def check(cond, msg):
    if not cond:
        sys.exit(f"FAIL: {msg}")


def v2_available():
    try:
        fastaddress.parse("1 Main St", model="v2")
        return True
    except ValueError as e:
        check(
            str(e) == "model 'v2' not available in this build",
            f"feature-off ValueError message wrong: {e!r}",
        )
        return False


def main():
    # 1. Default call identical to explicit model="v1" on every function.
    for raw in ADDRESSES:
        check(
            fastaddress.parse(raw) == fastaddress.parse(raw, model="v1"),
            f"parse default != model='v1': {raw!r}",
        )
        check(
            fastaddress.tag_native(raw) == fastaddress.tag_native(raw, model="v1"),
            f"tag_native default != model='v1': {raw!r}",
        )
        check(
            fastaddress.parse_with_confidence(raw)
            == fastaddress.parse_with_confidence(raw, model="v1"),
            f"parse_with_confidence default != model='v1': {raw!r}",
        )
        check(
            fastaddress.tag_native_with_confidence(raw)
            == fastaddress.tag_native_with_confidence(raw, model="v1"),
            f"tag_native_with_confidence default != model='v1': {raw!r}",
        )
        try:
            default_tag = fastaddress.tag(raw)
        except fastaddress.RepeatedLabelError:
            default_tag = "raised"
        try:
            v1_tag = fastaddress.tag(raw, model="v1")
        except fastaddress.RepeatedLabelError:
            v1_tag = "raised"
        check(default_tag == v1_tag, f"tag default != model='v1': {raw!r}")

    # tag_mapping still works alongside the model keyword.
    mapping = {"AddressNumber": "HouseNumber"}
    check(
        fastaddress.tag("123 Main St", tag_mapping=mapping, model="v1")
        == fastaddress.tag("123 Main St", tag_mapping=mapping),
        "tag with tag_mapping + model='v1' != default",
    )

    # 2. Invalid model name raises ValueError listing the options, on all six.
    calls = [
        lambda m: fastaddress.parse("1 Main St", model=m),
        lambda m: fastaddress.tag("1 Main St", model=m),
        lambda m: fastaddress.tag_native("1 Main St", model=m),
        lambda m: fastaddress.parse_with_confidence("1 Main St", model=m),
        lambda m: fastaddress.tag_with_confidence("1 Main St", model=m),
        lambda m: fastaddress.tag_native_with_confidence("1 Main St", model=m),
    ]
    for i, call in enumerate(calls):
        try:
            call("nope")
            sys.exit(f"FAIL: function #{i} accepted model='nope'")
        except ValueError as e:
            msg = str(e)
            check("nope" in msg, f"ValueError should name the bad value: {msg!r}")
            check(
                "'v1'" in msg and "'v2'" in msg,
                f"ValueError should list valid options: {msg!r}",
            )

    # 3. RepeatedLabelError contract unchanged on the default path — and it is
    # RepeatedLabelError, not ValueError, that comes out.
    for fn in (fastaddress.tag, fastaddress.tag_with_confidence):
        try:
            fn(CRASH_CLASS)
            sys.exit(f"FAIL: expected RepeatedLabelError from {fn.__name__}")
        except fastaddress.RepeatedLabelError:
            pass

    # 4. v2 behavior, both builds.
    if v2_available():
        v1 = fastaddress.parse(DIVERGENT, model="v1")
        v2 = fastaddress.parse(DIVERGENT, model="v2")
        check(v1 != v2, f"expected divergence on {DIVERGENT!r}; both gave {v1}")
        v1_labels = dict(v1)
        v2_labels = dict(v2)
        check(
            v1_labels.get("S") == "StreetNamePostDirectional",
            f"v1 should read S as StreetNamePostDirectional: {v1}",
        )
        check(
            v2_labels.get("S") == "PlaceName",
            f"v2 should read S as PlaceName: {v2}",
        )

        # Every function accepts model="v2" and returns a sane shape.
        tagged, kind = fastaddress.tag("123 Main St Chicago IL", model="v2")
        check(kind == "Street Address", f"v2 tag address_type: {kind!r}")
        tagged, kind = fastaddress.tag_native(DIVERGENT, model="v2")
        check(len(tagged) > 0, "v2 tag_native returned nothing")
        triples = fastaddress.parse_with_confidence(DIVERGENT, model="v2")
        check(
            [(t, l) for t, l, _c in triples] == v2,
            "v2 parse_with_confidence disagrees with v2 parse",
        )
        check(all(0.0 <= c <= 1.0 for _t, _l, c in triples), "v2 confidence out of range")
        tagged, kind, conf, seq = fastaddress.tag_with_confidence("123 Main St Chicago IL", model="v2")
        check(set(conf) == set(tagged), "v2 tag_with_confidence keys misaligned")
        check(0.0 <= seq <= 1.0, "v2 sequence confidence out of range")
        tagged, kind, conf, seq = fastaddress.tag_native_with_confidence(DIVERGENT, model="v2")
        check(set(conf) == set(tagged), "v2 tag_native_with_confidence keys misaligned")
        print("OK: model selection surface verified (model-v2 feature build)")
    else:
        # Feature-off: every function raises the exact ValueError for v2.
        for i, call in enumerate(calls):
            try:
                call("v2")
                sys.exit(f"FAIL: function #{i} accepted model='v2' in a default build")
            except ValueError as e:
                check(
                    str(e) == "model 'v2' not available in this build",
                    f"feature-off message wrong on function #{i}: {e!r}",
                )
        print("OK: model selection surface verified (default build; v2 correctly unavailable)")


if __name__ == "__main__":
    main()
