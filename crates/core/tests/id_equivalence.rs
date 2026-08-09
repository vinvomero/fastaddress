//! U2 equivalence: the id fast path must produce exactly the labels the string
//! path produces, including across repeated calls on one thread's tagger.

use crfs::Attribute;
use usaddr_core::features::tokens_to_attrs;
use usaddr_core::model::{attr_id, label_name, tag_attr_ids, tag_attrs};
use usaddr_core::tokenize::tokenize;

fn both_paths(address: &str) -> (Vec<String>, Vec<String>) {
    let tokens = tokenize(address);
    let attrs = tokens_to_attrs(&tokens);
    let string_labels = tag_attrs(&attrs).expect("string path must tag");
    let id_seq: Vec<Vec<(u32, f64)>> = attrs
        .iter()
        .map(|item| {
            item.iter()
                .filter_map(|a| attr_id(&a.name).map(|id| (id, a.value)))
                .collect()
        })
        .collect();
    let id_labels: Vec<String> = tag_attr_ids(&id_seq)
        .into_iter()
        .map(|lid| label_name(lid).to_string())
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
fn empty_sequence_yields_empty_labels() {
    assert!(tag_attr_ids(&[]).is_empty());
    let empty: Vec<Vec<Attribute>> = Vec::new();
    assert!(tag_attrs(&empty).unwrap().is_empty());
}
