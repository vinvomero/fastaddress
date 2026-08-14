use bitflags::bitflags;

bitflags! {
    /// Functionality flags for contexts
    #[derive(Default, Debug, Clone, Copy)]
    pub struct Flag: u32 {
        const BASE = 0x01;
        const VITERBI = 0x01;
        const MARGINALS = 0x02;
        const ALL = 0xFF;
    }
}

/// Working buffers for Viterbi algorithm
///
/// This struct holds per-sequence working buffers used during Viterbi decoding.
/// It is separate from Context to allow reuse across multiple tagging operations
/// without repeatedly reallocating memory, and to keep Context immutable during
/// the viterbi pass.
#[derive(Debug, Clone, Default)]
pub struct ViterbiState {
    /// The number of distinct labels
    pub(crate) num_labels: u32,
    /// The number of items in the sequence
    pub(crate) num_items: u32,
    /// State scores
    ///
    /// This is a `[T][L]` matrix whose element `[t][l]` presents the total score
    /// of state features associating label #l at #t.
    pub(crate) state: Vec<f64>,
    /// Alpha score matrix
    ///
    /// This is a `[T][L]` matrix whose element `[t][l]` presents the total
    /// score of paths starting at BOS and arriving at (t, l).
    alpha_score: Vec<f64>,
    /// Backward edges
    ///
    /// This is a `[T][L]` matrix whose element `[t][j]` represents the label #i
    /// that yields the maximum score to arrive at (t, j).
    backward_edge: Vec<u32>,
}

impl ViterbiState {
    /// Create a new ViterbiState with the given number of labels and items
    pub fn new(num_labels: u32, num_items: u32) -> Self {
        let l = num_labels as usize;
        let t = num_items as usize;
        Self {
            num_labels,
            num_items,
            state: vec![0.0; t * l],
            alpha_score: vec![0.0; t * l],
            backward_edge: vec![0; t * l],
        }
    }

    /// Reuse this state for a new sequence length: resize buffers as needed and
    /// zero the portion the pass will read/write. (Vendored addition.)
    pub fn reset(&mut self, num_labels: u32, num_items: u32) {
        let l = num_labels as usize;
        let t = num_items as usize;
        let n = t * l;
        self.num_labels = num_labels;
        self.num_items = num_items;
        self.state.clear();
        self.state.resize(n, 0.0);
        self.alpha_score.clear();
        self.alpha_score.resize(n, 0.0);
        self.backward_edge.clear();
        self.backward_edge.resize(n, 0);
    }
}

/// Working buffers for the forward-backward (marginal probability) pass.
///
/// Vendored addition. Kept in its own struct — parallel to [`ViterbiState`] —
/// so that the Viterbi-only path never allocates or touches any of it. A
/// default-constructed `MarginalState` owns no heap memory; the first
/// [`Context::forward_backward`] call sizes it.
///
/// The algorithm mirrors CRFsuite's `crf1d_context.c`
/// (`crf1dc_exp_state` / `crf1dc_alpha_score` / `crf1dc_beta_score` /
/// `crf1dc_marginal_point`): scaled forward-backward rather than log-space
/// log-sum-exp, with one scaling coefficient per position.
///
/// One deliberate deviation from CRFsuite: before exponentiating, the state
/// scores at each position have that position's maximum subtracted. Marginals
/// are exactly invariant under a per-position constant shift of the state
/// scores (every path passes through exactly one node per position, so the
/// shift multiplies every path weight by the same constant), and the shift
/// keeps `exp()` away from overflow. The shift is added back into `log_norm`
/// so the normalization constant — and therefore sequence probability —
/// still refers to the unshifted scores.
#[derive(Debug, Clone, Default)]
pub struct MarginalState {
    num_labels: u32,
    num_items: u32,
    /// Exponentiated (shifted) state scores, a `[T][L]` matrix.
    exp_state: Vec<f64>,
    /// Scaled forward scores, a `[T][L]` matrix.
    alpha: Vec<f64>,
    /// Scaled backward scores, a `[T][L]` matrix.
    beta: Vec<f64>,
    /// Per-position scaling coefficients, a `[T]` vector.
    scale: Vec<f64>,
    /// Per-position state-score maxima that were shifted out, a `[T]` vector.
    shift: Vec<f64>,
    /// Work row, an `[L]` vector.
    row: Vec<f64>,
    /// log of the normalization constant Z for the (unshifted) scores.
    log_norm: f64,
}

