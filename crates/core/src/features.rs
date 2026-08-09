//! Port of usaddress tokenFeatures / tokens2features (v0.5.16), emitting the
//! flattened CRFsuite attributes python-crfsuite's ItemSequence produces:
//! bool True -> (key, 1.0); bool False -> (key, 0.0); string value ->
//! ("key:value", 1.0) including empty strings; nested context dicts join with
//! ':' ("previous:word:main"). Parity is enforced by the differential suite.

use crate::vocab::{DIRECTIONS, STREET_NAMES};

pub type Attr = (String, f64);

// Python \w for our ASCII-dominant scope: Unicode alphanumeric or underscore.
fn is_word(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

// Python str.isdigit() approximation for the parity scope (ASCII decimal digits).
fn is_digit_str(s: &str) -> bool {
    !s.is_empty() && s.chars().all(|c| c.is_ascii_digit())
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

/// Base (non-context) attributes for one token, in usaddress field order.
pub fn token_attrs(token: &str) -> Vec<Attr> {
    let token_clean = if matches!(token, "&" | "#" | "\u{00BD}") {
        token
    } else {
        clean_token(token)
    };
    let token_abbrev: String = token_clean.to_lowercase().replace('.', "");
    let abbrev_is_digit = is_digit_str(&token_abbrev);

    let mut attrs: Vec<Attr> = Vec::with_capacity(9);

    // abbrev
    attrs.push((
        "abbrev".into(),
        (token_clean.chars().last() == Some('.')) as u8 as f64,
    ));

    // digits (on token_clean): all via isdigit, some via ASCII digit presence
    let digits = if is_digit_str(token_clean) {
        "all_digits"
    } else if token_clean.chars().any(|c| c.is_ascii_digit()) {
        "some_digits"
    } else {
        "no_digits"
    };
    attrs.push((format!("digits:{digits}"), 1.0));

    // word
    if abbrev_is_digit {
        attrs.push(("word".into(), 0.0));
    } else {
        attrs.push((format!("word:{token_abbrev}"), 1.0));
    }

    // trailing.zeros
    if abbrev_is_digit {
        let zeros: String = token_abbrev
            .chars()
            .rev()
            .take_while(|c| *c == '0')
            .collect();
        attrs.push((format!("trailing.zeros:{zeros}"), 1.0));
    } else {
        attrs.push(("trailing.zeros".into(), 0.0));
    }

    // length (codepoint count, like Python len)
    let prefix = if abbrev_is_digit { "d" } else { "w" };
    attrs.push((format!("length:{prefix}:{}", token_abbrev.chars().count()), 1.0));

    // endsinpunc: value is the LAST char of the original token
    if ends_in_punc(token) {
        let last = token.chars().last().unwrap();
        attrs.push((format!("endsinpunc:{last}"), 1.0));
    } else {
        attrs.push(("endsinpunc".into(), 0.0));
    }

    // directional / street_name (binary-searchable sorted arrays from gen_vocab)
    attrs.push((
        "directional".into(),
        DIRECTIONS.binary_search(&token_abbrev.as_str()).is_ok() as u8 as f64,
    ));
    attrs.push((
        "street_name".into(),
        STREET_NAMES.binary_search(&token_abbrev.as_str()).is_ok() as u8 as f64,
    ));

    // has.vowels: vowels among abbrev chars after the first
    let has_vowels = token_abbrev
        .chars()
        .skip(1)
        .any(|c| matches!(c, 'a' | 'e' | 'i' | 'o' | 'u'));
    attrs.push(("has.vowels".into(), has_vowels as u8 as f64));

    attrs
}

/// Full per-token attribute sequences including previous/next context and
/// address.start / address.end flags, mirroring usaddress.tokens2features.
pub fn tokens_to_attrs(tokens: &[String]) -> Vec<Vec<Attr>> {
    let n = tokens.len();
    if n == 0 {
        return Vec::new();
    }
    let base: Vec<Vec<Attr>> = tokens.iter().map(|t| token_attrs(t)).collect();

    let mut out: Vec<Vec<Attr>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut attrs = base[i].clone();
        if i == 0 {
            attrs.push(("address.start".into(), 1.0));
        }
        if i == n - 1 {
            attrs.push(("address.end".into(), 1.0));
        }
        if i > 0 {
            for (name, w) in &base[i - 1] {
                attrs.push((format!("previous:{name}"), *w));
            }
            if i - 1 == 0 && n > 1 {
                attrs.push(("previous:address.start".into(), 1.0));
            }
        }
        if i < n - 1 {
            for (name, w) in &base[i + 1] {
                attrs.push((format!("next:{name}"), *w));
            }
            if i + 1 == n - 1 && n > 1 {
                attrs.push(("next:address.end".into(), 1.0));
            }
        }
        out.push(attrs);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn attr_map(attrs: &[Attr]) -> std::collections::BTreeMap<String, f64> {
        attrs.iter().cloned().collect()
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
