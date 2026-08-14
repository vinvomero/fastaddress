//! Confidence (marginal probability) path.
//!
//! Three things are checked here: the marginals are a valid probability
//! distribution, the confidence path leaves the parity-protected `parse()` /
//! `tag()` output untouched, and component aggregation behaves as documented.

use usaddr_core::api;
use usaddr_core::attr_cache::facts_to_id_seq;
use usaddr_core::features::token_facts;
use usaddr_core::model::{tag_attr_ids_with_marginals_for, ModelId};
use usaddr_core::tokenize::tokenize;

/// A few hundred real rows from the benchmark corpora.
fn corpus(limit: usize) -> Vec<String> {
    let data_dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../benchmark/data");
    let mut out = Vec::new();
    let mut files: Vec<_> = std::fs::read_dir(&data_dir)
        .expect("benchmark/data must exist")
        .map(|e| e.unwrap().path())
        .filter(|p| p.extension().and_then(|e| e.to_str()) == Some("csv"))
        .collect();
    files.sort();
    'outer: for path in files {
        let mut reader = csv::Reader::from_path(&path).unwrap();
        let idx = reader
            .headers()
            .unwrap()
            .iter()
            .position(|h| h == "raw_address")
            .unwrap();
        for record in reader.records() {
            let record = record.unwrap();
            out.push(record.get(idx).unwrap_or("").to_string());
            if out.len() >= limit {
                break 'outer;
            }
        }
    }
    out
}

#[test]
fn per_position_marginals_sum_to_one() {
    let rows = corpus(2000);
    assert!(rows.len() >= 2000, "corpus too small: {}", rows.len());
    let mut worst = 0.0f64;
    let mut positions = 0usize;
    for raw in &rows {
        let tokens = tokenize(raw);
        if tokens.is_empty() {
            continue;
        }
        let facts: Vec<_> = tokens.iter().map(|t| token_facts(t)).collect();
        let seq = facts_to_id_seq(&facts);
        let out = tag_attr_ids_with_marginals_for(ModelId::V1, &seq);
        for t in 0..tokens.len() {
            let row = out.marginals_at(t);
            let sum: f64 = row.iter().sum();
            worst = worst.max((sum - 1.0).abs());
            positions += 1;
            for &p in row {
                assert!(
                    (-1e-12..=1.0 + 1e-12).contains(&p),
                    "marginal out of [0,1]: {p} in {raw:?}"
                );
            }
        }
    }
    println!("positions checked: {positions}, worst |sum - 1| = {worst:e}");
    assert!(
        worst < 1e-6,
        "per-position marginals do not sum to 1: worst error {worst:e}"
    );
}

#[test]
fn marginal_argmax_agrees_with_viterbi_most_of_the_time() {
    // Marginal-max and joint-max are different objectives, so this is a
    // measurement, not an invariant. The assert is only a smoke floor; the
    // reported rate is the number that matters.
    let rows = corpus(2000);
    let mut agree = 0usize;
    let mut total = 0usize;
    for raw in &rows {
        let tokens = tokenize(raw);
        if tokens.is_empty() {
            continue;
        }
        let facts: Vec<_> = tokens.iter().map(|t| token_facts(t)).collect();
        let seq = facts_to_id_seq(&facts);
        let out = tag_attr_ids_with_marginals_for(ModelId::V1, &seq);
        for (t, &lid) in out.labels.iter().enumerate() {
            let row = out.marginals_at(t);
            let argmax = row
                .iter()
                .enumerate()
                .max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
                .map(|(i, _)| i as u32)
                .unwrap();
            agree += (argmax == lid) as usize;
            total += 1;
        }
    }
    let rate = agree as f64 / total as f64;
    println!("viterbi/marginal-argmax agreement: {agree}/{total} = {:.6}", rate);
    assert!(rate > 0.90, "agreement collapsed to {rate}");
}

#[test]
fn confidence_path_does_not_change_parse_or_tag_output() {
    for raw in corpus(1500) {
        let plain = api::parse(&raw);
        let conf = api::parse_with_confidence(&raw);
        let conf_pairs: Vec<(String, String)> = conf
            .tokens
            .iter()
            .map(|t| (t.token.clone(), t.label.clone()))
            .collect();
        assert_eq!(plain, conf_pairs, "parse divergence on {raw:?}");

        match (api::tag(&raw), api::tag_with_confidence(&raw, None)) {
            (Ok((tagged, kind)), Ok(c)) => {
                assert_eq!(tagged, c.components, "tag divergence on {raw:?}");
                assert_eq!(kind, c.address_type, "address_type divergence on {raw:?}");
                assert_eq!(c.confidences.len(), c.components.len());
            }
            (Err(a), Err(b)) => {
                assert_eq!(a.repeated_label, b.repeated_label, "error divergence on {raw:?}");
            }
            (a, b) => panic!("error/ok mismatch on {raw:?}: {:?} vs {:?}", a.is_ok(), b.is_ok()),
        }

        let (nt, nk) = api::tag_native(&raw);
        let nc = api::tag_native_with_confidence(&raw);
        assert_eq!(nt, nc.components, "tag_native divergence on {raw:?}");
        assert_eq!(nk, nc.address_type);
        assert_eq!(nc.confidences.len(), nc.components.len());
    }
}