impl MarginalState {
    fn resize(&mut self, num_labels: u32, num_items: u32) {
        let l = num_labels as usize;
        let t = num_items as usize;
        let n = t * l;
        self.num_labels = num_labels;
        self.num_items = num_items;
        self.log_norm = 0.0;
        self.exp_state.clear();
        self.exp_state.resize(n, 0.0);
        self.alpha.clear();
        self.alpha.resize(n, 0.0);
        self.beta.clear();
        self.beta.resize(n, 0.0);
        self.scale.clear();
        self.scale.resize(t, 1.0);
        self.shift.clear();
        self.shift.resize(t, 0.0);
        self.row.clear();
        self.row.resize(l, 0.0);
    }

    /// log Z for the sequence most recently passed through forward-backward.
    #[inline]
    pub fn log_norm(&self) -> f64 {
        self.log_norm
    }

    /// Marginal probability of label `l` at position `t`.
    ///
    /// `p(t,i) = alpha'[t][i] * beta'[t][i] / C_t`, the scaled-arithmetic form
    /// of `alpha[t][i] * beta[t][i] / Z` (CRFsuite `crf1dc_marginal_point`).
    #[inline]
    pub fn marginal(&self, t: usize, l: u32) -> f64 {
        let idx = self.num_labels as usize * t + l as usize;
        self.alpha[idx] * self.beta[idx] / self.scale[t]
    }

    /// Flatten every position's marginals into a fresh `[T][L]` vector.
    pub fn to_probabilities(&self) -> Vec<f64> {
        let l = self.num_labels as usize;
        let t_n = self.num_items as usize;
        let mut out = Vec::with_capacity(t_n * l);
        for t in 0..t_n {
            let inv = 1.0 / self.scale[t];
            for i in 0..l {
                let idx = l * t + i;
                out.push(self.alpha[idx] * self.beta[idx] * inv);
            }
        }
        out
    }
}

/// A tagged sequence together with its per-position marginal probabilities.
#[derive(Debug, Clone, Default)]
pub struct TagMarginals {
    /// Viterbi (joint-maximum) label ids, one per position.
    pub labels: Vec<u32>,
    /// Number of distinct labels — the row stride of `probs`.
    pub num_labels: u32,
    /// Marginal probabilities, a flat `[T][L]` matrix.
    pub probs: Vec<f64>,
    /// log of the normalization constant Z.
    pub log_norm: f64,
    /// Unnormalized log score of `labels` (CRFsuite `crf1dc_score`).
    pub sequence_score: f64,
}

impl TagMarginals {
    /// Marginal probability of `label` at position `t`.
    #[inline]
    pub fn marginal(&self, t: usize, label: u32) -> f64 {
        self.probs[self.num_labels as usize * t + label as usize]
    }

    /// All label marginals at position `t`.
    #[inline]
    pub fn marginals_at(&self, t: usize) -> &[f64] {
        let l = self.num_labels as usize;
        &self.probs[l * t..l * (t + 1)]
    }

    /// Probability of the whole label sequence, `exp(score - log Z)` — the
    /// equivalent of pycrfsuite's `Tagger.probability()`.
    #[inline]
    pub fn sequence_probability(&self) -> f64 {
        if self.labels.is_empty() {
            return 1.0;
        }
        (self.sequence_score - self.log_norm).exp()
    }
}

bitflags! {
    /// Reset flags
    pub struct Reset: u32 {
        /// Reset transition scores
        const TRANS = 0x01;
        /// Reset all
        const ALL = 0xFF;
    }
}

