pub mod api;
pub mod attr_cache;
pub mod features;
pub mod model;
pub mod tokenize;
pub mod vocab;

// Allocation-heavy feature extraction is the hot path; mimalloc measurably
// outperforms the Windows default heap for this pattern.
#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;
