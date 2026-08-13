//! Attribute-id cache: renders `TokenFacts` directly to (attribute id, weight)
//! pairs, skipping string construction and cqdb lookups on the hot path.
//!
//! Per-model: fixed names and bounded families (length, endsinpunc,
//! trailing.zeros) precompute at first touch of that model; only `word:*` is
//! memoized, in a per-thread per-model fast-hash map with negative caching and
//! a per-model size cap. Anything outside the tables falls back to composing
//! the string and resolving via cqdb — identical behavior, just slower.
//!
//! Emission order matches `features::facts_to_attrs` + `tokens_to_attrs`
//! exactly, so f64 accumulation order in scoring is unchanged. Unknown-to-model
//! attributes are dropped, exactly as the string path's `to_attr_id` filter does.

use std::cell::RefCell;
use std::collections::HashMap;
use std::hash::BuildHasherDefault;
use std::sync::LazyLock;

use rustc_hash::FxHasher;

use crate::features::TokenFacts;
use crate::model::{self, ModelId};

const MAX_LEN: usize = 40;
const MAX_ZEROS: usize = 10;

const PREFIXES: [&str; 3] = ["", "previous:", "next:"];

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Slot {
    Base = 0,
    Prev = 1,
    Next = 2,
}

struct SlotIds {
    abbrev: Option<u32>,
    digits_all: Option<u32>,
    digits_some: Option<u32>,
    digits_no: Option<u32>,
    word_false: Option<u32>,
    zeros_false: Option<u32>,
    zeros_runs: Vec<Option<u32>>,
    length_d: Vec<Option<u32>>,
    length_w: Vec<Option<u32>>,
    endsinpunc_false: Option<u32>,
    endsinpunc_ascii: Vec<Option<u32>>,
    directional: Option<u32>,
    street_name: Option<u32>,
    has_vowels: Option<u32>,
}

struct FlagIds {
    addr_start: Option<u32>,
    addr_end: Option<u32>,
    prev_addr_start: Option<u32>,
    next_addr_end: Option<u32>,
}

struct ModelTables {
    slots: [SlotIds; 3],
    flags: FlagIds,
    word_cache_cap: usize,
}

fn resolve(id: ModelId, prefix: &str, name: &str) -> Option<u32> {
    let mut full = String::with_capacity(prefix.len() + name.len());
    full.push_str(prefix);
    full.push_str(name);
    model::attr_id_for(id, &full)
}

fn build_tables(id: ModelId) -> ModelTables {
    let slots = PREFIXES.map(|p| SlotIds {
        abbrev: resolve(id, p, "abbrev"),
        digits_all: resolve(id, p, "digits:all_digits"),
        digits_some: resolve(id, p, "digits:some_digits"),
        digits_no: resolve(id, p, "digits:no_digits"),
        word_false: resolve(id, p, "word"),
        zeros_false: resolve(id, p, "trailing.zeros"),
        zeros_runs: (0..=MAX_ZEROS)
            .map(|n| resolve(id, p, &format!("trailing.zeros:{}", "0".repeat(n))))
            .collect(),
        length_d: (0..=MAX_LEN).map(|n| resolve(id, p, &format!("length:d:{n}"))).collect(),
        length_w: (0..=MAX_LEN).map(|n| resolve(id, p, &format!("length:w:{n}"))).collect(),
        endsinpunc_false: resolve(id, p, "endsinpunc"),
        endsinpunc_ascii: (0u8..=127)
            .map(|b| resolve(id, p, &format!("endsinpunc:{}", b as char)))
            .collect(),
        directional: resolve(id, p, "directional"),
        street_name: resolve(id, p, "street_name"),
        has_vowels: resolve(id, p, "has.vowels"),
    });
    let flags = FlagIds {
        addr_start: model::attr_id_for(id, "address.start"),
        addr_end: model::attr_id_for(id, "address.end"),
        prev_addr_start: model::attr_id_for(id, "previous:address.start"),
        next_addr_end: model::attr_id_for(id, "next:address.end"),
    };
    ModelTables {
        slots,
        flags,
        // Per-model cap, sized deliberately: 2x that model's attribute count.
        word_cache_cap: model::num_attrs_for(id) as usize * 2,
    }
}

static TABLES_V1: LazyLock<ModelTables> = LazyLock::new(|| build_tables(ModelId::V1));
#[cfg(feature = "model-v2")]
static TABLES_V2: LazyLock<ModelTables> = LazyLock::new(|| build_tables(ModelId::V2));

fn tables_for(id: ModelId) -> &'static ModelTables {
    match id {
        ModelId::V1 => &TABLES_V1,
        #[cfg(feature = "model-v2")]
        ModelId::V2 => &TABLES_V2,
    }
}

type WordCache = HashMap<String, [Option<u32>; 3], BuildHasherDefault<FxHasher>>;

