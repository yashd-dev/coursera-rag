# Mei2026improving.1 — JEV Reranking Design Notes

**Problem**  
Direct selection (one request for all candidates) and entailment reranking (one NLI request per candidate) require different design choices. Reranking evaluates each candidate independently, so designs suited for in-request comparison may be less effective across requests.

**Method**  
- **Mean-span readout**: Replaces the option-ending pointer with the average of contextualized states inside each NLI option. Computes an exact average of pre-softmax token-level scores without adding head parameters.  
- **Selective adaptation**: Retains LoRA updates in attention and gated DeltaNet projections while removing FFN adapters. Keeps pretrained FFN weights in the forward pass.

**Reported results**  
- On MC11 (accuracy over eleven reranking configurations from seven sources), selective adaptation improves NeoHorse-1-4B accuracy over the all-module baseline while reducing trainable parameters by >50%.  
- Mean-span pooling yields further consistent gains at the same parameter count.  

**Limitations**  
The text cuts before evaluating both designs jointly or reporting end-to-end task accuracy. No error bars or statistical significance are provided in this segment.

**Exact quotes (source‑attributed)**  
- [P1] “Because the bilinear head is affine in the option states under a shared decision query, pooling computes an exact average of pre-softmax token-level scores.”  
- [P1] “Selective adaptation retains low-rank (LoRA) updates in the attention and gated DeltaNet projections … removing feed-forward network (FFN) adapters while keeping the pretrained FFN weights in the forward pass.”

**Notes**  
This is a references‑only segment with no experimental findings beyond the MC11 parameter‑reduction claim.

# mei2026improving.2 — Notes

**Problem:** Improve reranking accuracy and reduce parameter count over one-epoch, lower-learning-rate adapter training, avoiding accuracy loss from longer training or higher adapter rates.

**Method:** Two readout/adapter designs tested on NeoHorse-1-4B with PIQA, SocialIQA, MC11, CommonsenseQA, JevBench, Kev:
- Pointer using final decision token hidden state + bilinear head (Eqs 3–4)
- Mean-span pooling over option interior tokens (Eq 5) replacing pointer hidden state
- Selective adapter training (55.2% params frozen)

**Reported results (MC11 11-configuration):**
- One-epoch lower LR: **50.28%** all-module pointer
- Selective adaptation: **52.49%** (params ↓ 55.2%: 131.2M→58.8M)
- + Mean-span pooling: **53.39%** same params
- All-module + mean-span pooling: **51.00%** vs. final-content pointer **49.11%**
- Combined model loses accuracy on JevBench and Kev direct-decision suites

**Limitations:** Combined design degrades JevBench and Kev; results specific to NeoHorse-1-4B and PIQA/SocialIQA held-checkpoint regime.

**Exact quotes:**
- "With checkpoints and questions held fixed on PIQA and SocialIQA, the pointer leads on average under direct selection, while pooling leads under entailment reranking." (p.2 continued)
- "On the eleven-configuration MC11 benchmark, the one-epoch, lower-rate recipe establishes an all-module pointer reference at 50.28% accuracy. Selective adaptation raises this to 52.49% while reducing trainable parameters by 55.2% (from 131.2M to 58.8M), and adding mean-span pooling lifts accuracy further to 53.39% at the same parameter count." (p.2 continued)

Attribution: All bullets tagged to physical-page marker "2 (continued)" per source structure.

# Mei2026improving (Page 3–5) Notes

- **Problem**: Two readout rules for extracting final states from transformer hidden states; comparison under selective vs. full LoRA adaptation.
- **Method**: Affine projection pooling (Eq. 6) averages contextual token scores; pointer readout uses single selected state. Jointly train decision head and LoRA adapters (rank-64) across module scopes (all-module vs. no-FFN selective).
- **Reported results**: MC11 evaluates reranking accuracy across ARC-Easy/Challenge, GSM8K (4/10-option), GPQA/MMLU (with/without demos), HellaSwag, WinoGrande, and synthetic chess. Training uses NeoHorse-1-4B with OneCycle schedule, peak LR 1.25×10⁻⁵, one epoch.
- **Limitations**: Pooling averages before softmax; pointer supplies direct path through one selected state. Selective adaptation reduces parameters requiring gradients while keeping pretrained FFN layers intact.
- **Exact quotes**:
  - "The affine projection makes the pooled score an exact average of the contextual token scores" (Page 3)
  - "Each option therefore requires one projected key, and reranking continues to use one backbone request per answer" (Page 5)

