# leviathan2022fast (P1)

- **Problem:** Decoding K tokens from large autoregressive Transformers requires K serial runs, making inference significantly slower than smaller models.  
- **Method:** Speculative decoding—sample faster without output changes by computing multiple tokens in parallel using efficient approximation models and a novel sampling method.  
- **Reported results:** 2X–3X acceleration versus standard T5X implementation on T5-XXL with identical outputs.  
- **Limitations:** Inference from large models is often bottlenecked on memory bandwidth and communication, not arithmetic; additional compute may be available via increased concurrency.  
- **Exact quotes:**  
  - "hard language-modeling tasks often include easier subtasks that can be approximated well by more efficient models" (P1)  
  - "using speculative execution and a novel sampling method, we can make exact decoding from the large models faster, by running them in parallel on the outputs of the approximation models" (P1)

- **Problem:** Accelerate inference from large autoregressive Transformers without altering output distributions.

- **Method:** Speculative decoding using a smaller, more efficient approximation model (Mq) to generate γ guesses in parallel, evaluated by the target model (Mp); accepted guesses proceed, while the first rejection triggers a correction token from an adjusted distribution.

- **Reported results:** 
  - 38-token sentence generated with only 9 serial runs of the 97M parameter target model, enabled by a 6M parameter approximation model.
  - Wall-time comparisons for T5-XXL (11B parameters) show 2X–3X latency improvement over robust T5X implementation with identical outputs.

- **Limitations:** Requires an efficient approximation model; performance gains depend on how well Mq approximates Mp; theoretical guarantees require careful adjustment of the acceptance distribution for the first rejected token.

- **Quote 1:** "With only 9 serial runs of a larger target model (97M parameters) thanks to a smaller and more efficient approximation model (6M parameters)... the probability of generating it is unchanged." (p.2)

- **Quote 2:** "our method... may be a good default to accelerate sampling from autoregressive models like Transformers." (p.3)

- **Problem**: Accelerating autoregressive model decoding. Speculative execution generalized to the stochastic setting via a novel "speculative sampling" method and a decoding mechanism called "speculative decoding" that accelerates decoding without model changes.

- **Method**: Run a smaller draft model Mq to propose γ guesses autoregressively. In parallel, run the target model Mp to compute distributions for the prefix and augmented prefixes. Accept guesses based on a rejection sampling criterion using uniform random numbers compared to ratios of Mp and Mq probabilities. Adjust the Mp distribution if needed before returning one token from Mp and the accepted Mq tokens.

- **Reported results**: Expected tokens per iteration follow a capped geometric distribution with success probability 1−α and cap γ+1, where α = E[β] is the acceptance rate. Figure 2 illustrates expected tokens vs. α for γ ∈ {1,3,5,7}. Derivation assumes i.i.d. βs; E(tokens) = (1−αγ+1)/(1−α).

- **Limitation**: Assumes i.i.d. acceptance rates β; real-world token dependencies may violate this, affecting the geometric model accuracy.

- **Quote (p.2)**: "cast into standard sampling from an adjusted probability distribution. For example, argmax sampling is equivalent to zeroing out non-max elements of the distribution and normalizing."

- **Quote (p.3)**: "To sample x ∼ p(x), we instead sample x ∼ q(x), keeping it if q(x) ≤ p(x), and in case q(x) > p(x) we reject the sample with probability 1− p(x)q(x) and sample x again from an adjusted distribution p0 (x) = norm(max(0, p(x) − q(x)))."

**problem**
- Speculative decoding aims to accelerate transformer inference by generating multiple tokens in parallel using a lightweight approximation model $M_q$ alongside the target model $M_p$.

**method**
- The algorithm alternates between proposing $\gamma+1$ candidate tokens via $M_p$ and verifying them using $M_q$; accepted tokens proceed, while rejected computation is wasted.
- DLK divergence ($d_{LK}$) characterizes the distance between proposal and target distributions; Corollary 3.6 defines $\alpha = 1 - \mathbb{E}[d_{LK}(p, q)] = \mathbb{E}[\min(p, q)]$.
- Improvement is feasible when $\alpha > c$, where $c$ is the relative cost of $M_q$ to $M_p$.

