//! U2 equivalence: the id fast path must produce exactly the labels the string
//! path produces, including across repeated calls on one thread's tagger.

use crfs::Attribute;
use fastaddress_core::features::tokens_to_attrs;
use fastaddress_core::model::{tag_attr_ids, tag_attrs};
use fastaddress_core::tokenize::tokenize;

/// String path (oracle-diffed) vs the PRODUCTION id path (attr_cache + tag_ids
/// via api::parse) — the comparison that extends the parity guarantee.
fn both_paths(address: &str) -> (Vec<String>, Vec<String>) {
    let tokens = tokenize(address);
    let attrs = tokens_to_attrs(&tokens);
    let string_labels = tag_attrs(&attrs).expect("string path must tag");
    let id_labels: Vec<String> = fastaddress_core::api::parse(address)
        .into_iter()
        .map(|(_token, label)| label)
        .collect();
    (string_labels, id_labels)
}

#[test]
fn id_path_matches_string_path() {
    for address in [
        "123 N Main St Apt 4B Springfield IL 62704",
        "PO BOX 5410 CHICAGO IL 60680",
        "59 ST JAMES PLACE NEW YORK NY 10038",
        "115 -119 FORBES AVE PITTSBURGH PA 15222",
        "Mile K Beach Road # 1, Kenai, AK 99611",
    ] {
        let (string_labels, id_labels) = both_paths(address);
        assert_eq!(string_labels, id_labels, "divergence on {address}");
    }
}

#[test]
fn scratch_reuse_is_stable_across_calls() {
    let a = "123 N Main St Springfield IL 62704";
    let b = "PO BOX 5410 CHICAGO IL 60680";
    let first_a = both_paths(a).1;
    let _b = both_paths(b).1;
    let second_a = both_paths(a).1;
    assert_eq!(first_a, second_a, "tagger scratch reuse leaked state");
}

#[test]
fn full_corpus_id_path_matches_string_path() {
    // R3: every row of every benchmark dataset, both paths, identical labels.
    let data_dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../benchmark/data");
    let mut rows_checked = 0usize;
    for entry in std::fs::read_dir(&data_dir).expect("benchmark/data must exist") {
        let path = entry.unwrap().path();
        if path.extension().and_then(|e| e.to_str()) != Some("csv") {
            continue;
        }
        let mut reader = csv::Reader::from_path(&path).unwrap();
        let idx = reader
            .headers()
            .unwrap()
            .iter()
            .position(|h| h == "raw_address")
            .unwrap();
        for record in reader.records() {
            let record = record.unwrap();
            let raw = record.get(idx).unwrap_or("");
            let (string_labels, id_labels) = both_paths(raw);
            assert_eq!(string_labels, id_labels, "divergence on {raw:?} in {path:?}");
            rows_checked += 1;
        }
    }
    assert!(rows_checked > 20_000, "corpus missing: only {rows_checked} rows");
}

#[test]
fn word_cache_negative_caching_and_cap() {
    // Unknown words resolve once (negative-cached) and the map stays bounded.
    let before = fastaddress_core::attr_cache::word_cache_len_for_tests();
    for i in 0..200 {
        let addr = format!("123 Zzqx{i}veryunlikelyword St Springfield IL 62704");
        let (s, d) = both_paths(&addr);
        assert_eq!(s, d, "divergence on synthetic unknown word");
    }
    let after = fastaddress_core::attr_cache::word_cache_len_for_tests();
    assert!(after > before, "unknown words were not cached at all");
    assert!(
        after <= fastaddress_core::model::num_attrs() as usize * 2,
        "word cache exceeded its cap"
    );
}

#[test]
fn empty_sequence_yields_empty_labels() {
    assert!(tag_attr_ids(&[]).is_empty());
    let empty: Vec<Vec<Attribute>> = Vec::new();
    assert!(tag_attrs(&empty).unwrap().is_empty());
}