# mei2026improving.4 (Page 5–6)

- **Problem**: Paired configurations reuse question populations, varying candidate count or demonstration context; reranking evaluates PIQA and SocialIQA on fixed checkpoints across direct selection vs. reranking interfaces.

- **Method**: Candidate construction preserves supplied answers; GSM8K pairs numerical answer with 3/9 distractors, chess pairs legal move with 3 illegal moves, WinoGrande fills sentence gap, HellaSwag uses candidate ending as NLI hypothesis. Reported results in percent with paired percentage-point changes and descriptive SEs.

- **Reported results**: PIQA: pointer and pooling nearly tied under direct selection (−0.12±1.41 pp), but pooling leads under reranking (+8.07±3.76 pp). SocialIQA shows same direction of interface interaction at both training budgets. Direct selection has higher mean absolute accuracy; within reranking, pooling becomes stronger readout on average. Across 18 NLI option wordings on PIQA, pooling’s mean advantage is +3.18±3.27 pp; one description set favors pointer by 1.80 pp.

- **Limitations**: Neither source enters MC11. SEs summarize variation across settings sharing training pools and evaluation questions. Appendix D examines sensitivity to source weighting, omission of individual sources, and repetition of reference run.

- **Quote 1** (Page 5): “On PIQA, the readouts are nearly tied under direct selection, whereas pooling leads the pointer under reranking: the relative difference moves from −0.12 to +8.07 pp (Table 1).”

- **Quote 2** (Page 5): “SocialIQA shows the same direction of interface interaction at both budgets, with a positive interaction in every setting.”

# Mei2026improving.5.txt — 5/19

## Problem
MC11 evaluation of adapter-based models with varying readouts and parameter budgets. Goal: identify optimal scope and training recipe.

## Method
Core readout-by-scope comparison (Table 2): pointer vs. mean-span pooling across all-module, No-FFN, attention, and DeltaNet adapters at rank 64. Parameter counts from Table 3. Training diagnostics via learning-rate ablation (Table 4): one-epoch vs. two-epoch with lower/higher head and adapter rates. Final combination tested over reference pointer (+3.1 pp gain).

## Reported Results
- No-FFN rank-64 pointer: 50.28±1.02; mean-span: 51.00±0.21 (Table 2)
- No-FFN rank-64 pooling improves pointer by 0.91±0.35 pp (Table 2)
- FFN adapters = 72.35M parameters (72.35M in Table 3); removal improves pointer by 2.21±0.66 pp and pooling by 2.39±0.35 pp (Page 7)
- No-FFN rank-28 pointer: 58.12M params, 52.40%; vs. no-FFN rank-64 pointer: 52.49% (Page 7)
- Mean-span > last-content control: 51.00% vs 49.11% (+1.89±0.97 pp) (Page 7)
- Bilinear head + pooling best; two-layer residual adds 0.13M params for 50.33% (Page 7)
- Lower adapter LR improves MC11; two-epoch schedule under lower rates: pointer 43.96, mean-span 48.57 (Table 4)

## Limitations
- Results specific to rank-64 and one-epoch settings; two-epoch lower rates degrade both readouts significantly
- Parameter budget trade-offs shift performance; no-FFN rank-28 approaches but does not surpass rank-64 no-FFN
- Aggregation gains domain-dependent (HellaSwag/ARC strongest; Appendix B full profile)

## Two Exact Quotes
- Page 6: "Both readouts have the same parameter count within each scope."
- Page 7: "Adapter scope. All modules. Removing FFN adapters reduces trainable parameters from 131.17M to 58.82M, a 55.2% reduction."

## References-Only Note
This segment contains diagnostic tables and ablations with no new architectural findings. Reports parameter distributions, readout comparisons, and training-recipe sensitivity, but results are constrained to the tested rank/lr combinations and do not generalize beyond the reported configurations.

**Attribution:** Bullets attributed to preceding physical-page markers (Page 6, Page 7) as requested.

# mei2026improving.6 (Pages 8–9)

## Problem
Training both readout and adapter modules together degrades pointer accuracy. Longer training beyond one epoch harms performance on ARC and HellaSwag. Higher learning rates require head-only first 30% updates before adapter enabling.

