//! Port of usaddress's user-facing API (v0.5.16): parse(), tag(), and the
//! RepeatedLabelError contract, plus a native mode that never errors on
//! valid input.

use std::fmt;

use crate::attr_cache::facts_to_id_seq_for;
use crate::features::token_facts;
use crate::model::{label_name_for, tag_attr_ids_for, tag_attr_ids_with_marginals_for, ModelId};
use crate::tokenize::tokenize;

/// Mirror of usaddress.RepeatedLabelError: raised in compat mode when a label
/// recurs non-adjacently.
#[derive(Debug, Clone)]
pub struct RepeatedLabelError {
    pub original_string: String,
    pub parsed_string: Vec<(String, String)>,
    pub repeated_label: String,
}

impl fmt::Display for RepeatedLabelError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Unable to tag this string because more than one area of the string has the same label: {} (label {})",
            self.original_string, self.repeated_label
        )
    }
}

impl std::error::Error for RepeatedLabelError {}

/// parse() against a specific model (id fast path; the string path lives in
/// the dump/eval binaries for oracle diffing).
pub fn parse_with(model: ModelId, address: &str) -> Vec<(String, String)> {
    let tokens = tokenize(address);
    if tokens.is_empty() {
        return Vec::new();
    }
    let facts: Vec<_> = tokens.iter().map(|t| token_facts(t)).collect();
    let id_seq = facts_to_id_seq_for(model, &facts);
    let labels = tag_attr_ids_for(model, &id_seq);
    tokens
        .into_iter()
        .zip(labels.into_iter().map(|lid| label_name_for(model, lid).to_string()))
        .collect()
}

/// usaddress.parse(): the parity-protected v1 default.
pub fn parse(address: &str) -> Vec<(String, String)> {
    parse_with(ModelId::V1, address)
}

/// Per-token marginals aligned with the parse output, paired with the vector
/// that receives one aggregated confidence per emitted component.
type ConfSink<'a> = (&'a [f64], &'a mut Vec<f64>);

fn tag_impl(
    address: &str,
    parsed: Vec<(String, String)>,
    merge_repeats: bool,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
    conf: Option<ConfSink<'_>>,
) -> Result<(Vec<(String, String)>, String), RepeatedLabelError> {
    // `conf` is None on the parity-protected default path; `comp_conf` then
    // stays an unallocated empty Vec and the extra work is a handful of
    // never-taken branches.
    let (token_conf, conf_out) = match conf {
        Some((tc, out)) => (Some(tc), Some(out)),
        None => (None, None),
    };
    let mut comp_conf: Vec<f64> = Vec::new();

    // Ordered label -> tokens grouping, mirroring Python's OrderedDict semantics.
    let mut components: Vec<(String, Vec<String>)> = Vec::new();
    // Index of the component last pushed into — after a native-mode merge into an
    // earlier component, an adjacent repeat must follow that component, not the
    // positionally last one.
    let mut last_idx: Option<usize> = None;
    let mut last_label: Option<String> = None;
    let mut is_intersection = false;
    let mut og_labels: Vec<String> = Vec::new();

    for (i, (token, mut label)) in parsed.clone().into_iter().enumerate() {
        if label == "IntersectionSeparator" {
            is_intersection = true;
        }
        if label.contains("StreetName") && is_intersection {
            label = format!("Second{label}");
        }
        og_labels.push(label.clone());
        // Python: `if tag_mapping and tag_mapping.get(label)` — falsy mapped
        // values (empty string) leave the label unchanged.
        if let Some(mapping) = tag_mapping {
            if let Some(mapped) = mapping.get(&label) {
                if !mapped.is_empty() {
                    label = mapped.clone();
                }
            }
        }

        if last_label.as_deref() == Some(label.as_str()) {
            let idx = last_idx.expect("adjacent repeat implies a prior push");
            components[idx].1.push(token);
            merge_conf(&mut comp_conf, token_conf, idx, i);
        } else if let Some(pos) = components.iter().position(|(l, _)| *l == label) {
            if merge_repeats {
                components[pos].1.push(token);
                merge_conf(&mut comp_conf, token_conf, pos, i);
                last_idx = Some(pos);
            } else {
                return Err(RepeatedLabelError {
                    original_string: address.to_string(),
                    parsed_string: parsed,
                    repeated_label: label,
                });
            }
        } else {
            components.push((label.clone(), vec![token]));
            if let Some(tc) = token_conf {
                comp_conf.push(tc[i]);
            }
            last_idx = Some(components.len() - 1);
        }
        last_label = Some(label);
    }

    let tagged: Vec<(String, String)> = components
        .into_iter()
        .map(|(label, tokens)| {
            let joined = tokens.join(" ");
            let trimmed = joined.trim_matches(|c| matches!(c, ' ' | ',' | ';'));
            (label, trimmed.to_string())
        })
        .collect();

    let has_number = og_labels.iter().any(|l| l == "AddressNumber");
    let address_type = if has_number && !is_intersection {
        "Street Address"
    } else if is_intersection && !has_number {
        "Intersection"
    } else if og_labels.iter().any(|l| l == "USPSBoxID") {
        "PO Box"
    } else {
        "Ambiguous"
    };

    if let Some(out) = conf_out {
        *out = comp_conf;
    }
    Ok((tagged, address_type.to_string()))
}

