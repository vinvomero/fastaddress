//! Pure Rust implementation of Conditional Random Fields (CRF) — vendored,
//! inference-only fork of crfs 0.4.1 (see VENDORED.md).
//!
//! # Example
//!
//! ```no_run
//! use crfs::{Attribute, Model};
//!
//! let model_data = std::fs::read("model.crfsuite")?;
//! let model = Model::new(&model_data)?;
//! let tagger = model.tagger()?;
//!
//! let xseq = vec![
//!     vec![Attribute::new("walk", 1.0)],
//!     vec![Attribute::new("shop", 1.0)],
//! ];
//! let result = tagger.tag(&xseq)?;
//! # Ok::<(), std::io::Error>(())
//! ```

mod attribute;
mod context;
mod dataset;
mod feature;
mod model;
mod tagger;

// Re-export main types
pub use self::attribute::Attribute;
pub use self::model::Model;
pub use self::tagger::Tagger;