/// Context maintains internal data for an instance
#[derive(Debug, Clone, Default)]
pub struct Context {
    /// Flag specifying the functionality
    flag: Flag,
    /// The total number of distinct labels
    pub num_labels: u32,
    /// The number of items in the instance
    pub num_items: u32,
    /// The maximum number of labels
    cap_items: u32,
    /// Logarithm of the normalization factor for the instance.
    ///
    /// This is equivalent to the total scores of all paths in the lattice.
    log_norm: f64,
    /// Transition scores
    ///
    /// This is a `[L][L]` matrix whose element `[i][j]` represents the total
    /// score of transition features associating labels #i and #j.
    pub trans: Vec<f64>,
    /// Transposed transition scores for cache-friendly Viterbi
    ///
    /// This is a `[L][L]` matrix whose element `[j][i]` = trans[i][j].
    /// Stored for optimized column-wise access during Viterbi.
    pub(crate) trans_t: Vec<f64>,
    /// Beta score matrix
    ///
    /// This is a `[T][L]` matrix whose element `[t][l]` presents the total
    /// score of paths starting at (t, l) and arriving at EOS.
    beta_score: Vec<f64>,
    /// Scale factor vector
    ///
    /// This is a `[T]` vector whose element `[t]` presents the scaling
    /// coefficient for the alpha_score and beta_score.
    scale_factor: Vec<f64>,
    /// Row vector (work space)
    ///
    /// This is a `[T]` vector used internally for a work space.
    row: Vec<f64>,
    /// Exponents of state scores
    ///
    /// This is a `[T][L]` matrix whose element `[t][l]` presents the exponent
    /// of the total score of state features associating label #l at #t.
    /// This member is available only with `CTXF_MARGINALS` flag.
    exp_state: Vec<f64>,
    /// Exponents of transition scores.
    ///
    /// This is a `[L][L]` matrix whose element `[i][j]` represents the exponent
    /// of the total score of transition features associating labels #i and #j.
    /// This member is available only with `CTXF_MARGINALS` flag.
    exp_trans: Vec<f64>,
    /// Model expectations of states.
    ///
    /// This is a `[T][L]` matrix whose element `[t][l]` presents the model
    /// expectation (marginal probability) of the state (t,l)
    /// This member is available only with CTXF_MARGINALS flag.
    mexp_state: Vec<f64>,
    /// Model expectations of transitions.
    ///
    /// This is a `[L][L]` matrix whose element `[i][j]` presents the model
    /// expectation of the transition (i--j).
    /// This member is available only with `CTXF_MARGINALS` flag.
    mexp_trans: Vec<f64>,
}

impl Context {
    pub fn new(flag: Flag, l: u32, t: u32) -> Self {
        let l = l as usize;
        let trans = vec![0.0; l * l];
        let (exp_trans, mexp_trans) = if flag.contains(Flag::MARGINALS) {
            (vec![0.0; l * l + 4], vec![0.0; l * l])
        } else {
            (Vec::new(), Vec::new())
        };
        let trans_t = vec![0.0; l * l];
        let mut ctx = Self {
            flag,
            trans,
            trans_t,
            exp_trans,
            mexp_trans,
            num_items: 0,
            num_labels: l as u32,
            ..Default::default()
        };
        ctx.set_num_items(t);
        // t gives the 'hint' for maximum length of items.
        ctx.num_items = 0;
        ctx
    }

    pub fn set_num_items(&mut self, t: u32) {
        self.num_items = t;
        if self.cap_items < t {
            let l = self.num_labels as usize;
            let t = t as usize;
            self.beta_score = vec![0.0; t * l];
            self.scale_factor = vec![0.0; t];
            self.row = vec![0.0; l];
            if self.flag.contains(Flag::MARGINALS) {
                self.exp_state = vec![0.0; t * l + 4];
                self.mexp_state = vec![0.0; t * l];
            }
            self.cap_items = t as u32;
        }
    }

    pub fn reset(&mut self, flag: Reset) {
        let t = self.num_items as usize;
        let l = self.num_labels as usize;
        if flag.contains(Reset::TRANS) {
            self.trans[..l * l].fill(0.0);
        }
        if self.flag.contains(Flag::MARGINALS) {
            self.mexp_state[..t * l].fill(0.0);
            self.mexp_trans[..l * l].fill(0.0);
            self.log_norm = 0.0;
        }
    }

    pub fn exp_transition(&mut self) {
        let l = self.num_labels as usize;
        self.exp_trans[..l * l].copy_from_slice(&self.trans);
        for i in 0..(l * l) {
            self.exp_trans[i] = self.exp_trans[i].exp();
        }
    }

