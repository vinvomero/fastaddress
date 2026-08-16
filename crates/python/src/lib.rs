use std::collections::HashMap;

use pyo3::exceptions::{PyException, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use fastaddress_core::model::ModelId;

pyo3::create_exception!(
    fastaddress,
    RepeatedLabelError,
    PyException,
    "Raised when more than one area of the address string has the same label (usaddress-compatible)."
);

/// Build a RepeatedLabelError carrying usaddress's exact contract: the
/// `message`, `original_string`, and `parsed_string` attributes, and a str()
/// identical to probableparsing's MESSAGE (+ DOCS_MESSAGE) as usaddress
/// renders it — person/corporation wording and all, because drop-in means
/// drop-in. `parsed_string` is a list of (token, label) tuples; its repr in
/// the message comes from Python itself so quoting matches byte-for-byte.
fn repeated_label_err(py: Python<'_>, e: fastaddress_core::api::RepeatedLabelError) -> PyErr {
    let build = || -> PyResult<PyErr> {
        let parsed = PyList::new(
            py,
            e.parsed_string
                .iter()
                .map(|(t, l)| (t.as_str(), l.as_str())),
        )?;
        let parsed_repr: String = parsed.repr()?.extract()?;
        let message = format!(
            "\nERROR: Unable to tag this string because more than one area of the string has the same label\n\n\
             ORIGINAL STRING:  {}\n\
             PARSED TOKENS:    {}\n\
             UNCERTAIN LABEL:  {}\n\n\
             When this error is raised, it's likely that either (1) the string is not a valid person/corporation name or (2) some tokens were labeled incorrectly\n\n\
             To report an error in labeling a valid name, open an issue at https://github.com/datamade/usaddress/issues/new - it'll help us continue to improve probablepeople!\n\n\
             For more information, see the documentation at https://usaddress.readthedocs.io/",
            e.original_string, parsed_repr, e.repeated_label
        );
        let exc_type = py.get_type::<RepeatedLabelError>();
        let inst = exc_type.call1((message.clone(),))?;
        inst.setattr("message", message)?;
        inst.setattr("original_string", e.original_string.as_str())?;
        inst.setattr("parsed_string", &parsed)?;
        Ok(PyErr::from_value(inst))
    };
    build().unwrap_or_else(|err| err)
}

/// Resolve the `model=` keyword to a ModelId. Kept as a plain function
/// (String error, no Python types) so the feature-off path is unit-testable
/// with `cargo test`.
fn resolve_model(model: &str) -> Result<ModelId, String> {
    match model {
        "v1" => Ok(ModelId::V1),
        #[cfg(feature = "model-v2")]
        "v2" => Ok(ModelId::V2),
        #[cfg(not(feature = "model-v2"))]
        "v2" => Err("model 'v2' not available in this build".to_string()),
        other => Err(format!("unknown model '{other}'; valid options: 'v1', 'v2'")),
    }
}

fn model_arg(model: &str) -> PyResult<ModelId> {
    resolve_model(model).map_err(PyValueError::new_err)
}

/// usaddress.parse(): list of (token, label) tuples.
#[pyfunction]
#[pyo3(signature = (address_string, model="v1"))]
fn parse(address_string: &str, model: &str) -> PyResult<Vec<(String, String)>> {
    let model = model_arg(model)?;
    Ok(fastaddress_core::api::parse_with(model, address_string))
}

/// usaddress.tag(): (OrderedDict-equivalent dict, address_type). Raises
/// RepeatedLabelError exactly where usaddress does.
#[pyfunction]
#[pyo3(signature = (address_string, tag_mapping=None, model="v1"))]
fn tag<'py>(
    py: Python<'py>,
    address_string: &str,
    tag_mapping: Option<HashMap<String, String>>,
    model: &str,
) -> PyResult<(Bound<'py, PyDict>, String)> {
    let model = model_arg(model)?;
    match fastaddress_core::api::tag_model(model, address_string, tag_mapping.as_ref()) {
        Ok((pairs, kind)) => {
            let dict = PyDict::new(py);
            for (label, component) in pairs {
                dict.set_item(label, component)?;
            }
            Ok((dict, kind))
        }
        Err(e) => Err(repeated_label_err(py, e)),
    }
}

/// Native mode: never raises on valid input; non-adjacent repeated labels merge.
#[pyfunction]
#[pyo3(signature = (address_string, model="v1"))]
fn tag_native<'py>(
    py: Python<'py>,
    address_string: &str,
    model: &str,
) -> PyResult<(Bound<'py, PyDict>, String)> {
    let model = model_arg(model)?;
    let (pairs, kind) = fastaddress_core::api::tag_native_model(model, address_string);
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
#[pyo3(signature = (address_string, model="v1"))]
fn parse_with_confidence(address_string: &str, model: &str) -> PyResult<Vec<(String, String, f64)>> {
    let model = model_arg(model)?;
    Ok(fastaddress_core::api::parse_with_confidence_model(model, address_string)
        .tokens
        .into_iter()
        .map(|t| (t.token, t.label, t.confidence))
        .collect())
}

fn confidence_result<'py>(
    py: Python<'py>,
    c: fastaddress_core::api::TagConfidence,
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
#[pyo3(signature = (address_string, tag_mapping=None, model="v1"))]
fn tag_with_confidence<'py>(
    py: Python<'py>,
    address_string: &str,
    tag_mapping: Option<HashMap<String, String>>,
    model: &str,
) -> PyResult<(Bound<'py, PyDict>, String, Bound<'py, PyDict>, f64)> {
    let model = model_arg(model)?;
    match fastaddress_core::api::tag_model_with_confidence(model, address_string, tag_mapping.as_ref()) {
        Ok(c) => confidence_result(py, c),
        Err(e) => Err(repeated_label_err(py, e)),
    }
}

/// tag_native() with confidences; never raises on valid input.
#[pyfunction]
#[pyo3(signature = (address_string, model="v1"))]
fn tag_native_with_confidence<'py>(
    py: Python<'py>,
    address_string: &str,
    model: &str,
) -> PyResult<(Bound<'py, PyDict>, String, Bound<'py, PyDict>, f64)> {
    let model = model_arg(model)?;
    confidence_result(
        py,
        fastaddress_core::api::tag_native_model_with_confidence(model, address_string),
    )
}

#[pymodule]
fn fastaddress(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(tag, m)?)?;
    m.add_function(wrap_pyfunction!(tag_native, m)?)?;
    m.add_function(wrap_pyfunction!(parse_with_confidence, m)?)?;
    m.add_function(wrap_pyfunction!(tag_with_confidence, m)?)?;
    m.add_function(wrap_pyfunction!(tag_native_with_confidence, m)?)?;
    m.add("RepeatedLabelError", m.py().get_type::<RepeatedLabelError>())?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn v1_always_resolves() {
        assert!(matches!(resolve_model("v1"), Ok(ModelId::V1)));
    }

    #[cfg(feature = "model-v2")]
    #[test]
    fn v2_resolves_when_feature_on() {
        assert!(matches!(resolve_model("v2"), Ok(ModelId::V2)));
    }

    #[cfg(not(feature = "model-v2"))]
    #[test]
    fn v2_errors_when_feature_off() {
        assert_eq!(
            resolve_model("v2").unwrap_err(),
            "model 'v2' not available in this build"
        );
    }

    #[test]
    fn unknown_model_names_the_valid_options() {
        let err = resolve_model("nope").unwrap_err();
        assert!(err.contains("nope"), "error should name the bad value: {err}");
        assert!(err.contains("'v1'") && err.contains("'v2'"), "error should list options: {err}");
    }
}
