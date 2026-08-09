use std::io;

use crate::attribute::Attribute;
use crate::context::{Context, Flag, Reset, ViterbiState};
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