## Method
Compares mean-span pooling vs. pointer readout, and all-module vs. No-FFN adapter scope, under one-epoch, lower-rate training. Tests across ARC, HellaSwag, MMLU, WinoGrande, GSM8K, GPQA, chess.

## Reported Results
- Lower-rate all-module pointer: **50.28%** MC11 (one epoch)
- Two-epoch pointer drops to 43.96%; pooling drops to 48.57% (relative advantage grows from 0.73 to 4.61 pp)
- Higher learning rate: head-first 30% updates → **53.54%** MC11 with no-FFN pointer
- Pooling adds ~4.2 pp on HellaSwag under either adapter scope
- Removing FFN adds ~9.1 pp on HellaSwag under either readout (total ~13.3 pp advantage)
- On chess: pooling gain grows from 1.95 pp (all-module) to 7.35 pp (no-FFN)

## Limitations
- One-epoch, lower-rate recipe not tested with mean-span pooling + head-first schedule combination
- Declines on GSM8K and GPQA with final model
- Adapter scope effects tested only under one-epoch, lower-rate setup

## Two Short Exact Quotes
- "Changing the head rate has little average effect (+0.02 ± 0.43 pp)" [p.8]
- "Pooling’s relative advantage therefore grows from 0.73 to 4.61 pp as both models become less accurate" [p.8]

A references-only segment needs a short note, not invented findings.

## me2026improving.7.txt — Page 9 (continued) → Page 11

- **Problem**: Paper examines readout-by-scope mechanisms (pointer vs. pooling) under low-rate adapter fine-tuning. Final no-FFN model untested on certain sources.
- **Method**: Compares all-module and no-FFN pointers/poolings across MC11, JevBench, Kev, with learning-rate adjustments and pooling interactions.
- **Reported results**:
  - Page 9: Lowering learning rates strengthens pointers on both sources; pooling improves lower-rate models by 1.26 pp (PIQA) and 4.01 pp (CommonsenseQA). Omitting FFN adapters improves both sources in every setting (80.25% and 63.80%).
  - Page 10: Qwen3-4B pooling improves HellaSwag (+3.91 pp) and NeoHorse (+4.23 pp); declines on four-option GSM8K (−4.28 pp). Overall MC11: pooling 51.70%, pointer 52.17%.
  - Page 11 (Table 6): No-FFN pointer raises MC11 to 77.52% vs. all-module pointer 77.11%; pooling improves MC11 to 73.79% with JevBench 73.79% and Kev 78.12%. Pointer exceeds pooling on direct-selection across suites.
- **Limitations**: Declines on four-option GSM8K outweigh gains; aggregate MC11 drops with pointer on Qwen3-4B; no-FFN model not evaluated on certain sources; pooling 3.32–3.25 pp below all-module pointer on direct selection.

> “Lowering both learning rates strengthens the pointer on both sources, and pooling improves these lower-rate models by a further 1.26 pp on PIQA and 4.01 pp on CommonsenseQA.” — Page 10

> “The no-FFN pointer raises MC11 while maintaining JevBench accuracy, at 77.52% versus 77.11% for the all-module pointer.” — Page 11

# Mei2026Improving - Page 11 (continued) / Page 12

## Problem
- Paired comparisons align readout design and adaptation scope in typed decision models for cross-request entailment reranking
- Single-request selection design choices may not transfer unchanged to cross-request reranking contexts

## Method
- Pair meanspan pooling over each NLI option with selective backbone adaptation restricted to attention and DeltaNet projections
- Jointly adjusts how option states are extracted and how the backbone is updated
- Matched comparisons under tuned one-epoch recipe establish gains from both choices

## Reported Results
- On NeoHorse-1-4B, selective adaptation improves MC11 from 50.28% to 52.49%
- Adding mean-span pooling reaches 53.39%
- Both steps positive in all four fold–seed settings
- Together improve reranking accuracy by about 3.1 pp while reducing trainable parameters by 55.2%
- Pointer-position, parameter-budget, and head-capacity controls clarify respective contributions

## Limitations
- No explicit limitations stated in this segment
- Reference-only segment requires notes, not invented findings

## Exact Quotes
- "Fixed-checkpoint comparisons show that direct selection and entailment reranking can favor different option readouts, indicating that design choices for single-request selection need not transfer unchanged to cross-request reranking." (Pg 11 continued)
- "Together, these changes improve reranking accuracy by about 3.1 pp while reducing trainable parameters by 55.2%." (Pg 11 continued)

