use std::sync::LazyLock;

use regex::Regex;

// Port of usaddress.tokenize (v0.5.16). Same HTML-ampersand normalization and
// token regex; behavioral parity is enforced by the differential suite, not by
// regex-string similarity.
static AMP_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new("(&#38;)|(&amp;)").unwrap());
static TOKEN_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\(*\b[^\s,;#&()]+[.,;)\n]*|[#&]").unwrap());

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