#[test]
fn component_confidence_is_the_min_of_its_tokens() {
    for raw in corpus(1500) {
        let per_token = api::parse_with_confidence(&raw);
        let tagged = api::tag_native_with_confidence(&raw);
        // Every component confidence must equal some token's marginal, and be
        // <= every token marginal it could plausibly have come from within
        // that component. The direct check: it is one of the token values.
        for &c in &tagged.confidences {
            assert!((0.0..=1.0).contains(&c), "component confidence {c} out of range");
            assert!(
                per_token
                    .tokens
                    .iter()
                    .any(|t| (t.confidence - c).abs() < 1e-15),
                "component confidence {c} is not any token's marginal in {raw:?}"
            );
        }
    }

    // Explicit multi-token components ("NEW YORK" as one PlaceName, "MARTIN
    // LUTHER KING JR" as one StreetName): the component confidence must be the
    // smallest of its member tokens' marginals.
    let mut multi_token_seen = 0usize;
    for addr in [
        "59 ST JAMES PLACE NEW YORK NY 10038",
        "123 MARTIN LUTHER KING JR DR CHICAGO IL 60653",
    ] {
        let per_token = api::parse_with_confidence(addr);
        let tagged = api::tag_native_with_confidence(addr);
        for (idx, (label, _value)) in tagged.components.iter().enumerate() {
            let members: Vec<f64> = per_token
                .tokens
                .iter()
                .filter(|t| &t.label == label)
                .map(|t| t.confidence)
                .collect();
            if members.len() > 1 {
                multi_token_seen += 1;
                let min = members.iter().cloned().fold(f64::INFINITY, f64::min);
                assert!(
                    (tagged.confidences[idx] - min).abs() < 1e-15,
                    "{addr:?} / {label}: expected min {min}, got {}",
                    tagged.confidences[idx]
                );
            }
        }
    }
    assert!(multi_token_seen > 0, "no multi-token component exercised");
}

#[test]
fn sequence_confidence_is_a_probability_and_bounded_by_token_marginals() {
    for raw in corpus(1500) {
        let p = api::parse_with_confidence(&raw);
        assert!(
            (0.0..=1.0 + 1e-12).contains(&p.sequence_confidence),
            "sequence confidence {} out of range for {raw:?}",
            p.sequence_confidence
        );
        // The joint probability of the whole labelling cannot exceed the
        // marginal probability of any single position in it.
        for t in &p.tokens {
            assert!(
                p.sequence_confidence <= t.confidence + 1e-9,
                "sequence confidence {} exceeds token marginal {} on {raw:?}",
                p.sequence_confidence,
                t.confidence
            );
        }
    }
}

#[test]
fn single_token_input_is_handled() {
    // T = 1 is the degenerate forward-backward case (beta is just the scale
    // factor); its marginals must still be a distribution.
    for input in ["123", "Springfield", "60614"] {
        let seq = {
            let tokens = tokenize(input);
            assert_eq!(tokens.len(), 1);
            let facts: Vec<_> = tokens.iter().map(|t| token_facts(t)).collect();
            facts_to_id_seq(&facts)
        };
        let out = tag_attr_ids_with_marginals_for(ModelId::V1, &seq);
        let sum: f64 = out.marginals_at(0).iter().sum();
        assert!((sum - 1.0).abs() < 1e-9, "{input}: marginals sum to {sum}");
        let p = api::parse_with_confidence(input);
        assert_eq!(p.tokens.len(), 1);
        // With one position, the sequence probability IS that token's marginal.
        assert!((p.sequence_confidence - p.tokens[0].confidence).abs() < 1e-9);
    }
}

#[test]
fn empty_input_is_handled() {
    for input in ["", "   ", " \t \n "] {
        let p = api::parse_with_confidence(input);
        assert!(p.tokens.is_empty());
        assert_eq!(p.sequence_confidence, 1.0);
        let t = api::tag_native_with_confidence(input);
        assert!(t.components.is_empty());
        assert!(t.confidences.is_empty());
        assert_eq!(t.address_type, "Ambiguous");
    }
}