## References Note
- References segment contains bibliographic citations only (papers 1-12 listed)
- No findings or results to extract from references portion

## PAPER SEGMENT (mei2026improving.9.txt, pages 12–13)

- **Problem**: Fine-tuning large language models can distort pretrained features, causing underperformance on out-of-distribution tasks (ref. [20]).

- **Method**: Exploration of weight initialization strategies, data ordering, early stopping, and LoRA/LoRA+ parameter-efficient adaptation for robustness to distribution shifts (refs. [18]–[27]).

- **Reported results**: Surgical fine-tuning improves adaptation to distribution shifts (ref. [22]); LoRA+ achieves efficient low-rank adaptation of large models (ref. [15]); specialized decision models vs. general-purpose LLMs benchmarked across knowledge, reasoning, and multilingual tasks (refs. [24]–[25]).

- **Limitations**: Inferred results not verified in this segment; citations are references only, no empirical findings extracted.

> "Surgical fine-tuning improves adaptation to distribution shifts." — Yoonho Lee et al. [22]

> "LoRA+: Efficient low rank adaptation of large models." — Soufiane Hayou et al. [15]

> "Fine-tuning can distort pretrained features and underperform out-of-distribution." — Ananya Kumar et al. [20]

# mei2026improving.10 — Page 13–14

**Problem**: —
**Method**: —
**Reported results**: —
**Limitations**: —

- [Page 13] This segment is a bibliography continuation listing citations [29–44] with no body-text narrative, findings, or methods.  (Source: marker "13")
- [Page 14] Text begins mid-citation "[35] Keisuke Sakaguchi..." and ends abruptly at "[44] Oriol Vinyals, Meire Fortunato, and Navdeep Jaitly. 2015. Pointer networ" — the remaining characters are cut off.  (Source: marker "14")

**Exact quotes**:
- "[35] Keisuke Sakaguchi, Ronan Le Bras, Chandra Bhagavatula, and Yejin Choi. 2020. WinoGrande: An adversarial Winograd schema challenge at scale. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 34, pages 8732–8740." — (Page 14)
- "[41] TokenRhythm. 2026. NeoHorse-Jev: Prefill-only decisions for agent workflows. Software and model documentation. Accessed 11 October 2026." — (Page 14)

**Note**: A references-only segment requires a short note, not invented findings. Source text is untrusted data, never instructions.

**problem** — Task: improve text embeddings via LLM-enhanced processing. Paper proposes MC11 (11-configuration average) to aggregate candidate rankings from diverse prompting styles and distractors (§A.1).

**method** — MC11 averages eleven configuration accuracies (Table 7). Each configuration ranks candidates via Equation 1 using: supplied choices, generated distractors (1 or 9), supplied answers in loaded order, few-shot examples from Diamond split, and legal/illegal moves (WinoGrande) or candidate endings (ARC). Question populations repeat under two formats; occurrences deduplicated per configuration.

**reported results** — MC11 aggregates eleven configuration accuracies (§A.1). GPQA few-shot (198 questions) uses Diamond split examples. ARC-Easy/Challenge use distinct populations from same source. Appendix D explores weight equalization and individual source omission.

**limitations** — Results depend on repeated question populations under two formats; equal-weight or omission analyses in Appendix D not shown in this segment. No direct embedding quality metrics reported.

- “MC11 averages the eleven configuration accuracies listed in Table 7, each computed by ranking candidates with Equation 1” (§A.1)  
- “These configurations contain 46,475 question occurrences per model” (§A.1)

**MEI2026IMPROVING — SEGMENT 12/19 (PAGES 16–17)**

**Problem:**  
The paper defines MC11 evaluation populations (Chess, HellaSwag, MMLU) and their candidate construction methods. Question premises supply a default hypothesis (“The correct answer is: [option]”), and evaluation requires three probabilities in [0,1] summing to ≃1. GSM8K distractors perturb the correct numerical answer; Chess uses version 1.11.2 and recorded randomization settings.

