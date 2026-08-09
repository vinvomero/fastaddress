use std::io;
use std::sync::LazyLock;

use crfs::{Attribute, Model};

/// The usaddress-trained CRF model, vendored unmodified (see model/PROVENANCE.md).
pub static MODEL_BYTES: &[u8] =
    include_bytes!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../model/usaddr.crfsuite"));

static MODEL: LazyLock<Model<'static>> =
    LazyLock::new(|| Model::new(MODEL_BYTES).expect("vendored usaddr.crfsuite must parse"));

/// Tag a sequence of per-token attribute lists with the usaddress model.
///
/// Attributes must already be in CRFsuite's flattened form (the same strings
/// python-crfsuite's ItemSequence produces from usaddress feature dicts).
pub fn tag_attrs(xseq: &[Vec<Attribute>]) -> io::Result<Vec<String>> {
    let tagger = MODEL.tagger()?;
    let labels = tagger.tag(xseq)?;
    Ok(labels.into_iter().map(|s| s.to_string()).collect())
}