    /// Specialized Viterbi for small fixed L (fully unrolled)
    #[inline]
    fn viterbi_specialized<const L: usize>(
        &self,
        num_items: usize,
        vstate: &mut ViterbiState,
    ) -> (Vec<u32>, f64) {
        // Compute the scores at (0, *)
        vstate.alpha_score[..L].copy_from_slice(&vstate.state[..L]);

        // Compute the scores at (t, *)
        for t in 1..num_items {
            let state_t = &vstate.state[L * t..];
            let (prev, current) = vstate.alpha_score.split_at_mut(L * t);
            let prev = &prev[L * (t - 1)..];
            let back = &mut vstate.backward_edge[L * t..];

            // Compute the score of (t, j) - fully unrolled for const L
            for j in 0..L {
                let mut max_score = f64::MIN;
                let mut argmax_score = 0;
                let trans_col = &self.trans_t[L * j..];

                // This loop will be fully unrolled by the compiler
                for i in 0..L {
                    let score = prev[i] + trans_col[i];
                    if max_score < score {
                        max_score = score;
                        argmax_score = i;
                    }
                }

                back[j] = argmax_score as u32;
                current[j] = max_score + state_t[j];
            }
        }

        // Find the maximum score at the end
        let mut max_score = f64::MIN;
        let prev = &vstate.alpha_score[L * (num_items - 1)..];
        let mut labels = vec![0u32; num_items];

        for (i, prev_value) in prev.iter().enumerate().take(L) {
            if max_score < *prev_value {
                max_score = *prev_value;
                labels[num_items - 1] = i as u32;
            }
        }

        // Tag labels by tracing the backward links
        for t in (0..(num_items - 1)).rev() {
            let back = &vstate.backward_edge[L * (t + 1)..];
            labels[t] = back[labels[t + 1] as usize];
        }

        (labels, max_score)
    }

    /// Optimized Viterbi for medium L values (6-16)
    /// Uses manual loop unrolling to help compiler auto-vectorize
    #[inline]
    fn viterbi_unrolled<const L: usize>(
        &self,
        num_items: usize,
        vstate: &mut ViterbiState,
    ) -> (Vec<u32>, f64) {
        // Compute the scores at (0, *)
        vstate.alpha_score[..L].copy_from_slice(&vstate.state[..L]);

        // Compute the scores at (t, *)
        for t in 1..num_items {
            let state_t = &vstate.state[L * t..];
            let (prev, current) = vstate.alpha_score.split_at_mut(L * t);
            let prev = &prev[L * (t - 1)..];
            let back = &mut vstate.backward_edge[L * t..];

            // Compute the score of (t, j)
            for j in 0..L {
                let mut max_score = f64::MIN;
                let mut argmax_score = 0;
                let trans_col = &self.trans_t[L * j..];

                // Manually unroll in chunks of 4 to help auto-vectorization
                let chunks = L / 4;
                let _remainder = L % 4;

                for chunk in 0..chunks {
                    let i = chunk * 4;
                    // Process 4 elements at once (compiler can vectorize this)
                    let s0 = prev[i] + trans_col[i];
                    let s1 = prev[i + 1] + trans_col[i + 1];
                    let s2 = prev[i + 2] + trans_col[i + 2];
                    let s3 = prev[i + 3] + trans_col[i + 3];

                    if max_score < s0 {
                        max_score = s0;
                        argmax_score = i;
                    }
                    if max_score < s1 {
                        max_score = s1;
                        argmax_score = i + 1;
                    }
                    if max_score < s2 {
                        max_score = s2;
                        argmax_score = i + 2;
                    }
                    if max_score < s3 {
                        max_score = s3;
                        argmax_score = i + 3;
                    }
                }

                // Handle remainder
                for i in (chunks * 4)..L {
                    let score = prev[i] + trans_col[i];
                    if max_score < score {
                        max_score = score;
                        argmax_score = i;
                    }
                }

                back[j] = argmax_score as u32;
                current[j] = max_score + state_t[j];
            }
        }

        // Find the maximum score at the end
        let mut max_score = f64::MIN;
        let prev = &vstate.alpha_score[L * (num_items - 1)..];
        let mut labels = vec![0u32; num_items];

        for (i, prev_value) in prev.iter().enumerate().take(L) {
            if max_score < *prev_value {
                max_score = *prev_value;
                labels[num_items - 1] = i as u32;
            }
        }

        // Tag labels by tracing the backward links
        for t in (0..(num_items - 1)).rev() {
            let back = &vstate.backward_edge[L * (t + 1)..];
            labels[t] = back[labels[t + 1] as usize];
        }

        (labels, max_score)
    }