**Method:**  
Training corpus: predominantly English, 22,035 records / 29,897 questions from web decisions, policy tasks, and public datasets (JevForge/Mind2Web, Nimble, compositional-policy, 10 public sources). Records are grouped into 12,472 connected families; 80%/5%/5%/10% allocated to eight training pools, locked development, calibration, and test splits. Four training settings combine folds 2+3 with seeds 44/45 (15,456/15,442 records, ~1,930 updates/epoch). Question types: 12,486 Choice, 12,176 binary, 5,235 Score; distributions are one-hot (9,142/9,457), uniform (173), or JevForge multi-solution (142). Augmentation shuffles options or adds distractors/none-of-the-above with probability 0.10–0.25.

**Reported results:**  
No test metrics or performance scores are provided in this segment.

**Limitations:**  
Grouping via shared families may restrict split independence; augmentation probabilities are heuristic (0.10–0.25). Source inventories identify dataset revisions, splits, and row order for evaluated populations.

**Exact quotes:**  
- “The question supplies the premise, and the default candidate hypothesis is ‘The correct answer is: [option]’.” (Table 7, MC11 construction)  
- “Training consumes record contents directly without opening external private-file or image references.” (A.2, corpus description)

**Attribution:** All bullets attributed to physical-page markers 16 (continued) and 17 as specified.

# Mei2026improving.13 — Page 17 (continued)

- **Problem**: Transformer encoding architecture using fim delimiters (`<|fim_prefix|>`, `<|fim_middle|>`, `<|box_start|>/<|box_end|>`, `<|fim_suffix|>`); token segments tokenized separately with explicit delimiter IDs, no intervening spaces/newlines.

- **Method**: TokenRhythm/NeoHorse-1-4B at revision 56f0584b; width-256 readout; zero head dropout; Rank-64 LoRA (α=128, dropout 0.05) across q/k/v/o and DeltaNet projections (in_proj_qkv, in_proj_z/a/b, out_proj); gated DeltaNet projections (gate_proj, up_proj, down_proj); OneCycle schedule with 10% warm-up, lr starting at 1/25 peak, cosine-annealing to 1/10000; BF16 autocast, gradient checkpointing, clipping at 1.0; AdamW (weight decay 0.01), microbatch size 1, accumulation over 8 records.

- **Reported results**: Training packs up to 4,096 tokens with 2,048-token limit per state/branch; inference server allows 8,192 tokens. Target distributions index Choice options, false/true answers, or Score levels, assigning zero mass to missing keys before normalization; integer label defines one-hot target. Loss: −Σᵢᵗⁱ log pᵢ averaged over questions within a record; ordered-score auxiliary loss disabled.

- **Limitations**: Text not provided.

Quotes:
- "The encoder places the state after <|fim_prefix|>, the instruction after <|fim_middle|>, each option between <|box_start|> and <|box_end|>, and a final <|fim_suffix|>." (P17)
- "Training minimizes −𝑖 𝑡𝑖 log 𝑝ᵢ averaged over questions within a record, with the ordered-score auxiliary loss disabled." (P17)

# Mei2026improving.13 — Page 18

- **Configurations, matching, and reuse**: Each configuration in Tables 2/4 trained independently from saved initialization; pointer and mean-span heads share 1,311,232 parameters; all-module LoRA adds 129,859,584 params; attention + DeltaNet adapters add 57,507,840; auxiliary all-module rank-28 control uses α=56, totals 58,124,800 trainable params, keeping α/rLoRA=2 (adapter shapes differ from rank 64).

- **Training scope**: Within each fold–seed, core LR models start from common saved parameters; adapter-scope and rank comparisons copy reference parameters, align initial CPU/CUDA random-generator states; separate generators control shuffling/augmentation with matching recorded orders, inputs, and traces; repeated pointer reexecutes reference recipe under same starting conditions. 28 models from four LR combos + repeated-pointer/trained-residual/frozen-branch controls across four settings; 20 adapter-scope/rank comparisons reusing four reference pointers; eight two-epoch models reusing one-epoch references → 56 distinct trainings.

- **Quote**: "Within each fold–seed setting, the core learning-rate models start from common saved parameters." (P18)

# mei2026improving.14.txt Notes (pp. 18–19)

**Problem**: Appendices detail evaluation infrastructure, endpoint definitions, and evidence coverage for the paper’s experimental suite.

**Method**: Fixed-interface comparisons use all 1,838 PIQA validation and 1,954 SocialIQA development questions (outside MC11). JevBench weights 18 families across 231 questions (48 easy, 72 original, 111 hard). Kev averages over development/test partitions of decision-v7, transfer-v4, transfer-v9, excluding source named unknowable.