/// Fold token `i`'s marginal into component `idx`'s confidence.
///
/// A component can span several tokens (e.g. "N MAIN" as one StreetName). We
/// aggregate with `min`: the component's confidence is that of its weakest
/// token. This is the conservative reading — "how sure are we about the least
/// certain piece of this component" — and it means a component is never
/// reported as more confident than any token inside it. A mean would let one
/// very confident token mask a genuinely uncertain neighbour.
#[inline]
fn merge_conf(comp_conf: &mut [f64], token_conf: Option<&[f64]>, idx: usize, i: usize) {
    if let Some(tc) = token_conf {
        comp_conf[idx] = comp_conf[idx].min(tc[i]);
    }
}

/// usaddress.tag() compat mode: identical output, including RepeatedLabelError.
pub fn tag(address: &str) -> Result<(Vec<(String, String)>, String), RepeatedLabelError> {
    tag_impl(address, parse_with(ModelId::V1, address), false, None, None)
}

/// usaddress.tag(address, tag_mapping): compat mode with label remapping.
pub fn tag_with_mapping(
    address: &str,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
) -> Result<(Vec<(String, String)>, String), RepeatedLabelError> {
    tag_impl(address, parse_with(ModelId::V1, address), false, tag_mapping, None)
}

/// Native mode: same grouping, but a non-adjacent repeated label merges into
/// its existing component instead of erroring. Never fails on valid input.
pub fn tag_native(address: &str) -> (Vec<(String, String)>, String) {
    tag_impl(address, parse_with(ModelId::V1, address), true, None, None)
        .expect("merge_repeats mode cannot error")
}

/// Model-selecting variants (V2 exists only behind the `model-v2` feature and
/// remains unreleased until the go/no-go gate).
pub fn tag_model(
    model: ModelId,
    address: &str,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
) -> Result<(Vec<(String, String)>, String), RepeatedLabelError> {
    tag_impl(address, parse_with(model, address), false, tag_mapping, None)
}

pub fn tag_native_model(model: ModelId, address: &str) -> (Vec<(String, String)>, String) {
    tag_impl(address, parse_with(model, address), true, None, None)
        .expect("merge_repeats mode cannot error")
}

// ---------------------------------------------------------------------------
// Confidence (marginal probability) API — strictly opt-in.
//
// Everything above runs Viterbi only. The functions below additionally run a
// forward-backward pass over the same score matrices to obtain, per token, the
// marginal probability p(label_t = y_t | input), plus the probability of the
// whole predicted labelling. Nothing above this line calls into it.
// ---------------------------------------------------------------------------

/// One token, its predicted label, and the marginal probability of that label
/// at that position.
#[derive(Debug, Clone, PartialEq)]
pub struct TokenConfidence {
    pub token: String,
    pub label: String,
    /// p(this label at this position | the whole input), in [0, 1].
    pub confidence: f64,
}

/// `parse()` plus confidences.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct ParseConfidence {
    pub tokens: Vec<TokenConfidence>,
    /// p(the entire predicted label sequence | input) = exp(score - log Z).
    /// This is a joint probability over all positions, so it is never larger
    /// than the smallest per-token marginal and shrinks with address length.
    pub sequence_confidence: f64,
}

/// `tag()` plus confidences. `components` and `address_type` are exactly what
/// `tag()` returns; `confidences` is parallel to `components`.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct TagConfidence {
    pub components: Vec<(String, String)>,
    /// One entry per component, aligned by index. Aggregated across the
    /// component's tokens with `min` — see `merge_conf`.
    pub confidences: Vec<f64>,
    pub address_type: String,
    /// p(the entire predicted label sequence | input).
    pub sequence_confidence: f64,
}

/// Core confidence path: tokens, labels, per-token marginals, sequence probability.
fn parse_marginals(model: ModelId, address: &str) -> (Vec<(String, String)>, Vec<f64>, f64) {
    let tokens = tokenize(address);
    if tokens.is_empty() {
        // An empty sequence has exactly one (empty) labelling; probability 1.
        return (Vec::new(), Vec::new(), 1.0);
    }
    let facts: Vec<_> = tokens.iter().map(|t| token_facts(t)).collect();
    let id_seq = facts_to_id_seq_for(model, &facts);
    let out = tag_attr_ids_with_marginals_for(model, &id_seq);
    let confidences: Vec<f64> = out
        .labels
        .iter()
        .enumerate()
        .map(|(t, &lid)| out.marginal(t, lid))
        .collect();
    let parsed: Vec<(String, String)> = tokens
        .into_iter()
        .zip(out.labels.iter().map(|&lid| label_name_for(model, lid).to_string()))
        .collect();
    (parsed, confidences, out.sequence_probability())
}

