# tools/

One-off pipeline utilities from the model-v2 evaluation campaign,
kept for auditability. Each script's docstring says what it did; none are part
of the public reproduction path.

- `adjudicate_disagreements.py` -- Disagreement triage for gold adjudication (findings round 1).
- `carve_realtext_dev.py` -- Carve the real-text dev holdout out of the training corpus (RT-U2).
- `census_classify_citydir.py` -- Resolve the '<letter> <CITY>' ambiguity with Census evidence, per record.
- `enrich_with_census.py` -- Attach US Census geocoder evidence to contested adjudication records.
- `gen_vocab.py` -- Generate crates/core/src/vocab.rs from the installed usaddress package.
- `ingest_confirmation.py` -- Fold the human-reviewed confirmation round into the verdict record.
- `ingest_round5.py` -- Fold round 5 (the v23-deciding review) into the verdict record.
- `ingest_round8.py` -- Ingest Round-8 human verdicts (gold-2 scoring attempt 2, candidate v43).
- `label_assist.py` -- Gold-set candidate sampler and prelabeler (eval/PROTOCOL.md step 1).
- `make_adjudication_doc.py` -- Turn eval/gold/disagreements.jsonl into a human-fillable adjudication doc.
- `make_confirmation_doc.py` -- Round-1 confirmation worklist: the records the gate legally cannot use yet.
- `make_gold2_review_doc.py` -- Round-7 review doc: gold-2 disagreements, blinded, tripwire-compliant.
- `make_round3_doc.py` -- Round-3 adjudication doc: only the records with no verdict yet.
- `score_adjudication.py` -- Score a filled adjudication pass (tools/make_adjudication_doc.py output).
- `score_round2.py` -- Score round-2 adjudication (fresh groups only) and report the combined picture.
- `sync_gold_status.py` -- Write the protocol's `status` field back from the verdict files.
