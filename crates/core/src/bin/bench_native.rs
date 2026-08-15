//! Native-side benchmark entrypoint: times compat-mode tag() over a benchmark
//! CSV, single-threaded or with N threads over row chunks. Emits one JSON line
//! consumed by benchmark/run_speed.py.

use std::env;
use std::time::Instant;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: bench_native <csv-path> [threads]");
        std::process::exit(2);
    }
    let threads: usize = args
        .get(2)
        .map(|s| s.parse().expect("threads must be a number"))
        .unwrap_or(1)
        .max(1);

    let mut reader = csv::Reader::from_path(&args[1]).expect("csv must open");
    let headers = reader.headers().expect("headers").clone();
    let raw_idx = headers.iter().position(|h| h == "raw_address").expect("raw_address column");
    let rows: Vec<String> = reader
        .records()
        .map(|r| r.expect("record").get(raw_idx).unwrap_or("").to_string())
        .collect();

    // Warm-up: force the lazy model parse before timing.
    let _ = fastaddress_core::api::tag("123 Main St Springfield IL 62704");

    // Optional stage decomposition: BENCH_STAGE=tokenize|features|confidence|full
    // (default full). `confidence` times the opt-in marginal path against the
    // same rows so its cost can be quoted next to the plain path.
    let stage = env::var("BENCH_STAGE").unwrap_or_else(|_| "full".to_string());
    // Optional model selection for the v2 evaluation (requires --features model-v2).
    #[cfg(feature = "model-v2")]
    let use_v2 = env::var("BENCH_MODEL").map(|v| v == "v2").unwrap_or(false);
    let start = Instant::now();
    let mut errors = 0usize;
    if stage == "tokenize" {
        for raw in &rows {
            errors += fastaddress_core::tokenize::tokenize(raw).is_empty() as usize;
        }
    } else if stage == "features" {
        for raw in &rows {
            let tokens = fastaddress_core::tokenize::tokenize(raw);
            errors += fastaddress_core::features::tokens_to_attrs(&tokens).is_empty() as usize;
        }
    } else if stage == "confidence" {
        for raw in &rows {
            if fastaddress_core::api::tag_with_confidence(raw, None).is_err() {
                errors += 1;
            }
        }
    } else if threads <= 1 {
        #[cfg(feature = "model-v2")]
        if use_v2 {
            for raw in &rows {
                if fastaddress_core::api::tag_model(fastaddress_core::model::ModelId::V2, raw, None).is_err() {
                    errors += 1;
                }
            }
            let secs = start.elapsed().as_secs_f64();
            println!(
                "{{\"rows\": {}, \"threads\": 1, \"model\": \"v2\", \"secs\": {:.4}, \"per_sec\": {:.1}, \"errors\": {}}}",
                rows.len(), secs, rows.len() as f64 / secs, errors
            );
            return;
        }
        for raw in &rows {
            if fastaddress_core::api::tag(raw).is_err() {
                errors += 1;
            }
        }
    } else {
        let chunk = rows.len().div_ceil(threads).max(1);
        errors = std::thread::scope(|scope| {
            let handles: Vec<_> = rows
                .chunks(chunk)
                .map(|part| {
                    scope.spawn(move || part.iter().filter(|raw| fastaddress_core::api::tag(raw).is_err()).count())
                })
                .collect();
            handles.into_iter().map(|h| h.join().unwrap()).sum()
        });
    }
    let secs = start.elapsed().as_secs_f64();

    println!(
        "{{\"rows\": {}, \"threads\": {}, \"secs\": {:.4}, \"per_sec\": {:.1}, \"errors\": {}}}",
        rows.len(),
        threads,
        secs,
        rows.len() as f64 / secs,
        errors
    );
}