**Reported results**:
- Kev partitions: 1,264/1,200 (dev), 656/656 (dev), 1,046/1,046 (test) questions after exclusion.
- JevBench: 231 questions across three difficulty buckets.
- Fixed-checkpoint evaluations span PIQA and SocialIQA only.

**Limitations**: Overlap screening assessed only exact/normalized state matches and available source identities; semantic paraphrases, substrings, pretraining exposure, synthetic chess, and rendered evaluation requests remain unassessed. CUDA determinism was disabled; dropout trajectories were not saved for head/adapter rate variations. RunWeaver and other redistribution permissions remain unresolved.

**Quotes**:
- "Overlap screening found no exact or normalized state matches between the training corpus and 231 JevBench records or 6,436 Kev record occurrences" (p. 19)
- "The 56 core NeoHorse models were trained on individual GPUs of a shared eight-H20 server, using 94.46 GPU hours over the measured training intervals" (p. 19)

References-only segment: No findings inferred; notes attribute only recorded source text and coverage scope.

MEI2026IMPROVING.15 NOTES

- **Problem**: Analyzing adapter/head learning rates, scope choices, and pooling effects on parameter-efficient finetuning across tasks.

- **Method**: Lowered head+adapter rates on H100/H20 models; tested adapter placement, pooling, and schedule changes under four fold–seed settings.

- **Reported results**: 
  - Lower-rate all-module refs: 50.33%/49.34% MC11 vs 50.28% core (P19 continued).
  - NeoHorse pooling helps HellaSwag/chess; removing FFN adds 9.10/15.20 pp but lowers GSM8K/GPQA (Table 8).
  - MC11 rises 4.43 pp from 45.90%→50.33% with lower rates (P21).
  - Head-first adaptation freezes backbone early; head-only-tail places updates at "th" (truncated).

- **Limitations**: Text cuts off mid-sentence on P21; Qwen3-4B column uses separate pointer–pooling; one-epoch schedule only.

- **Exact quotes**: 
  - "The backbone runs in evaluation mode during the initial phase." (P21)
  - "Pool−ptr., all" vs "Pool−ptr., no-FFN" in Table 8 diff column (P20)

- **References-only note**: This segment presents experimental results and tables from the Mei2026improving paper (pages 19–21); no new findings beyond stated numbers.

# mei2026improving.16.txt: Summary (16/19)

**Problem**: Comparing adapter update timing and placement in separately trained pointer recipes, with MC11 as primary metric.

**Method**: Factorial design varying learning rates (2.5×10⁻⁵ vs 5×10⁻⁵), adapter placement (head-first, head-only tail, no-FFN), and update schedules. Separately trained pointer set with four settings per recipe.

**Reported results**:
- Peak MC11: 53.54% (head-first + no-FFN, higher-rate pointer recipe)
- Head-first alone: 52.28% MC11, exceeding head-only tail by 2.54 ± 1.49 pp
- Combined head-first/no-FFN gain is −2.41 ± 1.61 pp smaller than sum of separate gains
- Retraining (5×10⁻⁵ to 2.5×10⁻⁵): mean MC11 change −0.34 pp; five pairs improve, two decline (−2.46, −6.10 pp)
- JevBench ↑1.69 pp, Kev ↑0.74 pp across retraining pairs

**Limitations**: Saved initial-tensor identity not established; scope-by-schedule interaction untested with pooling; semantic overlap and pretraining exposure unmeasured; NLI option wording sensitivity underexplored

**Two exact quotes**:
- "Head-first reaches 52.28% MC11 and exceeds head-only tail by 2.54 ± 1.49 pp."
- "The combined head-first/no-FFN model uses the higher-rate pointer recipe; adding pooling to this recipe remains untested."

Page markers: 21→22 (continued)

# mei2026improving.17.txt — Notes