thread_local! {
    static WORDS_V1: RefCell<WordCache> = RefCell::new(HashMap::default());
    #[cfg(feature = "model-v2")]
    static WORDS_V2: RefCell<WordCache> = RefCell::new(HashMap::default());
}

fn with_words<R>(id: ModelId, f: impl FnOnce(&mut WordCache) -> R) -> R {
    let cell = match id {
        ModelId::V1 => &WORDS_V1,
        #[cfg(feature = "model-v2")]
        ModelId::V2 => &WORDS_V2,
    };
    cell.with(|c| f(&mut c.borrow_mut()))
}

fn word_ids(id: ModelId, word: &str) -> [Option<u32>; 3] {
    with_words(id, |cache| {
        if let Some(ids) = cache.get(word) {
            return *ids;
        }
        let ids = [
            resolve(id, "", &format!("word:{word}")),
            resolve(id, "previous:", &format!("word:{word}")),
            resolve(id, "next:", &format!("word:{word}")),
        ];
        // Negative results cached too (misses are the expensive case); capped so
        // adversarial input degrades to cqdb fallback speed, never in memory.
        if cache.len() < tables_for(id).word_cache_cap {
            cache.insert(word.to_string(), ids);
        }
        ids
    })
}

#[inline]
fn push(out: &mut Vec<(u32, f64)>, id: Option<u32>, value: f64) {
    if let Some(id) = id {
        out.push((id, value));
    }
}

/// Render one token's base attributes as ids for the given slot, in the exact
/// order of `features::facts_to_attrs`.
fn render_ids(model: ModelId, f: &TokenFacts, slot: Slot, out: &mut Vec<(u32, f64)>) {
    let t = tables_for(model);
    let s = &t.slots[slot as usize];
    let prefix = PREFIXES[slot as usize];

    push(out, s.abbrev, f.abbrev as u8 as f64);
    let digits_id = match f.digits {
        "all_digits" => s.digits_all,
        "some_digits" => s.digits_some,
        _ => s.digits_no,
    };
    push(out, digits_id, 1.0);
    match &f.word {
        Some(w) => push(out, word_ids(model, w)[slot as usize], 1.0),
        None => push(out, s.word_false, 0.0),
    }
    match &f.zeros {
        Some(z) if z.len() <= MAX_ZEROS => push(out, s.zeros_runs[z.len()], 1.0),
        Some(z) => push(out, resolve(model, prefix, &format!("trailing.zeros:{z}")), 1.0),
        None => push(out, s.zeros_false, 0.0),
    }
    let length_id = if f.length <= MAX_LEN {
        if f.length_kind == 'd' { s.length_d[f.length] } else { s.length_w[f.length] }
    } else {
        resolve(model, prefix, &format!("length:{}:{}", f.length_kind, f.length))
    };
    push(out, length_id, 1.0);
    match f.endsinpunc {
        Some(c) if (c as u32) < 128 => push(out, s.endsinpunc_ascii[c as usize], 1.0),
        Some(c) => push(out, resolve(model, prefix, &format!("endsinpunc:{c}")), 1.0),
        None => push(out, s.endsinpunc_false, 0.0),
    }
    push(out, s.directional, f.directional as u8 as f64);
    push(out, s.street_name, f.street_name as u8 as f64);
    push(out, s.has_vowels, f.has_vowels as u8 as f64);
}

/// Full per-token id sequences for a model, mirroring
/// `features::tokens_to_attrs` assembly order exactly.
pub fn facts_to_id_seq_for(model: ModelId, facts: &[TokenFacts]) -> Vec<Vec<(u32, f64)>> {
    let n = facts.len();
    if n == 0 {
        return Vec::new();
    }
    let flags = &tables_for(model).flags;
    let mut out: Vec<Vec<(u32, f64)>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut ids: Vec<(u32, f64)> = Vec::with_capacity(31);
        render_ids(model, &facts[i], Slot::Base, &mut ids);
        if i == 0 {
            push(&mut ids, flags.addr_start, 1.0);
        }
        if i == n - 1 {
            push(&mut ids, flags.addr_end, 1.0);
        }
        if i > 0 {
            render_ids(model, &facts[i - 1], Slot::Prev, &mut ids);
            if i - 1 == 0 && n > 1 {
                push(&mut ids, flags.prev_addr_start, 1.0);
            }
        }
        if i < n - 1 {
            render_ids(model, &facts[i + 1], Slot::Next, &mut ids);
            if i + 1 == n - 1 && n > 1 {
                push(&mut ids, flags.next_addr_end, 1.0);
            }
        }
        out.push(ids);
    }
    out
}

/// v1 convenience wrapper (the parity-protected default path).
pub fn facts_to_id_seq(facts: &[TokenFacts]) -> Vec<Vec<(u32, f64)>> {
    facts_to_id_seq_for(ModelId::V1, facts)
}

/// Test-support: current thread's v1 word-cache size. Not part of the public API.
#[doc(hidden)]
pub fn word_cache_len_for_tests() -> usize {
    with_words(ModelId::V1, |c| c.len())
}
