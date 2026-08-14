use std::io;

use crate::attribute::Attribute;
use crate::context::{Context, Flag, MarginalState, Reset, TagMarginals, ViterbiState};
use crate::model::Model;

/// The tagger provides the functionality for predicting label sequences for input sequences using a model
#[derive(Debug, Clone)]
pub struct Tagger<'a> {
    /// CRF model
    model: &'a Model<'a>,
    /// CRF context
    context: Context,
    /// Number of distinct output labels
    num_labels: u32,
    /// Vendored addition: reusable Viterbi scratch for the id-based fast path
    scratch: ViterbiState,
    /// Vendored addition: reusable forward-backward scratch. Stays empty (no
    /// heap allocation) unless `tag_ids_with_marginals` is called.
    marginals: MarginalState,
}

impl<'a> Tagger<'a> {
    pub(crate) fn new(model: &'a Model<'a>) -> io::Result<Self> {
        let num_labels = model.num_labels();
        let mut context = Context::new(Flag::VITERBI | Flag::MARGINALS, num_labels, 0);
        context.reset(Reset::TRANS);
        let mut tagger = Self {
            model,
            context,
            num_labels,
            scratch: ViterbiState::default(),
            marginals: MarginalState::default(),
        };
        tagger.transition_score()?;
        tagger.context.exp_transition();
        Ok(tagger)
    }

    /// Predict the label sequence for the item sequence.
    pub fn tag<T: AsRef<[Attribute]>>(&self, xseq: &[T]) -> io::Result<Vec<&str>> {
        if xseq.is_empty() {
            return Ok(Vec::new());
        }

        // Resolve attribute names to ids (unknown attributes are dropped, as before).
        let seq: Vec<Vec<(u32, f64)>> = xseq
            .iter()
            .map(|item| {
                item.as_ref()
                    .iter()
                    .filter_map(|x| self.model.to_attr_id(&x.name).map(|id| (id, x.value)))
                    .collect()
            })
            .collect();

        let mut vstate = ViterbiState::new(self.num_labels, seq.len() as u32);
        self.state_score_ids(&seq, &mut vstate);
        let (label_ids, _score) = self.context.viterbi(&mut vstate);

        Ok(label_ids
            .into_iter()
            .map(|id| self.model.label_name(id))
            .collect())
    }

    /// Vendored addition: id-based fast path with reusable scratch. Attribute
    /// ids must come from `Model::to_attr_id` (or equal caching). Returns label
    /// ids resolvable via `Model::label_name`.
    pub fn tag_ids(&mut self, seq: &[Vec<(u32, f64)>]) -> Vec<u32> {
        if seq.is_empty() {
            return Vec::new();
        }
        let mut scratch = std::mem::take(&mut self.scratch);
        scratch.reset(self.num_labels, seq.len() as u32);
        self.state_score_ids(seq, &mut scratch);
        let (label_ids, _score) = self.context.viterbi(&mut scratch);
        self.scratch = scratch;
        label_ids
    }

    /// Vendored addition: opt-in confidence path. Runs the same state scoring
    /// and Viterbi decode as [`Tagger::tag_ids`], then a forward-backward pass
    /// over the identical score matrices to produce per-position marginal
    /// probabilities and log Z.
    ///
    /// This is a separate entry point precisely so that `tag_ids` callers pay
    /// nothing: the forward-backward buffers are only sized on first use here.
    pub fn tag_ids_with_marginals(&mut self, seq: &[Vec<(u32, f64)>]) -> TagMarginals {
        if seq.is_empty() {
            return TagMarginals {
                num_labels: self.num_labels,
                ..Default::default()
            };
        }
        let mut scratch = std::mem::take(&mut self.scratch);
        scratch.reset(self.num_labels, seq.len() as u32);
        self.state_score_ids(seq, &mut scratch);
        let (labels, _score) = self.context.viterbi(&mut scratch);

        let mut marginals = std::mem::take(&mut self.marginals);
        self.context.forward_backward(&scratch, &mut marginals);
        // Score the Viterbi path explicitly rather than reusing Viterbi's
        // running maximum, so the value matches CRFsuite's `crf1dc_score`
        // accumulation order (and therefore pycrfsuite's `probability()`).
        let sequence_score = self.context.score(&scratch, &labels);
        let out = TagMarginals {
            labels,
            num_labels: self.num_labels,
            probs: marginals.to_probabilities(),
            log_norm: marginals.log_norm(),
            sequence_score,
        };
        self.scratch = scratch;
        self.marginals = marginals;
        out
    }

    fn transition_score(&mut self) -> io::Result<()> {
        // Compute transition scores between two labels
        let l = self.num_labels as usize;
        for i in 0..l {
            let trans = &mut self.context.trans[l * i..];
            let edge = self.model.label_ref(i as u32)?;
            for r in 0..edge.num_features {
                // Transition feature from #i to #(feature.target)
                let fid = edge.get(r as usize)?;
                let feature = self.model.feature(fid)?;
                let j = feature.target as usize;
                trans[j] = feature.weight;
                // Also update transposed matrix for cache-friendly Viterbi
                self.context.trans_t[l * j + i] = feature.weight;
            }
        }
        Ok(())
    }

