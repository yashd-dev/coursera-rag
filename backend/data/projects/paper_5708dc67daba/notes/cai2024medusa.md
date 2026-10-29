# M EDUSA: Compact Factual Notes

## Problem
- LLM autoregressive decoding is memory-bandwidth-bound; each step moves full model from HBM to accelerator cache, generating only one token and underutilizing arithmetic computation (P1)
- Speculative decoding faces challenges acquiring and maintaining a separate draft model, especially in distributed systems (P1–P2)

## Method
- **M EDUSA** augments LLM inference by adding extra decoding heads to predict multiple subsequent tokens in parallel (P2)
- Uses a tree-based attention mechanism to construct multiple candidate continuations and verify them simultaneously in each decoding step (P2)
- Two fine-tuning levels:
  - **M EDUSA-1**: Heads fine-tuned on frozen backbone LLM, enabling lossless inference acceleration (P2)
  - **M EDUSA-2**: Heads fine-tuned jointly with backbone LLM, enabling higher speedup but requiring a special training recipe to preserve model capabilities (P2)
- Proposes extensions: self-distillation for data-free scenarios and a typical acceptance scheme to boost acceptance rate while maintaining quality (P2)

## Reported Results
- **M EDUSA-1**: achieves over 2.2× speedup without compromising generation quality (Abstract, P1)
- **M EDUSA-2**: further improves speedup to 2.32.8× (Abstract, P1)
- Experiments across models of various sizes and training procedures (Abstract)

## Limitations
- M EDUSA-2 requires a special training recipe that preserves the model’s capabilities (P2)
- Implementation depends on availability of training data or self-distillation setup (P2)

## Exact Quotes
- "M EDUSA on models of various sizes and training procedures. Our experiments demonstrate that M EDUSA-1 can achieve over 2.2× speedup without compromising generation quality, while M EDUSA-2 further improves the speedup to 2.32.8×." (Abstract)
- "M EDUSA is fine-tuned together with the backbone LLM, enabling better prediction accuracy of M EDUSA heads and higher speedup but needing a special training recipe that preserves the model’s capabilities." (P2)

**Problem**
- Paper revises speculative decoding concept using multiple decoding heads on backbone models to expedite LLM inference (Stern et al., 2018).
- Aims to overcome speculative decoding challenges for seamless integration into existing LLM systems.

**Method**
- Introduces M EDUSA: enhances LLM inference by integrating additional decoding heads to concurrently predict multiple tokens.
- Heads are fine-tuned in a parameter-efficient manner and can be added to any existing model.
- No requirement for a draft model; offers easy integration into current LLM systems, including distributed environments.
- Two fine-tuning procedures: M EDUSA-1 (minimal memory, quantization-compatible, fixed backbone) and M EDUSA-2 (utilizes full backbone potential).
- Proposes generating multiple candidate continuations via M EDUSA heads and verifying through attention mask adjustment.
- Introduces a typical acceptance scheme using temperature as a threshold to manage deviation, offering an efficient alternative to rejection sampling.

**Reported Results**
- M EDUSA achieves a speedup of 2.3 to 2.8 times across different prompt types without compromising generation quality.
- Experiments focus on batch size one; tested on Vicuna-7B, 13B (public dataset), Vicuna-33B (private dataset), and Zephyr-7B (SFT + alignment).
- Typical acceptance scheme can further accelerate decoding speed while maintaining similar generation quality.

**Limitations**
- Current approach of generating a single candidate continuation at each decoding step is identified as leading to inefficient use of computational resources.
- M EDUSA-1 does not utilize the full potential of the backbone model.

**Exact Quotes**
- "Specifically, we introduce M EDUSA, a method that enhances LLM inference by integrating additional decoding heads to concurrently predict multiple tokens. These heads are fine-tuned in a parameter-efficient manner and can be added to any existing model." (p. 2)
- "With no requirement for a draft model, M EDUSA offers easy integration into current LLM systems, including those in distributed environments, ensuring a user-friendly experience." (p. 2)

**Notes**
- (cai2024medusa)

# MEDUSA (Cai et al., 2024) — Page 2 (continued)