    /// Run Viterbi decoding using state scores from ViterbiState
    ///
    /// State scores should be computed into `vstate.state` before calling this.
    ///
    /// # Panics
    /// Panics if `vstate.num_labels` does not match `self.num_labels`.
    pub fn viterbi(&self, vstate: &mut ViterbiState) -> (Vec<u32>, f64) {
        assert_eq!(
            self.num_labels, vstate.num_labels,
            "ViterbiState num_labels ({}) must match Context num_labels ({})",
            vstate.num_labels, self.num_labels
        );

        let l = self.num_labels as usize;
        let num_items = vstate.num_items as usize;

        // Use specialized versions for common small L values
        // These are fully unrolled by the compiler for maximum performance
        match l {
            2 => return self.viterbi_specialized::<2>(num_items, vstate),
            3 => return self.viterbi_specialized::<3>(num_items, vstate),
            4 => return self.viterbi_specialized::<4>(num_items, vstate),
            5 => return self.viterbi_specialized::<5>(num_items, vstate),
            6 => return self.viterbi_unrolled::<6>(num_items, vstate),
            7 => return self.viterbi_unrolled::<7>(num_items, vstate),
            8 => return self.viterbi_unrolled::<8>(num_items, vstate),
            9 => return self.viterbi_unrolled::<9>(num_items, vstate),
            10 => return self.viterbi_unrolled::<10>(num_items, vstate),
            12 => return self.viterbi_unrolled::<12>(num_items, vstate),
            16 => return self.viterbi_unrolled::<16>(num_items, vstate),
            // Vendored addition: the usaddress model has 26 labels, which
            // previously fell through to the generic scalar loop.
            26 => return self.viterbi_unrolled::<26>(num_items, vstate),
            _ => {} // Fall through to generic version
        }

        // Compute the scores at (0, *)
        vstate.alpha_score[..l].copy_from_slice(&vstate.state[..l]);

        // Compute the scores at (t, *)
        for t in 1..num_items {
            let state_t = &vstate.state[l * t..];
            let (prev, current) = vstate.alpha_score.split_at_mut(l * t);
            let prev = &prev[l * (t - 1)..];
            let back = &mut vstate.backward_edge[l * t..];
            // Compute the score of (t, j)
            for j in 0..l {
                let mut max_score = f64::MIN;
                let mut argmax_score = None;
                // Use transposed matrix for cache-friendly sequential access
                let trans_col = &self.trans_t[l * j..];
                for i in 0..l {
                    // Transit from (t-1, i) to (t, j)
                    // trans_t[j][i] = trans[i][j]
                    let score = prev[i] + trans_col[i];
                    // Store this path if it has the maximum score
                    if max_score < score {
                        max_score = score;
                        argmax_score = Some(i);
                    }
                }
                // Backward link (#t, #j) -> (#t-1, #i)
                if let Some(argmax_score) = argmax_score {
                    back[j] = argmax_score as u32;
                }
                // Add the state score on (t, j)
                current[j] = max_score + state_t[j];
            }
        }
        // Find the node (#T, Ei) that reaches EOS with the maximum score
        let mut max_score = f64::MIN;
        let prev = &vstate.alpha_score[l * (num_items - 1)..];
        // Set a score for T-1 to be overwritten later. Just in case we don't
        // end up with something beating f64::MIN.
        let mut labels = vec![0u32; num_items];
        for (i, prev_value) in prev.iter().enumerate().take(l) {
            if max_score < *prev_value {
                max_score = *prev_value;
                // Tag the item #T
                labels[num_items - 1] = i as u32;
            }
        }
        // Tag labels by tracing the backward links
        for t in (0..(num_items - 1)).rev() {
            let back = &vstate.backward_edge[l * (t + 1)..];
            labels[t] = back[labels[t + 1] as usize];
        }
        (labels, max_score)
    }

    /// Unnormalized log score of a label sequence.
    ///
    /// Mirrors CRFsuite `crf1dc_score`: the state score of the first label plus,
    /// for every subsequent position, the transition score into it and its own
    /// state score. Reads the same `vstate.state` matrix Viterbi consumed.
    pub fn score(&self, vstate: &ViterbiState, labels: &[u32]) -> f64 {
        if labels.is_empty() {
            return 0.0;
        }
        let l = self.num_labels as usize;
        let mut i = labels[0] as usize;
        let mut ret = vstate.state[i];
        for (t, &label) in labels.iter().enumerate().skip(1) {
            let j = label as usize;
            ret += self.trans[l * i + j];
            ret += vstate.state[l * t + j];
            i = j;
        }
        ret
    }

