//! Port of usaddress tokenFeatures / tokens2features (v0.5.16), emitting the
//! flattened CRFsuite attributes python-crfsuite's ItemSequence produces:
//! bool True -> (key, 1.0); bool False -> (key, 0.0); string value ->
//! ("key:value", 1.0) including empty strings; nested context dicts join with
//! ':' ("previous:word:main"). Parity is enforced by the differential suite.

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

/// Base (non-context) attributes for one token, in usaddress field order.
pub fn token_attrs(token: &str) -> Vec<Attribute> {
    let token_clean = if matches!(token, "&" | "#" | "\u{00BD}") {
        token
    } else {
        clean_token(token)
    };
    let token_abbrev: String = token_clean.to_lowercase().replace('.', "");
    let abbrev_is_digit = is_digit_str(&token_abbrev);

    let mut attrs: Vec<Attribute> = Vec::with_capacity(9);

    attrs.push(attr(
        "abbrev",
        (token_clean.ends_with('.')) as u8 as f64,
    ));

    let digits = if is_digit_str(token_clean) {
        "all_digits"
    } else if token_clean.bytes().any(|b| b.is_ascii_digit()) {
        "some_digits"
    } else {
        "no_digits"
    };
    attrs.push(attr_kv("digits", digits));

    if abbrev_is_digit {
        attrs.push(attr("word", 0.0));
    } else {
        attrs.push(attr_kv("word", &token_abbrev));
    }

    if abbrev_is_digit {
        let zeros_start = token_abbrev.len() - token_abbrev.bytes().rev().take_while(|b| *b == b'0').count();
        attrs.push(attr_kv("trailing.zeros", &token_abbrev[zeros_start..]));
    } else {
        attrs.push(attr("trailing.zeros", 0.0));
    }

    let mut length = String::with_capacity(12);
    length.push_str("length:");
    length.push(if abbrev_is_digit { 'd' } else { 'w' });
    length.push(':');
    length.push_str(itoa(token_abbrev.chars().count()).as_str());
    attrs.push(Attribute::new(length, 1.0));

    if ends_in_punc(token) {
        let last = token.chars().last().unwrap();
        let mut name = String::with_capacity(12);
        name.push_str("endsinpunc:");
        name.push(last);
        attrs.push(Attribute::new(name, 1.0));
    } else {
        attrs.push(attr("endsinpunc", 0.0));
    }

    attrs.push(attr(
        "directional",
        DIRECTIONS.binary_search(&token_abbrev.as_str()).is_ok() as u8 as f64,
    ));
    attrs.push(attr(
        "street_name",
        STREET_NAMES.binary_search(&token_abbrev.as_str()).is_ok() as u8 as f64,
    ));

    let has_vowels = token_abbrev
        .chars()
        .skip(1)
        .any(|c| matches!(c, 'a' | 'e' | 'i' | 'o' | 'u'));
    attrs.push(attr("has.vowels", has_vowels as u8 as f64));

    attrs
}

fn itoa(n: usize) -> String {
    n.to_string()
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
