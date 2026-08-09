//! Port of usaddress tokenFeatures / tokens2features (v0.5.16).
//!
//! `token_facts` computes the per-token feature decisions once; two renderers
//! consume it: `token_attrs` (CRFsuite attribute strings, oracle/dump path)
//! and the id renderer in `attr_cache` (production fast path). Single source
//! of logic keeps the paths from drifting; the equivalence and parity suites
//! enforce it.
//!
//! String serialization matches python-crfsuite's ItemSequence: bool True ->
//! (key, 1.0); bool False -> (key, 0.0); string value -> ("key:value", 1.0)
//! including empty strings; nested context dicts join with ':'.

use crfs::Attribute;

use crate::vocab::{DIRECTIONS, STREET_NAMES};

// Python \w for our ASCII-dominant scope: Unicode alphanumeric or underscore.
fn is_word(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

// Python str.isdigit() approximation for the parity scope (ASCII decimal digits).
fn is_digit_str(s: &str) -> bool {
    !s.is_empty() && s.bytes().all(|b| b.is_ascii_digit())
}

/// re.sub(r"(^[\W]*)|([^.\w]*$)", "", token): strip leading non-word chars and
/// trailing chars that are neither '.' nor word chars.
fn clean_token(token: &str) -> &str {
    let start = token
        .char_indices()
        .find(|(_, c)| is_word(*c))
        .map(|(i, _)| i)
        .unwrap_or(token.len());
    let stripped = &token[start..];
    let end = stripped
        .char_indices()
        .rev()
        .find(|(_, c)| *c == '.' || is_word(*c))
        .map(|(i, c)| i + c.len_utf8())
        .unwrap_or(0);
    &stripped[..end]
}

/// re.match(r".+[^.\w]", token): true iff the first char is not '\n' and some
/// char at position >= 1 is neither '.' nor a word char.
fn ends_in_punc(token: &str) -> bool {
    let mut chars = token.chars();
    match chars.next() {
        None | Some('\n') => false,
        Some(_) => chars.any(|c| c != '.' && !is_word(c)),
    }
}

/// The per-token feature decisions, computed once per token.
pub struct TokenFacts {
    pub abbrev: bool,
    pub digits: &'static str, // "all_digits" | "some_digits" | "no_digits"
    /// Some(word) when token_abbrev is not all-digits (may be empty string);
    /// None mirrors Python's `word: False` for numeric tokens.
    pub word: Option<String>,
    /// Some(trailing zero run, possibly empty) for numeric tokens; None mirrors False.
    pub zeros: Option<String>,
    pub length_kind: char, // 'd' | 'w'
    pub length: usize,     // codepoint count of token_abbrev
    /// Some(last char of the original token) when endsinpunc fires; None mirrors False.
    pub endsinpunc: Option<char>,
    pub directional: bool,
    pub street_name: bool,
    pub has_vowels: bool,
}

pub fn token_facts(token: &str) -> TokenFacts {
    let token_clean = if matches!(token, "&" | "#" | "\u{00BD}") {
        token
    } else {
        clean_token(token)
    };
    let token_abbrev: String = token_clean.to_lowercase().replace('.', "");
    let abbrev_is_digit = is_digit_str(&token_abbrev);

    let digits = if is_digit_str(token_clean) {
        "all_digits"
    } else if token_clean.bytes().any(|b| b.is_ascii_digit()) {
        "some_digits"
    } else {
        "no_digits"
    };

    let zeros = if abbrev_is_digit {
        let start = token_abbrev.len() - token_abbrev.bytes().rev().take_while(|b| *b == b'0').count();
        Some(token_abbrev[start..].to_string())
    } else {
        None
    };

    let endsinpunc = if ends_in_punc(token) {
        token.chars().last()
    } else {
        None
    };

    let directional = DIRECTIONS.binary_search(&token_abbrev.as_str()).is_ok();
    let street_name = STREET_NAMES.binary_search(&token_abbrev.as_str()).is_ok();
    let has_vowels = token_abbrev
        .chars()
        .skip(1)
        .any(|c| matches!(c, 'a' | 'e' | 'i' | 'o' | 'u'));
    let length = token_abbrev.chars().count();

    TokenFacts {
        abbrev: token_clean.ends_with('.'),
        digits,
        length_kind: if abbrev_is_digit { 'd' } else { 'w' },
        length,
        endsinpunc,
        directional,
        street_name,
        has_vowels,
        word: if abbrev_is_digit { None } else { Some(token_abbrev.clone()) },
        zeros,
    }
}

fn attr(name: &str, value: f64) -> Attribute {
    Attribute::new(name, value)
}

fn attr_kv(key: &str, value: &str) -> Attribute {
    let mut name = String::with_capacity(key.len() + 1 + value.len());
    name.push_str(key);
    name.push(':');
    name.push_str(value);
    Attribute::new(name, 1.0)
}

/// Render facts as CRFsuite attribute strings, in usaddress field order.
pub fn facts_to_attrs(f: &TokenFacts) -> Vec<Attribute> {
    let mut attrs: Vec<Attribute> = Vec::with_capacity(9);
    attrs.push(attr("abbrev", f.abbrev as u8 as f64));
    attrs.push(attr_kv("digits", f.digits));
    match &f.word {
        Some(w) => attrs.push(attr_kv("word", w)),
        None => attrs.push(attr("word", 0.0)),
    }
    match &f.zeros {
        Some(z) => attrs.push(attr_kv("trailing.zeros", z)),
        None => attrs.push(attr("trailing.zeros", 0.0)),
    }
    let mut length = String::with_capacity(12);
    length.push_str("length:");
    length.push(f.length_kind);
    length.push(':');
    length.push_str(&f.length.to_string());
    attrs.push(Attribute::new(length, 1.0));
    match f.endsinpunc {
        Some(c) => {
            let mut name = String::with_capacity(12);
            name.push_str("endsinpunc:");
            name.push(c);
            attrs.push(Attribute::new(name, 1.0));
        }
        None => attrs.push(attr("endsinpunc", 0.0)),
    }
    attrs.push(attr("directional", f.directional as u8 as f64));
    attrs.push(attr("street_name", f.street_name as u8 as f64));
    attrs.push(attr("has.vowels", f.has_vowels as u8 as f64));
    attrs
}

/// Base (non-context) attributes for one token, in usaddress field order.
pub fn token_attrs(token: &str) -> Vec<Attribute> {
    facts_to_attrs(&token_facts(token))
}

fn push_prefixed(out: &mut Vec<Attribute>, prefix: &str, base: &[Attribute]) {
    for a in base {
        let mut name = String::with_capacity(prefix.len() + a.name.len());
        name.push_str(prefix);
        name.push_str(&a.name);
        out.push(Attribute::new(name, a.value));
    }
}

/// Full per-token attribute sequences including previous/next context and
/// address.start / address.end flags, mirroring usaddress.tokens2features.
pub fn tokens_to_attrs(tokens: &[String]) -> Vec<Vec<Attribute>> {
    let n = tokens.len();
    if n == 0 {
        return Vec::new();
    }
    let base: Vec<Vec<Attribute>> = tokens.iter().map(|t| token_attrs(t)).collect();

    let mut out: Vec<Vec<Attribute>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut attrs: Vec<Attribute> = Vec::with_capacity(base[i].len() * 3 + 4);
        attrs.extend_from_slice(&base[i]);
        if i == 0 {
            attrs.push(attr("address.start", 1.0));
        }
        if i == n - 1 {
            attrs.push(attr("address.end", 1.0));
        }
        if i > 0 {
            push_prefixed(&mut attrs, "previous:", &base[i - 1]);
            if i - 1 == 0 && n > 1 {
                attrs.push(attr("previous:address.start", 1.0));
            }
        }
        if i < n - 1 {
            push_prefixed(&mut attrs, "next:", &base[i + 1]);
            if i + 1 == n - 1 && n > 1 {
                attrs.push(attr("next:address.end", 1.0));
            }
        }
        out.push(attrs);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn attr_map(attrs: &[Attribute]) -> std::collections::BTreeMap<String, f64> {
        attrs.iter().map(|a| (a.name.clone(), a.value)).collect()
    }

    #[test]
    fn numeric_token_features() {
        let m = attr_map(&token_attrs("123"));
        assert_eq!(m.get("digits:all_digits"), Some(&1.0));
        assert_eq!(m.get("word"), Some(&0.0));
        assert_eq!(m.get("trailing.zeros:"), Some(&1.0));
        assert_eq!(m.get("length:d:3"), Some(&1.0));
    }

    #[test]
    fn trailing_zeros_captured() {
        let m = attr_map(&token_attrs("6200"));
        assert_eq!(m.get("trailing.zeros:00"), Some(&1.0));
    }

    #[test]
    fn abbreviation_with_period() {
        let m = attr_map(&token_attrs("St."));
        assert_eq!(m.get("abbrev"), Some(&1.0));
        assert_eq!(m.get("word:st"), Some(&1.0));
        assert_eq!(m.get("street_name"), Some(&1.0));
    }

    #[test]
    fn trailing_comma_sets_endsinpunc() {
        let m = attr_map(&token_attrs("Main,"));
        assert_eq!(m.get("endsinpunc:,"), Some(&1.0));
        assert_eq!(m.get("word:main"), Some(&1.0));
    }

    #[test]
    fn directional_token() {
        let m = attr_map(&token_attrs("N"));
        assert_eq!(m.get("directional"), Some(&1.0));
        assert_eq!(m.get("length:w:1"), Some(&1.0));
    }

    #[test]
    fn single_token_gets_both_flags_and_no_context() {
        let seq = tokens_to_attrs(&["123".to_string()]);
        let m = attr_map(&seq[0]);
        assert_eq!(m.get("address.start"), Some(&1.0));
        assert_eq!(m.get("address.end"), Some(&1.0));
        assert!(m.keys().all(|k| !k.starts_with("previous:") && !k.starts_with("next:")));
    }
}