    /// Scaled forward-backward over the state scores already computed into
    /// `vstate.state`, filling `m` with alpha/beta/scale so that
    /// [`MarginalState::marginal`] and [`MarginalState::log_norm`] are valid.
    ///
    /// Vendored addition. Mirrors CRFsuite's `crf1dc_alpha_score` /
    /// `crf1dc_beta_score`; see [`MarginalState`] for the one deviation
    /// (per-position max shift before `exp`).
    ///
    /// # Panics
    /// Panics if `vstate.num_labels` does not match `self.num_labels`.
    pub fn forward_backward(&self, vstate: &ViterbiState, m: &mut MarginalState) {
        assert_eq!(
            self.num_labels, vstate.num_labels,
            "ViterbiState num_labels ({}) must match Context num_labels ({})",
            vstate.num_labels, self.num_labels
        );
        let l = self.num_labels as usize;
        let t_n = vstate.num_items as usize;
        m.resize(self.num_labels, vstate.num_items);
        if t_n == 0 {
            return;
        }

        // exp_state[t][i] = exp(state[t][i] - max_i state[t][i])
        for t in 0..t_n {
            let src = &vstate.state[l * t..l * (t + 1)];
            let max = src.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let max = if max.is_finite() { max } else { 0.0 };
            m.shift[t] = max;
            let dst = &mut m.exp_state[l * t..l * (t + 1)];
            for (d, s) in dst.iter_mut().zip(src) {
                *d = (*s - max).exp();
            }
        }

        // Forward: alpha[0][i] = exp_state[0][i]; then
        // alpha[t][j] = exp_state[t][j] * sum_i alpha[t-1][i] * exp_trans[i][j],
        // each row rescaled to sum to 1 and the coefficient kept in `scale`.
        m.alpha[..l].copy_from_slice(&m.exp_state[..l]);
        let sum: f64 = m.alpha[..l].iter().sum();
        m.scale[0] = if sum != 0.0 { 1.0 / sum } else { 1.0 };
        for a in &mut m.alpha[..l] {
            *a *= m.scale[0];
        }
        for t in 1..t_n {
            let (prev, cur) = m.alpha.split_at_mut(l * t);
            let prev = &prev[l * (t - 1)..];
            let cur = &mut cur[..l];
            cur.fill(0.0);
            for (i, &a) in prev.iter().enumerate() {
                let trans = &self.exp_trans[l * i..l * (i + 1)];
                for (c, &tr) in cur.iter_mut().zip(trans) {
                    *c += a * tr;
                }
            }
            let state = &m.exp_state[l * t..l * (t + 1)];
            for (c, &s) in cur.iter_mut().zip(state) {
                *c *= s;
            }
            let sum: f64 = cur.iter().sum();
            let scale = if sum != 0.0 { 1.0 / sum } else { 1.0 };
            m.scale[t] = scale;
            for c in cur.iter_mut() {
                *c *= scale;
            }
        }

        // log Z = -sum_t log(C_t), plus the per-position shifts taken out above.
        let mut log_norm = 0.0;
        for t in 0..t_n {
            log_norm += m.shift[t] - m.scale[t].ln();
        }
        m.log_norm = log_norm;

        // Backward: beta[T-1][i] = C_{T-1}; then
        // beta[t][i] = C_t * sum_j exp_trans[i][j] * exp_state[t+1][j] * beta[t+1][j].
        let last = l * (t_n - 1);
        m.beta[last..last + l].fill(m.scale[t_n - 1]);
        for t in (0..t_n - 1).rev() {
            for j in 0..l {
                m.row[j] = m.beta[l * (t + 1) + j] * m.exp_state[l * (t + 1) + j];
            }
            let scale = m.scale[t];
            for i in 0..l {
                let trans = &self.exp_trans[l * i..l * (i + 1)];
                let dot: f64 = trans.iter().zip(&m.row).map(|(a, b)| a * b).sum();
                m.beta[l * t + i] = dot * scale;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_context_new() {
        let _ctx = Context::new(Flag::VITERBI, 2, 0);
        let _ctx = Context::new(Flag::MARGINALS, 2, 0);
        let _ctx = Context::new(Flag::VITERBI | Flag::MARGINALS, 2, 0);
    }

    #[test]
    fn test_context_reset() {
        let mut ctx = Context::new(Flag::VITERBI | Flag::MARGINALS, 2, 0);
        ctx.reset(Reset::TRANS);
        ctx.reset(Reset::ALL);
    }
}