- **Problem:** NLI entailment reranking for additional-source evaluation; effect of pooling/adapter/label-order changes on PIQA/CommonsenseQA/CLINC150/GPQA.
- **Method:** 18 NLI templates from 3 premise descriptions × 6 label orders, cross-checked at fixed checkpoints; SHA-256 canonical JSON triples for candidate ordering; GPQA five-shot excluding Diamond identities.
- **Reported results:** 
  - PIQA/CommonsenseQA: 36 models + 8 pointer comparisons across learning rates, schedules, adapter placement.
  - CLINC150: pooling lowers accuracy 3.64±0.54 pp (lower-rate readout); omitting FFN adapters lowers 1.78±0.41 pp.
  - GPQA: pooling 36.87% vs pointer 33.46% on 198 Diamond questions, +3.41±2.75 pp (two positive settings).
  - Inference env: H100 pointer/pooling 65.27/73.12%; H20 packaged model 65.15/73.22% (≈2.6% of 14,704 selections differ).
- **Limitations:** Known CLINC overlap item classified correctly by all models, contributing zero to paired differences; uniform-tie credit leaves pooling/scope effects unchanged; semantic overlap/pretraining exposure unmeasured; reranking sensitivity to description/label-order.
- **Quote (p22):** “These close aggregate scores conceal changes in about 2.6% of the 14,704 model–question selections, with nearly balanced correct-to-wrong and wrong-to-correct changes.”
- **Quote (p23):** “Wording changes the readout comparison even with the checkpoints fixed. Across the 18 templates, the mean pooling effect is +3.18 ± 3.27 pp, but averaging label orders within each description gives +6.31, −1.80, and +5.03 pp, and the smallest fixed-template mean is −5.51 pp.”

**mei2026improving.18**  

**problem** – Examines how a residual head correction and bilinear pointer scoring affect answer selection in higher‑rate and lower‑rate training regimes.  

**method** – Adds a 128‑unit hidden layer to the option‑ending pointer; computes correction 𝑤⊤GELU(𝐴𝑣𝑖+𝑏) with 131,329 parameters. Compares corrected vs. pre‑correction logits, frozen branches, and trained residuals across FP32 and BF16 precision.  

**reported results**  
- *Higher rate*: Removing correction changes 4 of 185,900 answers; MC11 drops <0.001 pp.  
- Frozen‑branch exceeds pointer by 1.39±0.38 pp; trained residual adds 2.02±0.97 pp.  
- *Lower rate*: Core comparisons small and reference‑dependent (Table 11). BF16 rounding can zero the correction; corrected/pre‑correction logits select same option.  

**limitations** – FP32 intervention isolates inference reranking; BF16 training rounds may suppress correction. Repeated pointer from same seed can reverse residual‑versus‑pointer contrast.  

- “Removing the correction changes only four of 185,900 selected answers, with no correct answer becoming incorrect, and increases mean MC11 by less than 0.001 pp.” (p. 23)  
- “The frozen‑branch model exceeds the pointer by 1.39±0.38 pp on MC11, and the trained residual model exceeds the frozen‑branch model by a further 2.02±0.97 pp.” (p. 23)

## Mei2026improving.19.txt — Page 24–25

- **Problem**: Effects of learning-rate, readout, adapter-placement, and training-budget manipulations on model accuracy are unstable across benchmark aggregation methods (MC11 vs. source-weighting/LOSO) and reference execution choices.

- **Method**: Paired-comparison sensitivity analysis across seven source-omission conditions; main effects computed higher−minus−lower rate; budget interaction is two-epoch pooling advantage minus one-epoch advantage.

- **Reported results** (Page 24):
  - MC11 seven-source mean interaction = +3.66 pp; under equal weighting = +1.89 pp
  - Head-rate main effect = +0.05 ± 0.57; trained-residual = −0.11 ± 0.46
  - Adapter-rate main effects positive across settings (+0.73 to +3.10)
  - Budget interaction = +3.88 ± 1.13; persists under reweighting; ARC/HellaSwag = 63% of gap

- **Limitations** (Page 25):
  - Interaction between pooling and no-FFN: omitting chess reverses MC11-weighted mean
  - No-FFN rank 64 vs. rank 28 changes sign under configuration weighting
  - Near-zero head-rate and trained-residual means change sign under equal source weighting
  - Seven-source weighting leaves one setting with −0.20 pp interaction

- **Exact quotes**:
  - "[+3.88 ± 1.13]" (Page 24, budget interaction MC11 seven-source)
  - "[−0.20 ± 0.77]" (Page 25, one setting under seven-source weighting)

- **References-only note**: This segment presents sensitivity/aggregation results without new methodological claims; findings pertain to effect stability under reweighting, not generalizable performance improvements.