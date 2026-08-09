use std::cell::RefCell;
use std::io;
use std::sync::LazyLock;

use crfs::{Attribute, Model, Tagger};

/// The usaddress-trained CRF model, vendored unmodified (see model/PROVENANCE.md).
pub static MODEL_BYTES: &[u8] =
    include_bytes!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../model/usaddr.crfsuite"));

static MODEL: LazyLock<Model<'static>> =
    LazyLock::new(|| Model::new(MODEL_BYTES).expect("vendored usaddr.crfsuite must parse"));

thread_local! {
    // One tagger per thread; RefCell because the id fast path needs a mutable
    // receiver for its reusable scratch (single-threaded per thread, no contention).
    static TAGGER: RefCell<Option<Tagger<'static>>> = const { RefCell::new(None) };
}

/// Resolve an attribute name to the model's attribute id (None if unknown).
#[inline]
pub fn attr_id(name: &str) -> Option<u32> {
    MODEL.to_attr_id(name)
}

/// Pre-decoded label string for a label id.
#[inline]
pub fn label_name(lid: u32) -> &'static str {
    MODEL.label_name(lid)
}

/// String-attribute path (oracle/dump; per-call cost is irrelevant here).
///
/// Attributes must already be in CRFsuite's flattened form (the same strings
/// python-crfsuite's ItemSequence produces from usaddress feature dicts).
pub fn tag_attrs(xseq: &[Vec<Attribute>]) -> io::Result<Vec<String>> {
    TAGGER.with(|cell| {
        let mut opt = cell.borrow_mut();
        if opt.is_none() {
            *opt = Some(MODEL.tagger()?);
        }
        let labels = opt.as_ref().unwrap().tag(xseq)?;
        Ok(labels.into_iter().map(|s| s.to_string()).collect())
    })
}

/// Id fast path: attribute ids from `attr_id` (or equal caching); label ids
/// resolve via `label_name`.
pub fn tag_attr_ids(seq: &[Vec<(u32, f64)>]) -> Vec<u32> {
    TAGGER.with(|cell| {
        let mut opt = cell.borrow_mut();
        if opt.is_none() {
            *opt = Some(MODEL.tagger().expect("vendored model tagger must construct"));
        }
        opt.as_mut().unwrap().tag_ids(seq)
    })
}