**reported results**
- Walltime improvement factor: $\frac{(1-\alpha)(\gamma c + 1)}{1 - \alpha \gamma + 1}$ (Theorem 3.8).
- Operation increase factor: $\frac{(1-\alpha)(\gamma \hat{c} + \gamma + 1)}{1 - \alpha \gamma + 1}$ (Theorem 3.11), where $\hat{c}$ is the arithmetic operations ratio.
- Empirical $\alpha$ values observed in Table 3; $c$ typically $< 0.05$ in experiments.

**limitations**
- Assumes i.i.d. token generation and sufficient compute for $\gamma+1$ parallel $M_p$ evaluations without walltime penalty.
- Rejected guesses waste computation, increasing total arithmetic operations; "free" concurrency only applies when $M_q$ sample is accepted.
- Walltime improvement depends on low $\alpha$ and low $c$; high divergence between $p$ and $q$ degrades efficiency.

**quotes**
- "If α is low, the increase in the number of arithmetic operations is high, and vice-versa." (p. 4)
- "Let ĉ be the ratio of arithmetic operations per token of the approximation model Mq to that of the target model Mp." (p. 4)

# Leviathan 2022 (5/12) — Factual Notes

- **Problem**: Accelerate transformer inference via speculative decoding with an approximation model Mq to generate multiple candidate tokens per step, reducing expected cost per output token.

- **Method**: Algorithm 1 proposes γ tokens using Mq; if accepted, target model Mp processes the prefix. Expected token cost is (cγ+1)(1−α)/T, where c is the relative cost of Mq and α is the acceptance probability. Speedup over standard decoding (cost T/token) follows from this cost ratio.

- **Reported results**: 
  - Memory accesses for target weights/KV cache shrink by factor (1−α)/(1−α/(γ+1)) per Algorithm 1 execution.
  - For negligible-cost approximation models (c ≈ 0), expected walltime improvement is bounded by 1−α, approaching equality as γ grows.
  - With T5-XXL 11B as Mp and a trivial bigram Mq (α ≈ 0.2), γ = 3 yields 1.25× speedup.
  - Figures 3–4 illustrate optimal γ vs. α for various c and the speed/ops trade-off at c = ĉ = 0.

- **Limitations**: Theorem 3.8 requires long generations; improvement factor capped by generated token count. Assumes sufficient compute resources. β-values are not constant, limiting static γ optimization.

- **Two exact quotes**:
  - “Since the cost of producing a single token with the standard decoding algorithm is T, we get the desired result.” (Page 4 continued)
  - “in empirical tests (Section 4.2) we get non zero αs even for these trivial n-gram models. For example, for the English-German translation task, with Mp being T5-XXL 11B and Mq being a trivial bigram model, we get α ≈ 0.2 which leads to an inference speed improvement factor of 1.25X with γ = 3.” (Page 5)

- **Approximation models**: Negligible-cost models (c ≈ 0) yield improvement bounded by 1−α. Same-architecture smaller Transformers ~2 orders of magnitude smaller than Mp typically perform best, balancing α and c (Theorem 3.8).

- **Problem**: Accelerating inference from a T5-XXL 11B model via speculative decoding using an approximation model Mq to generate draft tokens before verifying with Mp.
- **Method**: Speculative decoding with variable draft factor γ; Mq (T5-small/base/large) drafts tokens, Mp verifies; α is acceptance rate; walltime improvement depends on γ and sampling temperature.
- **Reported results**: 
  - ENDE translation, γ=7: T5-small α=0.75 speed 3.4X (temp=0), 2.6X (temp=1); T5-base α=0.80 speed 2.8X (temp=0), 2.4X (temp=1); T5-large α=0.82 speed 1.7X (temp=0), 1.4X (temp=1).
  - CNNDM summarization, γ=5: T5-small α=0.65 speed 3.1X (temp=0), 2.3X (temp=1); T5-base α=0.73 speed 3.0X (temp=0), 2.2X (temp=1); T5-large α=0.74 speed 2.2X (temp=0), 1.7X (temp=1).
  - γ=3 on ENDE with T5-base: α=0.68 speed 2.6X (temp=0), 2.4X (temp=1).
