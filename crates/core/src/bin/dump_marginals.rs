//! Ground-truth cross-check dump: reads a benchmark CSV (raw_address column)
//! and emits JSONL with the Rust side's tokens, Viterbi labels, the full
//! per-position marginal matrix, log Z and the sequence probability.
//!
//! Compared against pycrfsuite's `Tagger.marginal()` / `Tagger.probability()`
//! over the same model by benchmark/compare_marginals.py.

use std::env;
use std::io::{BufWriter, Write};

use serde_json::json;
use usaddr_core::model::{label_name_for, tag_attr_ids_with_marginals_for, ModelId};

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: dump_marginals <csv-path> [limit]");
        std::process::exit(2);
    }
    let limit: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(usize::MAX);

    let mut reader = csv::Reader::from_path(&args[1]).expect("csv must open");
    let headers = reader.headers().expect("csv headers").clone();
    let raw_idx = headers
        .iter()
        .position(|h| h == "raw_address")
        .expect("raw_address column");

    let stdout = std::io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    for record in reader.records().take(limit) {
        let record = record.expect("csv record");
        let raw = record.get(raw_idx).unwrap_or("");
        let tokens = usaddr_core::tokenize::tokenize(raw);
        if tokens.is_empty() {
            continue;
        }
        let facts: Vec<_> = tokens.iter().map(|t| usaddr_core::features::token_facts(t)).collect();
        let seq = usaddr_core::attr_cache::facts_to_id_seq_for(ModelId::V1, &facts);
        let m = tag_attr_ids_with_marginals_for(ModelId::V1, &seq);

        let l = m.num_labels as usize;
        let label_names: Vec<&str> =
            (0..m.num_labels).map(|i| label_name_for(ModelId::V1, i)).collect();
        let labels: Vec<&str> = m.labels.iter().map(|&i| label_name_for(ModelId::V1, i)).collect();
        let marginals: Vec<Vec<f64>> =
            (0..tokens.len()).map(|t| m.probs[l * t..l * (t + 1)].to_vec()).collect();

        writeln!(
            out,
            "{}",
            json!({
                "raw": raw,
                "tokens": tokens,
                "labels": labels,
                "label_names": label_names,
                "marginals": marginals,
                "log_norm": m.log_norm,
                "sequence_probability": m.sequence_probability(),
            })
        )
        .expect("write");
    }
}
