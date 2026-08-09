//! Port of usaddress's user-facing API (v0.5.16): parse(), tag(), and the
//! RepeatedLabelError contract, plus a native mode that never errors on
//! valid input.

use std::fmt;

use crate::features::tokens_to_attrs;
use crate::model::tag_attrs;
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

/// usaddress.parse(): token/label pairs straight from the model.
pub fn parse(address: &str) -> Vec<(String, String)> {
    let tokens = tokenize(address);
    if tokens.is_empty() {
        return Vec::new();
    }
    let attr_seq = tokens_to_attrs(&tokens);
    let labels = tag_attrs(&attr_seq).expect("model tagging must not fail on valid attributes");
    tokens.into_iter().zip(labels).collect()
}

fn tag_impl(
    address: &str,
    merge_repeats: bool,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
) -> Result<(Vec<(String, String)>, String), RepeatedLabelError> {
    // Ordered label -> tokens grouping, mirroring Python's OrderedDict semantics.
    let mut components: Vec<(String, Vec<String>)> = Vec::new();
    // Index of the component last pushed into — after a native-mode merge into an
    // earlier component, an adjacent repeat must follow that component, not the
    // positionally last one.
    let mut last_idx: Option<usize> = None;
    let mut last_label: Option<String> = None;
    let mut is_intersection = false;
    let mut og_labels: Vec<String> = Vec::new();

    let parsed = parse(address);
    for (token, mut label) in parsed.clone() {
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
            components[last_idx.expect("adjacent repeat implies a prior push")]
                .1
                .push(token);
        } else if let Some(pos) = components.iter().position(|(l, _)| *l == label) {
            if merge_repeats {
                components[pos].1.push(token);
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

    Ok((tagged, address_type.to_string()))
}

/// usaddress.tag() compat mode: identical output, including RepeatedLabelError.
pub fn tag(address: &str) -> Result<(Vec<(String, String)>, String), RepeatedLabelError> {
    tag_impl(address, false, None)
}

/// usaddress.tag(address, tag_mapping): compat mode with label remapping.
pub fn tag_with_mapping(
    address: &str,
    tag_mapping: Option<&std::collections::HashMap<String, String>>,
) -> Result<(Vec<(String, String)>, String), RepeatedLabelError> {
    tag_impl(address, false, tag_mapping)
}

/// Native mode: same grouping, but a non-adjacent repeated label merges into
/// its existing component instead of erroring. Never fails on valid input.
pub fn tag_native(address: &str) -> (Vec<(String, String)>, String) {
    tag_impl(address, true, None).expect("merge_repeats mode cannot error")
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