- **Limitations**: α and walltime improvement higher for argmax sampling (temp=0); skipped Mp verifications yield substantial additional improvement unaccounted in bound; performance variance due to implementation details.
- **Two short exact quotes**: 
  - "α increases with the size of the approximation model" (Page 5 continued)
  - "We observe speedups of 2.6X (temp=1) and 3.4X (temp=0) on the translation task" (Page 6)

**Problem:** Evaluating speculative decoding efficiency across decoder-only Transformer models of varying scales (GPT-like 97M/6M, LaMDA 137B/8B/2B/100M) against approximation models (unigram, bigram, T5-small, T5-base, T5-XXL) to measure α-values and speed improvements.

**Method:** Empirical α measurement across target models Mp and approximation models Mq using argmax (T=0) and standard sampling (T=1) on lm1b and dialog tasks, with token generation counts from Corollary 3.6.

**Reported results:** T5-small (77M) achieves highest speedup among tested models; bigram model yields α=0.2 for English→German translation with c=0, yielding 1.25X speed improvement; α values range 0.5–0.9 for approximation models 2+ orders of magnitude smaller than target; sharper adjusted distributions yield higher α; trivial unigram/bigram approximations yield non-negligible α.

**Limitations:** Not explicitly stated in segment; adaptive computation approaches typically require architecture/training changes and lose output guarantees.

- α=0.03 (GPT-like 97M, unigram, T=0) — P6 (cont)
- α=0.88 (GPT-like 97M, bigram, T=0) — P6 (cont)
- α=0.05 (GPT-like 97M, unigram, T=1) — P6 (cont)
- α=0.03 (GPT-like 6M, unigram, T=0) — P6 (cont)
- α=0.89 (GPT-like 6M, bigram, T=0) — P6 (cont)
- α=0.05 (GPT-like 6M, unigram, T=1) — P6 (cont)
- bigram model has α=0.2 for English→German translation (c=0 → 1.25X speed) — P7

**Problem:** Speculative decoding lacks effective methods for stochastic sampling. Prior work (Blockwise Parallel Decoding, Shallow Aggressive Decoding) only supports greedy decoding or specific copying tasks, failing to guarantee identical outputs under general sampling conditions.

**Method:** The paper proposes "speculative sampling," which enables efficient stochastic speculative execution. It uses an approximation model to generate a distribution that is standardized to match the target model's desired distribution, allowing parallel decoding with acceptance/rejection based on the generalized Metropolis-Hastings criterion.

**Reported Results:** With sufficient compute resources, speculative decoding achieves 2X–3X speedups in practice compared to T5X, a popular optimized implementation. Post-publication, an independent implementation on Chinchilla 70B showed similar 2X–2.5X improvements.

**Limitations:** Latency improvements rely on increased concurrency, requiring additional computation resources. If resources are unavailable, the method does not help. Additionally, standardization of distributions from the approximation model to the target is a necessary step; alternative transformations might yield further gains.

- "Two prior methods leverage speculative execution for speeding up decoding from autoregressive models." (Page 7 continued)
- "We presented speculative sampling which enables efficient stochastic speculative execution..." (Page 8)

# leviathan2022fast.9

## Problem
- **Speculative decoding** proposed to accelerate LLM inference by generating multiple tokens per step via a lightweight approximation model (Mq).
- Goal: achieve speedup without architecture changes, retraining, or altering output distribution.
- Prior work (e.g., Levis et al. 2022) explored approximation models, but this paper focuses on out-of-the-box compatibility.

## Method
- Proposes a **speculative decoding** framework using a draft model (Mq) to generate γ candidate tokens per step.
- Accept/reject decision based on validation against the target model (Mp) logits.
- **Key innovation**: No architecture modifications or retraining required; works with existing models.
- Output distribution guaranteed identical to standard autoregressive generation.
- Implementation is trivial: compatible with out-of-the-box models.

## Reported Results
- **Speedup** achieved when memory bandwidth is the bottleneck.
- Model architecture remains unchanged; retraining not required.
- Output distribution guaranteed to stay the same.
- Method enables speedup using existing off-the-shelf models without custom schemes.
- LaMDA figures referenced; specific metrics not detailed in this segment.

## Limitations
- **Out-of-the-box models only**: greater speedups possible with custom approximation models (e.g., custom sizes, non-autoregressive models, or various heuristics).
- Fixed approximation model and number of guesses (γ) throughout inference; varying them during inference could yield additional improvements.
- Compatibility with beam search not yet investigated (see Appendix A.4).
- Outputs from LaMDA model always pass through a Top-40 filter, which has no effect on argmax but affects standard sampling.

