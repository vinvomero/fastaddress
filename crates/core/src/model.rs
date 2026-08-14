use std::cell::RefCell;
use std::io;
use std::sync::LazyLock;

use crfs::{Attribute, Model, TagMarginals, Tagger};

/// Which embedded model to run. V1 is the usaddress-pinned parity model and
/// the permanent default; V2 exists only behind the `model-v2` feature and
/// stays unreleased until the plan's go/no-go gate enables it.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum ModelId {
    V1,
    #[cfg(feature = "model-v2")]
    V2,
}

/// The usaddress-trained CRF model, vendored unmodified (see model/PROVENANCE.md).
pub static MODEL_BYTES: &[u8] =
    include_bytes!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../model/usaddr.crfsuite"));

#[cfg(feature = "model-v2")]
pub static MODEL_V2_BYTES: &[u8] =
    include_bytes!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../model/usaddr_v2.crfsuite"));

static MODEL: LazyLock<Model<'static>> =
    LazyLock::new(|| Model::new(MODEL_BYTES).expect("vendored usaddr.crfsuite must parse"));

#[cfg(feature = "model-v2")]
static MODEL_V2: LazyLock<Model<'static>> =
    LazyLock::new(|| Model::new(MODEL_V2_BYTES).expect("usaddr_v2.crfsuite must parse"));

fn model_for(id: ModelId) -> &'static Model<'static> {
    match id {
        ModelId::V1 => &MODEL,
        #[cfg(feature = "model-v2")]
        ModelId::V2 => &MODEL_V2,
    }
}

thread_local! {
    // One tagger per thread per model; RefCell because the id fast path needs a
    // mutable receiver for its reusable scratch.
    static TAGGER_V1: RefCell<Option<Tagger<'static>>> = const { RefCell::new(None) };
    #[cfg(feature = "model-v2")]
    static TAGGER_V2: RefCell<Option<Tagger<'static>>> = const { RefCell::new(None) };
}

fn with_tagger<R>(id: ModelId, f: impl FnOnce(&mut Tagger<'static>) -> R) -> R {
    let cell = match id {
        ModelId::V1 => &TAGGER_V1,
        #[cfg(feature = "model-v2")]
        ModelId::V2 => &TAGGER_V2,
    };
    cell.with(|c| {
        let mut opt = c.borrow_mut();
        if opt.is_none() {
            *opt = Some(model_for(id).tagger().expect("embedded model tagger must construct"));
        }
        f(opt.as_mut().unwrap())
    })
}

/// Number of attributes in a model (sizes that model's word-cache cap).
#[inline]
pub fn num_attrs_for(id: ModelId) -> u32 {
    model_for(id).num_attrs()
}

/// Resolve an attribute name to a model's attribute id (None if unknown).
#[inline]
pub fn attr_id_for(id: ModelId, name: &str) -> Option<u32> {
    model_for(id).to_attr_id(name)
}

/// Pre-decoded label string for a label id.
#[inline]
pub fn label_name_for(id: ModelId, lid: u32) -> &'static str {
    model_for(id).label_name(lid)
}

/// String-attribute path (oracle/dump; per-call cost is irrelevant here).
pub fn tag_attrs_for(id: ModelId, xseq: &[Vec<Attribute>]) -> io::Result<Vec<String>> {
    with_tagger(id, |tagger| {
        let labels = tagger.tag(xseq)?;
        Ok(labels.into_iter().map(|s| s.to_string()).collect())
    })
}

/// Id fast path: attribute ids from `attr_id_for` (or equal caching); label ids
/// resolve via `label_name_for`.
pub fn tag_attr_ids_for(id: ModelId, seq: &[Vec<(u32, f64)>]) -> Vec<u32> {
    with_tagger(id, |tagger| tagger.tag_ids(seq))
}

/// Id path with marginals: same Viterbi labels as `tag_attr_ids_for`, plus the
/// forward-backward marginal probabilities and log Z. Opt-in — callers of
/// `tag_attr_ids_for` never run the forward-backward pass.
pub fn tag_attr_ids_with_marginals_for(id: ModelId, seq: &[Vec<(u32, f64)>]) -> TagMarginals {
    with_tagger(id, |tagger| tagger.tag_ids_with_marginals(seq))
}

// ---- v1 convenience API (unchanged surface; the parity-protected default) ----

#[inline]
pub fn num_attrs() -> u32 {
    num_attrs_for(ModelId::V1)
}

#[inline]
pub fn attr_id(name: &str) -> Option<u32> {
    attr_id_for(ModelId::V1, name)
}

#[inline]
pub fn label_name(lid: u32) -> &'static str {
    label_name_for(ModelId::V1, lid)
}

pub fn tag_attrs(xseq: &[Vec<Attribute>]) -> io::Result<Vec<String>> {
    tag_attrs_for(ModelId::V1, xseq)
}

pub fn tag_attr_ids(seq: &[Vec<(u32, f64)>]) -> Vec<u32> {
    tag_attr_ids_for(ModelId::V1, seq)
}