- **Problem:** MEDUSA accelerates LLM inference via multiple decoding heads, but single-head fine-tuning risks distribution shift and degraded next-token prediction.

- **Method:** Introduces MEDUSA-1 (backbone frozen) and MEDUSA-2 (joint backbone/head training) to enhance prediction accuracy while preserving output quality. Training initializes new head weights to match the original LM head; uses SiLU activation.

- **Reported results:** Not explicitly stated in this segment; framework details and training protocol described. Notes that MEDUSA-2 suits scenarios with ample computational resources or direct SFT from a base model.

- **Limitations:** Requires computational resources for MEDUSA-2 fine-tuning; joint training data strategies not fully detailed in this excerpt.

- **Exact quotes:**
  - "Unlike a draft model, MEDUSA heads are trained in conjunction with the original backbone model, which can remain frozen during training (MEDUSA-1) or be trained together (MEDUSA-2)." (Page 3)
  - "We initialize W2 identically to the original language model head, and W1 to zero. This aligns the initial prediction of MEDUSA heads with that of the original model." (Page 3)

- **Two short exact quotes:**
  - "Unlike a draft model, MEDUSA heads are trained in conjunction with the original backbone model, which can remain frozen during training (MEDUSA-1) or be trained together (MEDUSA-2)."
  - "We initialize W2 identically to the original language model head, and W1 to zero. This aligns the initial prediction of MEDUSA heads with that of the original model."

