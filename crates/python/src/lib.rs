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

#[pymodule]
fn usaddr(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(tag, m)?)?;
    m.add_function(wrap_pyfunction!(tag_native, m)?)?;
    m.add("RepeatedLabelError", m.py().get_type::<RepeatedLabelError>())?;
    Ok(())
}
