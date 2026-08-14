use std::collections::HashMap;

use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::PyDict;

pyo3::create_exception!(
    usaddr,
    RepeatedLabelError,
    PyException,
    "Raised when more than one area of the address string has the same label (usaddress-compatible)."
);

/// usaddress.parse(): list of (token, label) tuples.
#[pyfunction]
fn parse(address: &str) -> Vec<(String, String)> {
    usaddr_core::api::parse(address)
}

/// usaddress.tag(): (OrderedDict-equivalent dict, address_type). Raises
/// RepeatedLabelError exactly where usaddress does.
#[pyfunction]
#[pyo3(signature = (address, tag_mapping=None))]
fn tag<'py>(
    py: Python<'py>,
    address: &str,
    tag_mapping: Option<HashMap<String, String>>,
) -> PyResult<(Bound<'py, PyDict>, String)> {
    match usaddr_core::api::tag_with_mapping(address, tag_mapping.as_ref()) {
        Ok((pairs, kind)) => {
            let dict = PyDict::new(py);
            for (label, component) in pairs {
                dict.set_item(label, component)?;
            }
            Ok((dict, kind))
        }
        Err(e) => Err(RepeatedLabelError::new_err(e.to_string())),
    }
}

/// Native mode: never raises on valid input; non-adjacent repeated labels merge.
#[pyfunction]
fn tag_native<'py>(py: Python<'py>, address: &str) -> PyResult<(Bound<'py, PyDict>, String)> {
    let (pairs, kind) = usaddr_core::api::tag_native(address);
    let dict = PyDict::new(py);
    for (label, component) in pairs {
        dict.set_item(label, component)?;
    }
    Ok((dict, kind))
}

// ---- Confidence (marginal probability) API — opt-in, additive ----------------
//
// `parse` / `tag` / `tag_native` above are unchanged and never run the
// forward-backward pass. The functions below do, and pay for it.

/// parse() with confidences: list of (token, label, confidence) triples, where
/// confidence is the CRF marginal probability of that label at that position.
#[pyfunction]
fn parse_with_confidence(address: &str) -> Vec<(String, String, f64)> {
    usaddr_core::api::parse_with_confidence(address)
        .tokens
        .into_iter()
        .map(|t| (t.token, t.label, t.confidence))
        .collect()
}

fn confidence_result<'py>(
    py: Python<'py>,
    c: usaddr_core::api::TagConfidence,
) -> PyResult<(Bound<'py, PyDict>, String, Bound<'py, PyDict>, f64)> {
    let tagged = PyDict::new(py);
    let confidences = PyDict::new(py);
    for ((label, component), conf) in c.components.into_iter().zip(c.confidences) {
        tagged.set_item(&label, component)?;
        confidences.set_item(&label, conf)?;
    }
    Ok((tagged, c.address_type, confidences, c.sequence_confidence))
}

/// tag() with confidences: (tagged, address_type, confidences, sequence_confidence).
///
/// `tagged` and `address_type` are exactly what `tag()` returns. `confidences`
/// is keyed by the same labels and holds the marginal probability of each
/// component — for a component spanning several tokens, the minimum of its
/// tokens' marginals. `sequence_confidence` is the probability of the entire
/// predicted labelling. Raises RepeatedLabelError exactly where `tag()` does.
#[pyfunction]
#[pyo3(signature = (address, tag_mapping=None))]
fn tag_with_confidence<'py>(
    py: Python<'py>,
    address: &str,
    tag_mapping: Option<HashMap<String, String>>,
) -> PyResult<(Bound<'py, PyDict>, String, Bound<'py, PyDict>, f64)> {
    match usaddr_core::api::tag_with_confidence(address, tag_mapping.as_ref()) {
        Ok(c) => confidence_result(py, c),
        Err(e) => Err(RepeatedLabelError::new_err(e.to_string())),
    }
}

/// tag_native() with confidences; never raises on valid input.
#[pyfunction]
fn tag_native_with_confidence<'py>(
    py: Python<'py>,
    address: &str,
) -> PyResult<(Bound<'py, PyDict>, String, Bound<'py, PyDict>, f64)> {
    confidence_result(py, usaddr_core::api::tag_native_with_confidence(address))
}

#[pymodule]
fn usaddr(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(tag, m)?)?;
    m.add_function(wrap_pyfunction!(tag_native, m)?)?;
    m.add_function(wrap_pyfunction!(parse_with_confidence, m)?)?;
    m.add_function(wrap_pyfunction!(tag_with_confidence, m)?)?;
    m.add_function(wrap_pyfunction!(tag_native_with_confidence, m)?)?;
    m.add("RepeatedLabelError", m.py().get_type::<RepeatedLabelError>())?;
    Ok(())
}
