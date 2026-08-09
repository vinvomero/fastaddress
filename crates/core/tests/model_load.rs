use crfs::Attribute;
use serde::Deserialize;

#[derive(Deserialize)]
struct Fixture {
    address: String,
    attrs: Vec<Vec<(String, f64)>>,
    labels: Vec<String>,
}

#[test]
fn model_loads_from_vendored_bytes() {
    assert!(!usaddr_core::model::MODEL_BYTES.is_empty());
    // Force the lazy model parse by tagging an empty-attribute single token.
    let xseq = vec![vec![]];
    let labels = usaddr_core::model::tag_attrs(&xseq).expect("tagging must not error");
    assert_eq!(labels.len(), 1);
}

#[test]
fn fixture_attrs_reproduce_python_labels() {
    let raw = include_str!("fixtures/fixture.json");
    let fixture: Fixture = serde_json::from_str(raw).expect("fixture.json must parse");
    let xseq: Vec<Vec<Attribute>> = fixture
        .attrs
        .iter()
        .map(|token_attrs| {
            token_attrs
                .iter()
                .map(|(name, weight)| Attribute::new(name.clone(), *weight))
                .collect()
        })
        .collect();
    let labels = usaddr_core::model::tag_attrs(&xseq).expect("tagging must not error");
    assert_eq!(
        labels, fixture.labels,
        "Rust labels must equal Python usaddress labels for {}",
        fixture.address
    );
}