/// `parse_with()` plus per-token marginals, against a specific model.
pub fn parse_with_confidence_model(model: ModelId, address: &str) -> ParseConfidence {
    let (parsed, confidences, sequence_confidence) = parse_marginals(model, address);
    ParseConfidence {
        tokens: parsed
            .into_iter()
            .zip(confidences)
            .map(|((token, label), confidence)| TokenConfidence { token, label, confidence })
            .collect(),
        sequence_confidence,
    }
}

/// `parse()` plus per-token marginals (v1 model).
pub fn parse_with_confidence(address: &str) -> ParseConfidence {
    parse_with_confidence_model(ModelId::V1, address)
}

fn tag_confidence_impl(
    model: ModelId,
    address: &str,
    merge_repeats: bool,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
) -> Result<TagConfidence, RepeatedLabelError> {
    let (parsed, token_conf, sequence_confidence) = parse_marginals(model, address);
    let mut confidences: Vec<f64> = Vec::new();
    let (components, address_type) = tag_impl(
        address,
        parsed,
        merge_repeats,
        tag_mapping,
        Some((&token_conf, &mut confidences)),
    )?;
    Ok(TagConfidence {
        components,
        confidences,
        address_type,
        sequence_confidence,
    })
}

/// `tag()` plus confidences. Same grouping, same `RepeatedLabelError` contract.
pub fn tag_with_confidence(
    address: &str,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
) -> Result<TagConfidence, RepeatedLabelError> {
    tag_confidence_impl(ModelId::V1, address, false, tag_mapping)
}

/// `tag_native()` plus confidences. Never fails on valid input.
pub fn tag_native_with_confidence(address: &str) -> TagConfidence {
    tag_confidence_impl(ModelId::V1, address, true, None).expect("merge_repeats mode cannot error")
}

/// Model-selecting confidence variants.
pub fn tag_model_with_confidence(
    model: ModelId,
    address: &str,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
) -> Result<TagConfidence, RepeatedLabelError> {
    tag_confidence_impl(model, address, false, tag_mapping)
}

pub fn tag_native_model_with_confidence(model: ModelId, address: &str) -> TagConfidence {
    tag_confidence_impl(model, address, true, None).expect("merge_repeats mode cannot error")
}

#[cfg(test)]
mod tests {
    use super::*;

    // Expected values in these tests were captured from Python usaddress 0.5.16.

    fn pairs(v: &[(&str, &str)]) -> Vec<(String, String)> {
        v.iter().map(|(a, b)| (a.to_string(), b.to_string())).collect()
    }

    #[test]
    fn street_address_matches_python() {
        let (tagged, kind) = tag("123 N Main St Apt 4B Springfield IL 62704").unwrap();
        assert_eq!(kind, "Street Address");
        assert_eq!(
            tagged,
            pairs(&[
                ("AddressNumber", "123"),
                ("StreetNamePreDirectional", "N"),
                ("StreetName", "Main"),
                ("StreetNamePostType", "St"),
                ("OccupancyType", "Apt"),
                ("OccupancyIdentifier", "4B"),
                ("PlaceName", "Springfield"),
                ("StateName", "IL"),
                ("ZipCode", "62704"),
            ])
        );
    }

    #[test]
    fn commas_are_stripped_from_components() {
        let (tagged, kind) = tag("123 Main St, Chicago, IL 60614").unwrap();
        assert_eq!(kind, "Street Address");
        assert_eq!(
            tagged,
            pairs(&[
                ("AddressNumber", "123"),
                ("StreetName", "Main"),
                ("StreetNamePostType", "St"),
                ("PlaceName", "Chicago"),
                ("StateName", "IL"),
                ("ZipCode", "60614"),
            ])
        );
    }

    #[test]
    fn po_box_matches_python() {
        let (tagged, kind) = tag("PO BOX 5410 CHICAGO IL 60680").unwrap();
        assert_eq!(kind, "PO Box");
        assert_eq!(
            tagged,
            pairs(&[
                ("USPSBoxType", "PO BOX"),
                ("USPSBoxID", "5410"),
                ("PlaceName", "CHICAGO"),
                ("StateName", "IL"),
                ("ZipCode", "60680"),
            ])
        );
    }

    #[test]
    fn empty_and_whitespace_input_is_ambiguous_not_a_crash() {
        for input in ["", "   ", " \t \n "] {
            let (tagged, kind) = tag(input).unwrap();
            assert!(tagged.is_empty());
            assert_eq!(kind, "Ambiguous");
            let (native_tagged, native_kind) = tag_native(input);
            assert!(native_tagged.is_empty());
            assert_eq!(native_kind, "Ambiguous");
        }
    }

    #[test]
    fn saint_name_street_raises_in_compat_mode() {
        let err = tag("59 ST JAMES PLACE NEW YORK NY 10038").unwrap_err();
        assert!(!err.repeated_label.is_empty());
        assert_eq!(err.original_string, "59 ST JAMES PLACE NEW YORK NY 10038");
    }

    #[test]
    fn saint_name_street_succeeds_in_native_mode() {
        let (tagged, _kind) = tag_native("59 ST JAMES PLACE NEW YORK NY 10038");
        assert!(!tagged.is_empty());
        assert!(tagged.iter().any(|(_, comp)| comp.contains("59")));
    }
}
