use std::sync::LazyLock;

use regex::Regex;

// Port of usaddress.tokenize (v0.5.16). Same HTML-ampersand normalization and
// token regex; behavioral parity is enforced by the differential suite, not by
// regex-string similarity.
static AMP_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new("(&#38;)|(&amp;)").unwrap());
// Python's re treats No/Nl characters (½, ¼, Roman numerals) as word chars, so
// its \b fires before a standalone '½'; Rust's \w excludes No/Nl and the same
// token silently vanished (usaddress keeps it — '123 ½ Main St' is real assessor
// data). The extra alternations restore Python's boundary behavior for those
// categories without touching anything the parity suite already pins.
static TOKEN_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\(*(?:[\p{No}\p{Nl}]|\b)[^\s,;#&()]+[.,;)\n]*|\(*[\p{No}\p{Nl}][.,;)\n]*|[#&]")
        .unwrap()
});

pub fn tokenize(address: &str) -> Vec<String> {
    let normalized = AMP_RE.replace_all(address, "&");
    TOKEN_RE
        .find_iter(&normalized)
        .map(|m| m.as_str().to_string())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::tokenize;

    #[test]
    fn splits_basic_address() {
        assert_eq!(
            tokenize("123 N Main St"),
            vec!["123", "N", "Main", "St"]
        );
    }

    #[test]
    fn hash_and_amp_are_standalone_tokens() {
        assert_eq!(tokenize("# 1 A & B"), vec!["#", "1", "A", "&", "B"]);
    }

    #[test]
    fn trailing_punctuation_stays_attached() {
        assert_eq!(tokenize("ab. cd,ef"), vec!["ab.", "cd,", "ef"]);
    }

    #[test]
    fn standalone_half_fraction_is_kept() {
        // Python \w includes ½ (category No); usaddress keeps it as a token.
        assert_eq!(
            tokenize("123 \u{00BD} Main St"),
            vec!["123", "\u{00BD}", "Main", "St"]
        );
        assert_eq!(tokenize("123\u{00BD} Main"), vec!["123\u{00BD}", "Main"]);
        assert_eq!(tokenize("\u{00BD},"), vec!["\u{00BD},"]);
        assert_eq!(tokenize("\u{00BD}Main"), vec!["\u{00BD}Main"]);
    }

    #[test]
    fn html_entities_normalize_to_ampersand() {
        assert_eq!(tokenize("A &amp; B"), vec!["A", "&", "B"]);
        assert_eq!(tokenize("A &#38; B"), vec!["A", "&", "B"]);
    }

    #[test]
    fn empty_and_whitespace_yield_no_tokens() {
        assert!(tokenize("").is_empty());
        assert!(tokenize("   \t  ").is_empty());
    }
}
