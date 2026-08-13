//! Accuracy-harness tagger: tags addresses with either the embedded model or a
//! model file loaded at runtime (`--model <path>`), emitting JSONL
//! {raw, tokens, labels} per input row. Used by benchmark/run_accuracy.py to
//! score candidate .crfsuite artifacts without rebuilding the crate.
//!
//! Eval throughput is irrelevant, so this uses the string-attribute path.

use std::env;
use std::io::{BufWriter, Write};

use crfs::{Attribute, Model};
use serde_json::json;

fn main() {
    let args: Vec<String> = env::args().collect();
    // usage: eval_tag <csv-path> [--model <path>]
    if args.len() != 2 && args.len() != 4 {
        eprintln!("usage: eval_tag <csv-path> [--model <path>]");
        std::process::exit(2);
    }
    let csv_path = &args[1];
    let runtime_model: Option<Model<'static>> = if args.len() == 4 {
        assert_eq!(args[2], "--model", "third arg must be --model");
        let bytes: &'static [u8] =
            Box::leak(std::fs::read(&args[3]).expect("model file must read").into_boxed_slice());
        Some(Model::new(bytes).expect("model file must parse"))
    } else {
        None
    };
    let runtime_tagger = runtime_model.as_ref().map(|m| m.tagger().expect("tagger"));

    let mut reader = csv::Reader::from_path(csv_path).expect("csv must open");
    let headers = reader.headers().expect("headers").clone();
    let raw_idx = headers.iter().position(|h| h == "raw_address").expect("raw_address column");

    let stdout = std::io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    for record in reader.records() {
        let record = record.expect("record");
        let raw = record.get(raw_idx).unwrap_or("");
        let tokens = usaddr_core::tokenize::tokenize(raw);
        let labels: Vec<String> = if tokens.is_empty() {
            Vec::new()
        } else {
            let attrs = usaddr_core::features::tokens_to_attrs(&tokens);
            match &runtime_tagger {
                Some(tagger) => {
                    let xseq: Vec<Vec<Attribute>> = attrs;
                    tagger
                        .tag(&xseq)
                        .expect("tagging must not error")
                        .into_iter()
                        .map(|s| s.to_string())
                        .collect()
                }
                None => usaddr_core::model::tag_attrs(&attrs).expect("tagging must not error"),
            }
        };
        let line = json!({"raw": raw, "tokens": tokens, "labels": labels});
        writeln!(out, "{line}").expect("stdout write");
    }
}
