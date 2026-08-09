//! Differential-suite dump binary: reads a benchmark CSV (raw_address column)
//! and emits JSONL with the Rust side's tokens, serialized CRF attributes, and
//! model labels for each row. Compared against benchmark/dump_oracle.py output
//! by benchmark/run_parity.py.

use std::env;
use std::io::{BufWriter, Write};

use crfs::Attribute;
use serde_json::json;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("usage: dump <csv-path>");
        std::process::exit(2);
    }
    let mut reader = csv::Reader::from_path(&args[1]).expect("csv must open");
    let headers = reader.headers().expect("csv headers").clone();
    let raw_idx = headers
        .iter()
        .position(|h| h == "raw_address")
        .expect("raw_address column");

    let stdout = std::io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    for record in reader.records() {
        let record = record.expect("csv record");
        let raw = record.get(raw_idx).unwrap_or("");
        let tokens = usaddr_core::tokenize::tokenize(raw);
        let attr_seq = usaddr_core::features::tokens_to_attrs(&tokens);

        // Sort per token for canonical comparison (matches oracle's sorted items).
        let attrs_sorted: Vec<Vec<(String, f64)>> = attr_seq
            .iter()
            .map(|attrs| {
                let mut v = attrs.clone();
                v.sort_by(|a, b| a.0.cmp(&b.0));
                v
            })
            .collect();

        let xseq: Vec<Vec<Attribute>> = attr_seq
            .iter()
            .map(|attrs| {
                attrs
                    .iter()
                    .map(|(name, w)| Attribute::new(name.clone(), *w))
                    .collect()
            })
            .collect();
        let labels = if xseq.is_empty() {
            Vec::new()
        } else {
            usaddr_core::model::tag_attrs(&xseq).expect("tagging must not error")
        };

        let line = json!({
            "raw": raw,
            "tokens": tokens,
            "attrs": attrs_sorted,
            "labels": labels,
        });
        writeln!(out, "{line}").expect("stdout write");
    }
}
