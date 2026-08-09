//! Attribute-id cache: renders `TokenFacts` directly to (attribute id, weight)
//! pairs, skipping string construction and cqdb lookups on the hot path.
//!
//! Fixed names resolve once at init. Bounded families (length, endsinpunc,
//! trailing.zeros) are precomputed into tables. Only `word:*` is memoized, in
//! a per-thread fast-hash map with negative caching and a size cap; anything
//! outside the tables falls back to composing the string and resolving via
//! cqdb — identical behavior, just slower.
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
use crate::model;

const MAX_LEN: usize = 40; // length:{d,w}:N precomputed for N <= MAX_LEN
const MAX_ZEROS: usize = 10; // trailing.zeros:<run> precomputed for runs <= MAX_ZEROS

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
    zeros_runs: Vec<Option<u32>>, // index = run length ("" .. "0"*MAX_ZEROS)
    length_d: Vec<Option<u32>>,   // index = N
    length_w: Vec<Option<u32>>,
    endsinpunc_false: Option<u32>,
    endsinpunc_ascii: Vec<Option<u32>>, // index = byte value
    directional: Option<u32>,
    street_name: Option<u32>,
    has_vowels: Option<u32>,
}

fn resolve(prefix: &str, name: &str) -> Option<u32> {
    let mut full = String::with_capacity(prefix.len() + name.len());
    full.push_str(prefix);
    full.push_str(name);
    model::attr_id(&full)
}

static SLOTS: LazyLock<[SlotIds; 3]> = LazyLock::new(|| {
    PREFIXES.map(|p| SlotIds {
        abbrev: resolve(p, "abbrev"),
        digits_all: resolve(p, "digits:all_digits"),
        digits_some: resolve(p, "digits:some_digits"),
        digits_no: resolve(p, "digits:no_digits"),
        word_false: resolve(p, "word"),
        zeros_false: resolve(p, "trailing.zeros"),
        zeros_runs: (0..=MAX_ZEROS)
            .map(|n| resolve(p, &format!("trailing.zeros:{}", "0".repeat(n))))
            .collect(),
        length_d: (0..=MAX_LEN).map(|n| resolve(p, &format!("length:d:{n}"))).collect(),
        length_w: (0..=MAX_LEN).map(|n| resolve(p, &format!("length:w:{n}"))).collect(),
        endsinpunc_false: resolve(p, "endsinpunc"),
        endsinpunc_ascii: (0u8..=127)
            .map(|b| resolve(p, &format!("endsinpunc:{}", b as char)))
            .collect(),
        directional: resolve(p, "directional"),
        street_name: resolve(p, "street_name"),
        has_vowels: resolve(p, "has.vowels"),
    })
});

static FLAG_IDS: LazyLock<FlagIds> = LazyLock::new(|| FlagIds {
    addr_start: model::attr_id("address.start"),
    addr_end: model::attr_id("address.end"),
    prev_addr_start: model::attr_id("previous:address.start"),
    next_addr_end: model::attr_id("next:address.end"),
});

struct FlagIds {
    addr_start: Option<u32>,
    addr_end: Option<u32>,
    prev_addr_start: Option<u32>,
    next_addr_end: Option<u32>,
}

type WordCache = HashMap<String, [Option<u32>; 3], BuildHasherDefault<FxHasher>>;

thread_local! {
    static WORDS: RefCell<WordCache> = RefCell::new(HashMap::default());
}

static WORD_CACHE_CAP: LazyLock<usize> = LazyLock::new(|| model::num_attrs() as usize * 2);

fn word_ids(word: &str) -> [Option<u32>; 3] {
    WORDS.with(|cell| {
        let mut cache = cell.borrow_mut();
        if let Some(ids) = cache.get(word) {
            return *ids;
        }
        let ids = [
            resolve("", &format!("word:{word}")),
            resolve("previous:", &format!("word:{word}")),
            resolve("next:", &format!("word:{word}")),
        ];
        // Negative results cached too (misses are the expensive case); capped so
        // adversarial input degrades to cqdb fallback speed, never in memory.
        if cache.len() < *WORD_CACHE_CAP {
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
fn render_ids(f: &TokenFacts, slot: Slot, out: &mut Vec<(u32, f64)>) {
    let s = &SLOTS[slot as usize];
    let prefix = PREFIXES[slot as usize];

    push(out, s.abbrev, f.abbrev as u8 as f64);
    let digits_id = match f.digits {
        "all_digits" => s.digits_all,
        "some_digits" => s.digits_some,
        _ => s.digits_no,
    };
    push(out, digits_id, 1.0);
    match &f.word {
        Some(w) => push(out, word_ids(w)[slot as usize], 1.0),
        None => push(out, s.word_false, 0.0),
    }
    match &f.zeros {
        Some(z) if z.len() <= MAX_ZEROS => push(out, s.zeros_runs[z.len()], 1.0),
        Some(z) => push(out, resolve(prefix, &format!("trailing.zeros:{z}")), 1.0),
        None => push(out, s.zeros_false, 0.0),
    }
    let length_id = if f.length <= MAX_LEN {
        if f.length_kind == 'd' { s.length_d[f.length] } else { s.length_w[f.length] }
    } else {
        resolve(prefix, &format!("length:{}:{}", f.length_kind, f.length))
    };
    push(out, length_id, 1.0);
    match f.endsinpunc {
        Some(c) if (c as u32) < 128 => push(out, s.endsinpunc_ascii[c as usize], 1.0),
        Some(c) => push(out, resolve(prefix, &format!("endsinpunc:{c}")), 1.0),
        None => push(out, s.endsinpunc_false, 0.0),
    }
    push(out, s.directional, f.directional as u8 as f64);
    push(out, s.street_name, f.street_name as u8 as f64);
    push(out, s.has_vowels, f.has_vowels as u8 as f64);
}

/// Full per-token id sequences, mirroring `features::tokens_to_attrs` assembly
/// order exactly (base, start/end flags, previous:, previous-start, next:,
/// next-end).
pub fn facts_to_id_seq(facts: &[TokenFacts]) -> Vec<Vec<(u32, f64)>> {
    let n = facts.len();
    let flags = &*FLAG_IDS;
    let mut out: Vec<Vec<(u32, f64)>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut ids: Vec<(u32, f64)> = Vec::with_capacity(31);
        render_ids(&facts[i], Slot::Base, &mut ids);
        if i == 0 {
            push(&mut ids, flags.addr_start, 1.0);
        }
        if i == n - 1 {
            push(&mut ids, flags.addr_end, 1.0);
        }
        if i > 0 {
            render_ids(&facts[i - 1], Slot::Prev, &mut ids);
            if i - 1 == 0 && n > 1 {
                push(&mut ids, flags.prev_addr_start, 1.0);
            }
        }
        if i < n - 1 {
            render_ids(&facts[i + 1], Slot::Next, &mut ids);
            if i + 1 == n - 1 && n > 1 {
                push(&mut ids, flags.next_addr_end, 1.0);
            }
        }
        out.push(ids);
    }
    out
}

/// Test-support: current thread's word-cache size. Not part of the public API.
#[doc(hidden)]
pub fn word_cache_len_for_tests() -> usize {
    WORDS.with(|cell| cell.borrow().len())
}