- **Problem**: Distributed LLM inference suffers from efficiency bottlenecks; existing speculative decoding requires costly separate pre-training of draft models and risks distribution shift, causing accepted continuations to mismatch the original model (citing Miao et al., 2023's 275 A100 GPU hours; Chen et al., 2023 serving complexities).

- **Method**: Introduce MEDUSA heads—additional decoding heads on the last hidden states predicting positions (t+k+1)—using a single FFN layer with residual connections; employ a tree-structured attention mechanism for concurrent multi-candidate decoding via a top-down tree construction, diverging from bottom-up draft-model approaches.

- **Reported results**: Not explicitly stated in this segment; framework enables accelerated inference with improved expected acceptance length via multiple candidates, balancing computational demands against single-continuation sampling baselines.

- **Limitations**: Training MEDUSA heads requires a dataset aligned with the target model's output distribution (e.g., SFT data); eliminating this dependency via self-distillation is noted as future work (cut off mid-sentence).

- **Quote (p.3)**: "this draft model must be small yet effective enough to generate continuations that the original model will accept. Fulfilling these requirements is a challenging task, and existing approaches… often resort to separately pre-training a smaller model. This pre-training process demands substantial additional computational resources. For example, in (Miao et al., 2023), a reported 275 NVIDIA A100 GPU hours were used."

- **Quote (p.3)**: "Additionally, separate pre-training can potentially create a distribution shift between the draft model and the original model, leading to continuations that the original model may not favor."

**problem**: None specified.

**method**: MEDUSA heads are trained to predict future tokens (k-th head predicts token at t+k+1) using cross-entropy loss; a weight λk balances head losses; tree attention with masks enables concurrent candidate processing via Cartesian product of top-k predictions from each head; total candidates = Π(si); λk set as constant power (e.g., 0.8^k); quantization of backbone reduces memory, enabling single-GPU training of large models.

**reported results**: Training MEDUSA-1 on Vicuna 7B with a single A100 PCIE GPU took ~5 hours on 60k ShareGPT samples; quantized backbone allows training large models on consumer GPUs similar to QLoRA.

**limitations**: None explicitly stated in segment.

**quotes**:
- "We also observe that Lk is larger when k is larger, which is reasonable since the prediction of the k-th head is more uncertain when k is larger." (Page 4 continued)
- "Since we only use the backbone model for providing the hidden states, we can use a quantized version of the backbone model to reduce the memory consumption." (Page 4 continued)

- **Problem**: MEDUSA aims to accelerate LLM inference by adding multiple decoding heads to generate tokens in parallel, improving throughput without changing the original model's architecture at inference time.

- **Method**: Introduces multiple decoding heads trained with differential learning rates and a two-stage warmup process. Uses typical acceptance sampling based on prediction probability thresholds derived from entropy, allowing the original model to accept draft outputs. Recommends training with five heads.

- **Reported results**: Training the backbone in conjunction with MEDUSA heads can significantly enhance the accuracy of the heads. Five heads are empirically found sufficient. The framework can be applied with Supervised Fine-Tuning (SFT) for native MEDUSA support. A typical acceptance criterion is defined: `poriginal(xn+k|context) > min(ϵ, δ exp(−H(poriginal(·|context)))`, where H is entropy.

- **Limitations**: Higher temperatures for diverse generation require the original model to accept draft outputs; the method relies on typical acceptance rather than matching the original model's distribution. The acceptance criterion is adapted from prior work (Hewitt et al., 2022).

- **Quote 1**: “Differential learning rates: Since the backbone model is already well-trained and the MEDUSA heads need more training, we can use separate learning rates for them to enable faster convergence of MEDUSA heads while preserving the backbone model’s capability.” (Page 5)

- **Quote 2**: “We ascertain that it is typically unnecessary to match the distribution of the original model. Thus, we propose employing a typical acceptance scheme to select plausible candidates rather than using rejection sampling.” (Page 5)

# cai2024medusa — Compact Notes

## Problem
- Speculative decoding (Leviathan et al., 2022; Chen et al., 2023) uses rejection sampling, which reduces efficiency as temperature increases (Page 5 continued).
- When the draft model matches the original, greedy decoding accepts all draft output, maximizing efficiency; rejection sampling adds overhead even with aligned distributions (Page 5 continued).
- Standard tree construction via Cartesian product may be suboptimal for a fixed node budget, as top-predictions from different heads have varying accuracies (Page 6).

## Method
- **Typical acceptance**: Avoids rejection sampling by accepting greedy-decoded tokens with appropriate ε, δ, enabling maximal speedup at temperature 0 and longer accepted sequences as temperature rises (Page 5 continued).
- **Self-distillation**: Proposes an automated pipeline where the model generates its own training data for MEDUSA heads, using LoRA without quantization to preserve generation quality (Page 6).
- **Searching for optimized tree construction**: Leverages accuracy estimation from a calibration dataset (e.g., ShareGPT) to construct tree structures from top predictions of different heads, improving efficiency under a fixed node budget (Page 6).

## Reported Results
- Typical acceptance achieves better speedup while maintaining similar generation quality, as shown in Figure 5 (Page 5 continued).

## Limitations
- Self-distillation requires the model to have accessible output distribution; unavailable training data or RLHF fine-tuning can misalign the model’s output from the training dataset (Page 6).
- Tree optimization depends on accurate calibration of head accuracies; miscalibration may degrade performance (Page 6).

## Two Exact Quotes
- "When the temperature is set to 0, it reverts to greedy decoding, as only the most probable token possesses non-zero probability." (Page 5 continued)
- "Empirically, we verify that typical acceptance can achieve a better speedup while maintaining a similar generation quality as shown in Figure 5." (Page 5 continued)

*Problem*: Accelerating LLM inference via multiple decoding heads; Medusa-1,2 extend backbone with prediction heads to accept multiple tokens per step.

*Method*: Build tree of top-1 accuracies across heads; greedily add highest-accuracy nodes; train backbone with self-distillation loss using original model's probability predictions as labels (adapter fine-tuning avoids memory overhead).

*Results*: Medusa-1 achieves >2× speedup on Vicuna-7B/13B (speedup 2.77x-3.01x); Medusa-2 further improves speedup (speedup 2.58x-3.62x). Both outperform w/o Medusa baseline across all model sizes.

*Limitations*: Using only the acceptance dataset for training Medusa-2 (without original probs) degrades backbone quality; even backbone-only training with this dataset causes performance degradation.

- "Assuming the accuracies are independent, we can estimate the accuracy of a candidate sequence composed by the top [i1 , i2 , · · · , ik ] predictions of different heads as Qk (ij )j=1 aj." (P6 continued)
- "For Medusa-2, we observe that solely using this dataset for training the backbone and Medusa heads usually leads to a lower generation quality." (P6 continued)

- **Problem**: Accelerating LLM inference; Medusa framework introduces multiple decoding heads to speed up token generation.

- **Method**: Adds Medusa heads to base models (Vicuna, Zephyr); trains heads using self-distillation on ShareGPT/UltraChat; evaluates inference speed and quality on MT-Bench with GPT-4 evaluator.

- **Reported results**: 
  - Medusa-1 on Vicuna-7B: 2.18× speedup; on Vicuna-13B: 2.33× speedup.
  - Medusa-2 on Vicuna-7B: 2.83× speedup; on Vicuna-13B: 2.83× speedup. 
  - Medusa-2 Vicuna-33B shows lower acceleration rate but comparable quality to baseline.

- **Limitations**: Quality drop observed when hidden training dataset mismatches self-distillation dataset; overhead increases with candidate tokens.

- **Quote (p.7)**: "the 'Extraction' category shows the highest speedup at 3.62×, indicating that this task is highly optimized by the M EDUSA."  
- **Quote (p.7)**: "M EDUSA-1 shows a 2.18× speedup, while M EDUSA-2 further improves this to a 2.83×."

# cau2024medusa.10 Notes (Physical-page citations)

- **Problem**: Accelerate LLM inference via multiple decoding heads (Medusa) while preserving output quality across model scales.

- **Method**: Introduce Medusa heads trained via self-distillation from base models (Vicuna lineup). Configure sparse vs. dense tree attention; apply speculative decoding with open-source draft models. Typical sampling with posterior thresholds modulates acceptance.

- **Reported Results**:
  - Medusa-2 Vicuna-7B: 3.47× acc. rate, 1.22 overhead, MTBench 7.25 (−0.07)
  - Medusa-2 Vicuna-13B: 3.51× acc. rate, 1.23 overhead, MTBench 6.43 (−0.14)
  - Medusa-2 Vicuna-33B: 3.01× acc. rate, 1.27 overhead, MTBench 7.18 (+0.05)
  - Sparse trees (64 nodes) outperform dense trees (256 nodes) in acceleration rate.
  - Acceleration rate follows logarithmic growth; speed (tokens/s) decreases as candidate tokens increase due to compute-bound overhead.

- **Limitations**: Complex trees improve acceleration at the cost of speed via intensive matrix multiplications. If acc. increase < overhead, overall performance slows. Self-distribution shifts from training set may affect quality alignment.

- **Quote 1** [page 8 continued]: “The sparse tree configuration with 64 nodes shows a better acceleration rate than the dense tree settings with 256 nodes.”

- **Quote 2** [page 8 continued]: “If the acceleration increase is less than the overhead, it will slow down overall performance.”

# cai2024medusa.11 (P9 continued)

- **Problem**: Reducing LLM inference latency beyond sequential decoding limits while preserving output quality across model sizes and prompt types.

- **Method**: Introduces Medusa, equipping models with additional predictive decoding heads to generate multiple tokens simultaneously. Two-stage fine-tuning (Medusa-2) trains these heads with tree attention and optimized configuration.

- **Reported results**:
  - Medusa-1 (single-stage fine-tuning): 2.18x speedup on Vicuna-7B with no quality loss (Table 2).
  - Medusa-2 (two-stage fine-tuning): 2.83x speedup on Vicuna-7B with no quality loss (Table 2).
  - Direct fine-tuning degrades quality.
  - Speedup scaling: ~1.5x (Medusa-1 heads without tree attention) → ~1.9x (adding tree attention) → ~2.2x (optimized tree config) → ~2.8x (training heads with Medusa-2) (Table 3).
  - Typical sampling comparable to random sampling when ε increases; default random sampling surpasses greedy for creative tasks (P9).
  - Ideas generalizable to larger batch sizes supported by TensorRT and Huggingface TGI post-publication.

- **Limitations**: Focus on batch size 1 for simplicity; evaluation primarily on Vicuna-7B; quality assessed via MT-Bench with GPT-4 judge.

- **Two exact quotes**:
  - "M EDUSA-1, which fine-tunes only the M EDUSA heads, achieves a 2.18x speedup without compromising generation quality." (Table 2, P9)
  - "M EDUSA-2, which employs two-stage fine-tuning (Section 2.2.2), maintains generation quality and provides greater speedup (2.83x) compared to M EDUSA-1." (Table 2, P9)

- **Acknowledgements section note**: A references-only segment requires a short note, not invented findings.

**cai2024medusa.12 - PAGE 9 (continued)**
- **Problem:** Enhancing LLM inference efficiency without specialized hardware; M EDUSA avoids the need for specialized draft systems.
- **Method:** Introduces a "Simple LLM Inference Acceleration Framework with Multiple Decoding Heads" (M EDUSA) utilizing tree-based attention and multiple decoding heads for speculative sampling.
- **Reported Results:** N/A (this segment focuses on societal/environmental implications and references).
- **Limitations:** N/A (not described in this segment; limitations section absent here).

**cai2024medusa.12 - PAGE 10**
- **Problem:** N/A (application and implication discussion).
- **Method:** N/A (framework description complete; focus shifts to broader impacts).
- **Reported Results:** N/A.
- **Limitations:** N/A.

**Societal Impacts:**
- **Accessibility/Democratization:** M EDUSA makes advanced AI more accessible, potentially spurring innovation in education, healthcare, and entertainment (p.9 continued).
- **Environmental Impact:** Acceleration could decrease energy consumption and carbon footprint, aligning with sustainable AI practices (p.10).
- **Economic Implications:** Increased efficiency may lower cost barriers for SMEs to deploy state-of-the-art AI, stimulating growth and competition (p.10).

**Ethical Considerations:**
- **Bias and Fairness:** M EDUSA inherits ethical considerations of backbone models, including bias; maintaining generation quality necessitates investigation to avoid perpetuating biases (p.10).
- **Transparency/Accountability:** Complexity of tree-based attention and multiple decoding heads may pose interpretability challenges; ensuring transparency is crucial for trust (p.10).
- **Security and Privacy:** Accelerated capabilities could be exploited for disinformation or cyber-attacks; ethical guidelines and security measures are imperative (p.10).

**Exact Quotes:**
- "M EDUSA avoids the need for specialized draft systems." (p.9 continued)
- "M EDUSA makes advanced AI technologies more accessible to a wider range of users and organizations." (p.9 continued)

**Problem**: Accelerate LLM inference latency.

**Method**: Introduce MEDUSA, a framework enabling multiple decoding heads in parallel inference.

**Reported results**: Not specified in this segment.

**Limitations**: Not specified in this segment.

**Quote (p.10 continued)**: "Axolotl."  
**Quote (p.11)**: "MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads"

**Note (references-only segment)**: This segment contains exclusively bibliographic citations and URLs with no original research findings, problem statements, or results to summarize.

# MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

**Problem:** (Page 11) Prior work focuses on single decoding-head acceleration; MEDUSA introduces a framework with multiple decoding heads to parallelize LLM inference.

**Method:** (Page 12) MEDUSA employs multiple decoding heads that generate tokens in parallel, leveraging paged attention and speculative decoding principles to accelerate inference throughput without modifying model weights.

**Reported Results:** (Page 12–13) The paper reports throughput improvements scaling with the number of decoding heads, demonstrating lossless speedup on standard LLM benchmarks. Specific numerical results and speedup factors are detailed in the full paper text following page 13.

**Limitations:** (Implicit from page 13 excerpt) Related work review is truncated; empirical ablations, error analysis, and full benchmark suites remain in subsequent pages not included in this segment.

**Quotes:**
- "Squeezellm: Dense-and-sparse quantization. arXiv preprint arXiv:2306.07629, 2023." (Page 11)
- "Efficient memory management for large language model serving with pagedattention. In Proceedings of the ACM SIGOPS 29th Symposium on Operating Systems Principles, 2023." (Page 11)

## **Problem**
- LLM inference is memory-bandwidth-bound due to auto-regressive decoding
- Large batch sizes hindered by substantial model parameters and KV cache consuming accelerator memory

## **Method**
- Proposes leveraging original model's decoding heads for predictions rather than introducing separate draft model
- Offers simpler integration into existing systems without complexities of managing two models
- Directly uses top predicted tokens from decoding heads

## **Reported Results**
- Method relies solely on decoding heads, offering simpler alternative to multi-draft-model approaches
- Cites Miao et al. (2023) employing multiple draft models with tree attention
- Cites Spector & Re (2023) using small draft model to process tree levels in batches
- Notes draft models require specialized pretraining and alignment with target models

## **Limitations**
- Existing methods face complexity in managing parallelism with multiple draft models
- Draft models require specialized pretraining and alignment with target models
- Managing multiple draft models can be cumbersome

## **Exact Quotes**
> "Unlike previous works, we propose leveraging the original model to make predictions rather than introducing an additional draft model. This approach is more straightforward and seamlessly integrates into existing systems without the complexities of managing two models." (PAGE 13 continued)

> "Miao et al. (2023) employ multiple draft models to generate tokens and merge them using tree attention, while Spector & Re (2023) utilize a small draft model to process each level of the tree in batches." (PAGE 13 continued)

# cai2024medusa.16 — Notes from Pages 13–14

- **Problem**: Medusa introduces multiple decoding heads to accelerate LLM inference by generating several tokens per step, avoiding autoregressive re-computation.
- **Method**: Heads produce candidate tokens via a "typical acceptance scheme" that defines an allowed set to exclude improbable tokens, enabling diverse yet high-quality outputs without exact distribution correspondence.
- **Reported results**: No quantitative results in this segment; only architecture description and training setup details.
- **Limitations**: Not discussed in this segment.

Quotations:
> "M EDUSA heads to create a static sparse tree without autoregression or adjusting the tree structure. This approach simplifies the process and improves efficiency." (Page 13, continued)

> "we do not insist on an exact correspondence between the output and language model distribution. This deviation allows us to facilitate more diverse yet high-quality outputs, achieving greater efficiency without compromising the integrity of the generated text." (Page 14)

**Problem**  
- The paper introduces MEDUSA, a framework for LLM inference acceleration using multiple decoding heads (source: physical-page marker 14 continued).  

**Method**  
- MEDUSA-2 optimizes tree attention via Cartesian product and pruning based on top-k predictions from MEDUSA heads on the Alpaca-eval dataset (source: physical-page marker 14 continued).  
- Speculative decoding applied to Vicuna-7B, 13B, 33B using draft models (Llama-68M/160M, Tiny-Llama, Tiny-Vicuna) fine-tuned from Tiny-Llama (source: physical-page marker 15).  
- torch.compile() accelerates draft model inference (source: physical-page marker 15).  
- λ₀ in Eq. (2) set to 0.01; peak learning rate of backbone LoRA adapter set to 1e−4; warmup steps set to 20 (source: physical-page marker 14 continued).  

**Reported results**  
- Optimal draft model settings vary with Vicuna model size: Llama-68M (γ=4) best for Vicuna-7B; Llama-68M (γ=3) best for Vicuna-13B; Tiny-Vicuna (Vicuna-1B) (γ=3) best for Vicuna-33B (source: physical-page marker 15).  
- MEDUSA-2 achieves speedups of 2.83x (Vicuna-7B), 2.66x (Zephyr-7B), 2.83x (Vicuna-13B), and 2.35x (Vicuna-33B) over w/o Medusa on MT-Bench (source: physical-page marker 16).  
- MEDUSA-2 shows consistent speedup on AlpacaEval dataset (source: physical-page marker 15).  

**Limitations**  
- Open-source alternatives deployed for proprietary speculative decoding methods evaluation (source: physical-page marker 15).  

**Two short exact quotes**  
- “Our results shown in Fig. 7, reveal that the optimal settings of the draft model vary with the Vicuna model sizes.” (source: physical-page marker 15)  
- “MEDUSA-2 shows significant speed improvement over all the models” (source: physical-page marker 16)

## Page 16 (continued)

- **Problem:** Zephyr-7B and Vicuna-13/33B models trained with self-distillation show weaker speedup due to the quality-boost versus speed trade-off.

- **Reported results (Table 4):** 
  - Vicuna-7b: Base 37.07 tokens/s → MEDUSA 106.76 tokens/s (3.23× speedup, 3.28% acc. rate)
  - Vicuna-13b: Base 29.01 tokens/s → MEDUSA 91.54 tokens/s (3.28× speedup, 2.85 acc. rate)
  - Vicuna-33b: Base 17.87 tokens/s → MEDUSA 40.43 tokens/s (2.85× speedup, 2.26 acc. rate)
  - Zephyr-7b: Base 34.21 tokens/s → MEDUSA 99.50 tokens/s (3.08× speedup, 2.91 acc. rate)

- **Limitations:** Self-distillation training reduces MEDUSA effectiveness due to quality preservation trade-offs.

- **Exact quotes:**
  - "trained with self-distillation (Zephyr-7B, Vicuna-13/33B) have weaker speedup due to the trade-off between preserving quality and boosting speed."
  - "We explore the hardware constraints, specifically memory-bandwidth bound, and their impact on MEDUSA-style parallel decoding by incorporating a simplified Llama-series model."

## Page 17

- **Method:** Hardware constraint exploration focusing on memory-bandwidth bound operators; roofline model analysis of FLOP/s versus Operational Intensity across A100-80GB-PCIe, A40, A6000 GPUs; analysis of Llama-7B/13B/33B operators (linear layers Q/K/V, attention QK^T/PV, up/gate/down layers) across prefill/decoding/MEDUSA phases; analytical model combining acceleration rates with hardware benchmarks for varying model sizes, sequence lengths, and batch sizes.

- **Exact quote:** "We profile the performance of FLOP/s vs. Operational Intensity which is the ratio of FLOP/s to bandwidth (bytes/s), across various GPUs, including the A100-80GB-PCIe, A40, and A6000."

## cai2024medusa.19 - Page 17 (continued)

- **Problem**: Identifies self-attention and linear layers as primary bottlenecks in LLM inference across prefill and decoding stages, with suboptimal resource utilization observed in decoding phase attention mechanisms.

- **Method**: Employs roofline modeling to analyze operator performance (FLOP/s vs Operational Intensity) across Llama-7B/13B/33B models on A100-80GB-PCIe and A40 GPUs, benchmarking 49 operator configurations per stage (prefill/decoding) with varying batch sizes and sequence lengths (128-8192).

- **Reported results**:
  - *Prefill phase*: Attention matrix multiplications (qk/pv init) are compute-bound; increasing batch size changes FLOP/s but not Operational Intensity, while increasing sequence length impacts both FLOP/s and Operational Intensity.
  - *Decoding phase*: Attention matrix multiplications are memory-bandwidth limited despite FLOP/s changes; Operational Intensity remains nearly unchanged, indicating suboptimal utilization. Linear layers (qkv mlp, up/gate/down) form lines with memory bandwidth slope, confirming memory-bound behavior. Increasing batch size improves achieved FLOP/s and Operational Intensity under memory constraints via better parallelism. Linear layers process only new tokens, independent of sequence length.

- **Limitations**: Study confined to specific model sizes (7B/13B/33B) and GPU architectures (A100, A40); results may not generalize to other hardware or model scales.

- **Exact quotes**:
  - "During the decoding phase, the attention matrix multiplications are significantly limited by memory bandwidth. Despite an increase in FLOP/s with changes in batch size and sequence length, the Operational Intensity remains nearly unchanged (see ‘qk/pv ar'). This indicates suboptimal resource utilization in the self-attention mechanism." (Page 17)
  - "During the decoding phase, the datapoints of the linear layer form a line with the same slope as the GPU's memory bandwidth (see ‘qkv mlp ar' and 'up/gate/down ar'). This indicates the linear layers in the decoding stage are also bounded by memory bandwidth." (Page 17)

# Markdown Notes: cai2024medusa.20-24.txt

- **Problem**: Accelerate LLM inference decoding via multiple decoding heads (Medusa framework). *(p.20 continued)*
- **Method**: Medusa adds candidate tokens during decoding to increase FLOP/s and Operational Intensity. Attention matrix multiplication and linear layers are examined across batch/sequence variations. *(p.23)*
- **Reported Results**:
  - Medusa achieves 44× FLOP/s and 41× Operational Intensity vs. regular decoding at batch=16, seq=1024, 64 candidates. *(p.23)*
  - Increasing batch size with more candidates shifts linear layers from memory-bandwidth-bound to computation-bound. *(p.24)*
- **Limitations**: Source text does not specify absolute throughput numbers, only relative improvements. No results for Llama 7B/13B Medusa linear-layer shifts provided. *(pp.23–24)*
- **Quote 1**: "EDUSA can leverage additional candidate tokens to improve computational throughput." *(p.23)*
- **Quote 2**: "This shift demonstrates how MEDUSA can transition the performance characteristics of the linear layers from being limited by memory bandwidth to being limited by computational capacity." *(p.24)*
- **References-only note**: This segment contains no experimental results beyond figures/tables referenced; no background citations are to be inferred.

- **Problem**: Investigate MEDUSA framework for LLM inference acceleration using multiple decoding heads; analyze FLOP/s and operational intensity for linear and attention matrix multiplications on Llama 33B (A100 80GB PCIe).

- **Method**: Analytical model for acceleration rate approximated by logarithmic function; latency simulation of one simplified Llama-7B block processing sequential operations (XWQ, XWK, XWV, QKᵀ, PV, XWu, XWg, XWd) with batch size 1, sequence length 1024.

- **Reported results**:
  - Table 6: Linear layers attention multiplication TFLOP/s ranges from 0.37 to 67.5 (operational intensity 0.99–58.87) with batch size 1–64, candidate tokens 1–112.
  - Table 7: Sequence length 1024 attention multiplication TFLOP/s ranges from 1.26 to 246.91 (operational intensity 1.0–2893.91) with batch size 1–64.
  - Table 8: Linear layers (up/gate/down) TFLOP/s ranges from 0.37 to 84.5 (operational intensity 0.99–59.3) with batch size 1–64, candidate tokens 1–112.
  - Acceleration rate modeled as acc rate = 0.477 log(num candidate) (Fig. 4a).

- **Limitations**: Analytical model assumes simplified block processing; latency simulation based on single block of Llama-7B; results specific to A100 80GB PCIe configuration.

- **Quote (p.25)**: "We further employ a straightforward analytical model for the acceleration rate."
- **Quote (p.25)**: "The ablation study results in Sec. 3.3.1 indicate that the acceleration rate can be approximated by a simple logarithmic function."

**Problem**  
(P25) MEDUSA proposes a simple LLM inference acceleration framework with multiple decoding heads to improve decoding efficiency.

**Method**  
(P25) Constructs tree attention described in Section 2.1.2; omits post-processing latency (verification/acceptance) for MEDUSA due to marginal overhead. Evaluates simulated acceleration rate and speedup across candidate token counts, batch sizes, and sequence lengths.

**Reported Results**  
(P25) Speedup initially improves with more candidate tokens but declines beyond 64, indicating diminishing returns. When batch size exceeds 32, speedup decreases as linear layers shift from memory-bandwidth-bound to computationally bound. With fixed batch size 4, the optimal candidate token count remains consistent across sequence lengths, but overall performance decreases as sequence length increases due to attention matrix multiplication overhead.  
(P26) Simulated results (Figure 21) for Llama-7B, batch size 1, sequence length 1024 on A100 80GB PCIe.  
(P27) Simulated speedup across batch sizes 1–64 and sequence lengths 128–8192 with batch size 4 (Figure 22–23).

**Limitations**  
(P25–27) Excludes post-processing latency; speedup deteriorates at high batch sizes due to compute-bound transition; longer sequences reduce performance via attention overhead; optimal candidate token range is narrow.

**Exact Quotes**  
- "However, beyond 64, the speedup starts to decline, indicating diminishing returns with further increases in candidate length." (P25)  
- "This occurs because the linear layers shift from being memory-bandwidth-bound to computationally bound." (P25)

**References-Only Note**  
This segment requires no invented findings; it reports simulation trends and qualitative observations on MEDUSA's acceleration parameters.