    /// Compute state scores from pre-decoded model tables. Attribute and
    /// feature iteration order matches the original buffer-parsing path, so
    /// f64 accumulation order — and therefore output — is identical.
    fn state_score_ids(&self, seq: &[Vec<(u32, f64)>], vstate: &mut ViterbiState) {
        let l = self.num_labels as usize;
        for (t, item) in seq.iter().enumerate() {
            let state_slice = &mut vstate.state[l * t..];
            for &(aid, value) in item {
                for &(target, weight) in self.model.attr_features(aid) {
                    state_slice[target as usize] += weight * value;
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    /// The forward-backward marginals must equal what you get by enumerating
    /// every possible label sequence and summing their normalized weights.
    /// The bundled 2-label toy model makes that tractable (2^T paths), which
    /// makes this an independent check of the algorithm rather than a
    /// self-consistency check.
    #[test]
    fn marginals_match_brute_force_enumeration() {
        let buf = fs::read("tests/model.crfsuite").unwrap();
        let model = Model::new(&buf).unwrap();
        let mut tagger = model.tagger().unwrap();

        let raw: [&[(&str, f64)]; 6] = [
            &[("walk", 1.0), ("shop", 0.5)],
            &[("walk", 1.0)],
            &[("clean", 0.5), ("shop", 0.25)],
            &[("clean", 1.0)],
            &[("walk", 0.5), ("clean", 1.0)],
            &[("shop", 1.0)],
        ];
        let seq: Vec<Vec<(u32, f64)>> = raw
            .iter()
            .map(|item| {
                item.iter()
                    .map(|(n, v)| (model.to_attr_id(n).unwrap(), *v))
                    .collect()
            })
            .collect();

        let out = tagger.tag_ids_with_marginals(&seq);

        let l = model.num_labels() as usize;
        let t_n = seq.len();
        assert_eq!(l, 2);

        // Re-derive the state scores and enumerate all l^T labellings.
        let mut vstate = ViterbiState::new(l as u32, t_n as u32);
        tagger.state_score_ids(&seq, &mut vstate);

        let mut totals = vec![0.0f64; t_n * l];
        let mut z = 0.0f64;
        let mut labels = vec![0u32; t_n];
        for code in 0..l.pow(t_n as u32) {
            let mut c = code;
            for slot in labels.iter_mut() {
                *slot = (c % l) as u32;
                c /= l;
            }
            let w = tagger.context.score(&vstate, &labels).exp();
            z += w;
            for (t, &lab) in labels.iter().enumerate() {
                totals[l * t + lab as usize] += w;
            }
        }

        for t in 0..t_n {
            for i in 0..l {
                let expected = totals[l * t + i] / z;
                let got = out.probs[l * t + i];
                assert!(
                    (expected - got).abs() < 1e-12,
                    "marginal[{t}][{i}]: brute force {expected}, forward-backward {got}"
                );
            }
            let sum: f64 = out.marginals_at(t).iter().sum();
            assert!((sum - 1.0).abs() < 1e-12, "position {t} marginals sum to {sum}");
        }

        assert!(
            (out.log_norm - z.ln()).abs() < 1e-9,
            "log Z: brute force {}, forward-backward {}",
            z.ln(),
            out.log_norm
        );

        // The Viterbi path's probability must equal its enumerated share.
        let best = tagger.context.score(&vstate, &out.labels).exp() / z;
        assert!(
            (out.sequence_probability() - best).abs() < 1e-12,
            "sequence probability: brute force {best}, computed {}",
            out.sequence_probability()
        );

        // The Viterbi path is by construction the single highest-weight path.
        let mut labels = vec![0u32; t_n];
        let mut best_score = f64::NEG_INFINITY;
        for code in 0..l.pow(t_n as u32) {
            let mut c = code;
            for slot in labels.iter_mut() {
                *slot = (c % l) as u32;
                c /= l;
            }
            best_score = best_score.max(tagger.context.score(&vstate, &labels));
        }
        assert!((out.sequence_score - best_score).abs() < 1e-12);
    }

    /// `tag_ids` and `tag_ids_with_marginals` must decode identically.
    #[test]
    fn marginal_path_decodes_the_same_labels() {
        let buf = fs::read("tests/model.crfsuite").unwrap();
        let model = Model::new(&buf).unwrap();
        let mut tagger = model.tagger().unwrap();
        let seq: Vec<Vec<(u32, f64)>> = ["walk", "shop", "clean", "walk"]
            .iter()
            .map(|n| vec![(model.to_attr_id(n).unwrap(), 1.0)])
            .collect();
        assert_eq!(tagger.tag_ids(&seq), tagger.tag_ids_with_marginals(&seq).labels);
        assert!(tagger.tag_ids_with_marginals(&[]).labels.is_empty());
    }

    /// Scratch buffers are reused across calls; a short sequence after a long
    /// one must not read stale values.
    #[test]
    fn scratch_reuse_is_clean() {
        let buf = fs::read("tests/model.crfsuite").unwrap();
        let model = Model::new(&buf).unwrap();
        let mut tagger = model.tagger().unwrap();
        let long: Vec<Vec<(u32, f64)>> = (0..8)
            .map(|i| vec![(model.to_attr_id(["walk", "shop", "clean"][i % 3]).unwrap(), 1.0)])
            .collect();
        let short = &long[..2];
        let a = tagger.tag_ids_with_marginals(short);
        let _ = tagger.tag_ids_with_marginals(&long);
        let b = tagger.tag_ids_with_marginals(short);
        assert_eq!(a.probs, b.probs);
        assert_eq!(a.log_norm, b.log_norm);
        // MarginalState::marginal must agree with the flattened matrix.
        let mut m = crate::context::MarginalState::default();
        let mut vstate = ViterbiState::new(model.num_labels(), short.len() as u32);
        tagger.state_score_ids(short, &mut vstate);
        tagger.context.forward_backward(&vstate, &mut m);
        for t in 0..short.len() {
            for i in 0..model.num_labels() {
                assert!((m.marginal(t, i) - a.marginal(t, i)).abs() < 1e-15);
            }
        }
    }
}