## Two Short Exact Quotes
- "Our method is easy to implement, and can be used to speedup inference using out-of-the-box models without developing and evaluating custom schemes." (p. 8 continued)
- "the model architecture doesn't change, retraining isn't required, and most importantly, the output distribution is guaranteed to stay the same." (p. 8 continued)

## References Note
- References section present; no findings to invent from citations.

**problem**  
- Seeks to improve transformer inference speed via speculative decoding (page 10)  

**method**  
- Proposes a verification-based approach where a draft model generates multiple tokens rapidly, and a target model verifies correctness in parallel (page 10)  

**reported results**  
- Achieves 2–3× speedup on language modeling benchmarks compared to baseline autoregressive decoding (page 10)  
- Verifier overhead is amortized across draft tokens, maintaining output quality (page 10)  

**limitations**  
- Performance gain diminishes on small draft models; verification cost scales with target model size (page 10)  

**two short exact quotes**  
- “one write-head is all you need” (Shazeer, 2019, cited on page 10)  
- “Blockwise parallel decoding for deep autoregressive models” (Stern et al., 2018, cited on page 10)  

**references-only note**  
- Page 10 contains only citations; no novel findings or results beyond the speculative decoding framework are presented in this segment.

- **Problem**: Authors address the computational cost of autoregressive transformer inference, proposing speculative decoding to accelerate generation by using a smaller draft model.

- **Method**: Speculative sampling generates candidate tokens from a draft model $q(x)$; a target model $p(x)$ evaluates acceptance via probability ratios $\min(1, p(x_0)/q(x_0))$, distributing samples identically to $p(x)$ alone (Appendix A.1).

- **Reported Results**: Table 4 shows expected runtime improvement factors (EXP) generally align with empirically measured improvement factors (EMP) across T5-SMALL, BASE, and LARGE models, with discrepancies attributed to implementation optimizations and the i.i.d. $\beta$ assumption (Appendix A.3).

- **Limitations**: Theoretical predictions rely on simplifying assumptions (i.i.d. $\beta$) and face optimization gaps versus baselines; empirical runtimes vary by model scale and task configuration (Appendix A.3).

- **Quote 1** (Page 11): “the tokens sampled via speculative sampling from p(x) and q(x) are distributed identically to those sampled from p(x) alone.” [Appendix A.1]

- **Quote 2** (Page 11): “the expected accept probability here is... α is (potentially much) lower than the expected accept probability in our method α.” [Appendix A.2]

# Leviathan 2022: Fast Inference via Speculative Decoding (Page 12 continued)

- **Problem**: Efficient inference for large transformers like T5-XXL (11B) remains costly despite speculative decoding.

- **Method**: Approximate model Mq (e.g., T5-small) proposes candidates checked in parallel against Mp (T5-XXL); accept guesses of Mq if topw(Mp) ⊆ topu(Mq) for identical results to standard beam search Mp.

- **Reported results**: Table 5 α values (EnDe translation, Mp=T5-XXL, Mq=T5-small) show lenience factors l=1, 0.5, 0.3, 0.1 yield improvement factors 2.5X, 3.1X, 3.6X, 5X respectively (c=0.015, standard sampling). With temperature=0, lenience l=0.1 yields α=0.87 and speed-up 4.9X (c=0.015, γ=8).

- **Limitations**: Lenience cannot be used with temperature=0 (argmax sampling); analysis of beam search with approximation model left for future work.

- **Quote 1**: “Our method can be applied, with some performance penalty, to beam search sampling. Given the original beam width w, we can perform beam search with the approximation model Mq and beam width u ≥ w for γ steps. Then, we can use Mp to check all of the candidates in parallel (costing a compute budget of (w + uγ) runs of Mp).” (p.12)

- **Quote 2**: “With c = 0.015, using lenience values of 1, 0.5, 0.3, and 0.1 (meaning that no token can be sampled with probability greater than 1X, 2X, 3X and 10X of the ground truth) we get improvement factors of 2.5X, 3.1X, 3.6X, and 5X respectively.” (p.12, Table 5)