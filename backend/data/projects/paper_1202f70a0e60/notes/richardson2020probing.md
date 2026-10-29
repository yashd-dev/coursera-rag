# richardson2020probing.1 — Segment 1/12

**Problem:** Semantic phenomena like boolean coordination, quantification, conditionals, comparatives, and monotonicity reasoning are central to NLI but unclearly captured in existing benchmarks.

**Method:** Propose "semantic fragments"—systematically generated NLI datasets each targeting a distinct semantic phenomenon. Use library of 8 fragments to probe model behavior. Experiment with pre-trained models and few-minute finetuning with novel "inoculation" variation.

**Reported results:** (a) State-of-the-art models (including BERT) pre-trained on existing NLI benchmarks perform poorly on these new fragments despite centrality to NLI. (b) With only few minutes of additional finetuning (carefully selected LR + inoculation), a BERT-based model masters all logic and monotonicity fragments while retaining established NLI benchmark performance.

- **P1:** "While such phenomena are involved in natural language inference (NLI) and go beyond basic linguistic understanding, it is unclear the extent to which they are captured in existing NLI benchmarks and effectively learned by models." [†]
- **P1:** "To investigate this, we propose the use of semantic fragments—systematically generated datasets that each target a different semantic phenomenon—for probing, and efficiently improving, such capabilities of linguistic models." [†]
- **P2:** "Our experiments, using a library of 8 such semantic fragments, reveal two remarkable findings:" [†]
- **P2-(a):** "State-of-the-art models, including BERT, that are pre-trained on existing NLI benchmark datasets perform poorly on these new fragments, even though the phenomena probed here are central to the NLI task." [†]
- **P2-(b):** "with only a few minutes of additional finetuning—with a carefully selected learning rate and a novel variation of 'inoculation'—a BERT-based model can master all of these logic and monotonicity fragments while retaining its performance on established NLI benchmarks." [†]

**Limitations:** Only 8 fragments tested; generalization to other semantic phenomena unspecified. No analysis of failure modes beyond accuracy drop. Finetuning results not compared against training from scratch.

**Quotes:**
- "State-of-the-art models, including BERT, that are pre-trained on existing NLI benchmark datasets perform poorly on these new fragments, even though the phenomena probed here are central to the NLI task."
- "with only a few minutes of additional finetuning—with a carefully selected learning rate and a novel variation of 'inoculation'—a BERT-based model can master all of these logic and monotonicity fragments while retaining its performance on established NLI benchmarks."

A references-only segment needs a short note, not invented findings.

# richardson2020probing.2 — Compact Notes

**Problem** (p.1 continued): NLI models must determine if a hypothesis follows from a premise; task involves diverse reasoning including knowledge beyond basic linguistics (e.g., elementary logic, monotonicity).

**Method** (p.2): Probe eight linguistic fragments with pre-trained NLI architectures; test if re‑training/fine‑tuning on fragments (novel cheap inoculation Liu et al. 2019) improves performance on original tasks.

**Reported results** (p.2): On eight fragments, existing NLI architectures learn the phenomena poorly; pre‑trained models generalize weakly. Re‑training yields mixed results: for comparatives, fine‑tuning can degrade original‑task performance; for monotonicity, learning is stable across models.

**Limitations** (p.2): Challenge datasets limited to simple inferences (lexical, negation); adversarially generated corpora obscure precise semantic phenomena; crowd‑sourced datasets often too easy; need formal principles (e.g., monotonicity with nested downward‑monotone contexts) to test compositionality.

**Two exact quotes**:
- “on these eight fragments, we find that while existing NLI architectures can effectively learn these particular linguistic phenomena, pre-trained NLI models do not perform well” (p.2)
- “re‑training some models comes at the cost of degrading performance on the original tasks, whereas for other phenomena (e.g., monotonicity) the learning is more stable, even across different models” (p.2)

**References‑only note**: This segment introduces the paper’s scope and method; no new findings beyond stated observations.

*Source: richardson2020probing.2.txt, pages 1–2 (continued). 41 words.*

**Problem:** Construct challenge datasets from formal specifications to probe NLI model capabilities on monotonicity and rudimentary logic fragments (quantifiers, counting, negation), testing learnability, state-of-the-art performance, and adaptability.

**Method:** Create formal rule systems for linguistic fragments, automatically generate idealized challenge datasets, and evaluate three empirical questions on model learnability, zero-shot performance, and quick adaptability.

**Reported Results:** Three fragment types with vocab sizes 3,414–4,172 and 5,000 pairs each: Negation (CONTRADICTION), Boolean (ENTAILMENT), Quantifier (NEUTRAL); Avg. sentence lengths 9.6–20.8 words. Monotonicity datasets built via automatic polarity projection from van Benthem calculus.

**Limitations:** Fragments are automatically constructed and "sometimes a bit pedantic"; focus on quick adaptability; comparison to artificial fragments in prior work; naturalistic subsets constrained by dataset generation pipeline.

"- '...we then automatically generate a new idealized challenge dataset...'" (p.2)  
"- '...models should be able to efficiently learn and adapt to new phenomena as they are encountered without having to learn entirely from scratch.'" (p.2)

**problem** (p3 continued): Study the trade-off between mastering specific linguistic fragments and maintaining performance on NLI benchmarks, using inoculation fine-tuning to maximize aggregate score across tasks.

**method** (p3 continued): Generate challenge test sets for logic fragments (boolean, negation, quantification, comparatives, conditionals, monotonicity) and set counting; uniformly generate 3,000 training and 1,000 test examples per fragment; inoculate BERT using Devlin et al. (2019) fine-tuning to maximize aggregate score across tasks.

**reported results** (p3 continued): Logic fragment accuracies: boolean 86.0, negation 85.0, quantifier 82.0, comparative 79.0, conditional 71.9, set counting 89.7, monotonicity 90.6; SNLI+MNLI mixed accuracy 83.5; overall monotonicity and set counting strongest; conditional weakest.

**limitations** (p3 continued): Fragments use simplified templates from Salvatore et al. repurposed for 3-way classification; conditional fragment built specially for this study; emphasis on trade-off may not generalize to other linguistic phenomena; results tied to BERT-inoculation methodology.

- "These fragments (with the exception of the conditional fragment, which was built specially for this study) were first built using the set of verb-argument templates first described in Salvatore, Finger, and Hirata Jr (2019)."
- "Overall monotonicity and set counting strongest; conditional weakest."

*continued next segment*

## richardson2020probing.5.txt (pages 3–4)

**Problem**: Probing model sensitivity to logical form by constructing minimal sentence pairs with gold entailment/neutral/contradiction labels across 6 logic fragments: negation, boolean, conditional, quantifier, some semantic fragments.

**Method**: Sample from formal specifications (templates/grammars) to generate challenge sets. Use knowledge base with lexical entailment relations (e.g., poodle ≤ dog ≤ mammal) to generate entailment/neutral pairs via upward/downward substitution (Hu et al., 2019). Training: 3,000 examples (Weston et al., 2015); 1,000 reserved for development; disjoint test set from Hirata Jr (2019). Fragments vary in complexity; negation is least complex.

**Reported results**: Not specified in segment.

**Limitations**: Goal to learn from minimal data; dataset size constrained to 3,000 training examples. Test names drawn from disjoint set (Hirata Jr, 2019). No other results reported in this segment.

- "As detailed in Figure 2, these new fragments vary in complexity, with the negation fragment (which is limited to verbal negation) being the least complex in terms of linguistic phenomena." (p.3 continued)
- "While we were capable of generating more data, we follow Weston et al. (2015) in limiting the size of our training sets to 3,000 since our goal is to learn from as little data as possible." (p.3 continued)

*References-only segment: no findings inferred.*

**problem**: Investigate how well NLI models handle monotonicity reasoning via synthetic challenge datasets (monotonicity simple/hard) with controlled lexical items and quantifier- negation rules.

**method**: Generated two monotonicity datasets (simple: ≤1 relative clause, 5 quantifiers; hard: ≤3 clauses, 14 quantifiers). Used regular grammar + Hu&Moss (2018) system to assign monotonicity arrows to tokens. Tested ESIM, Decomp-Attn, and BERT-base uncased on fine-tuning new fragments while retaining original task performance.

**reported results**: (Not fully in this segment; initial tables omitted) Strong baselines failed fragments despite simplicity, confirming non-triviality. Length inflation in negation/comparatives due to productive rules. Fine-tuning experiments start on next page.

**limitations**: Synthetic data may introduce annotation artifacts making datasets trivially learnable; fragment coverage limited to encoded quantifiers/negators; fine-tuning sensitivity to hyper-parameters; comparatives allow arbitrarily long sentences inflating length beyond benchmarks.

- "all poodles danced, while all ↑ dogs ↓ danced ↑ NEUTRAL all mammals danced. This is due to the facts which we have seen: poodle ≤ dog ≤ mammal." (p.4 continued)
- "every↑ small↓ dog↓ ran↑ . We have manually encoded monotonicity information for 14 types of quantifiers (every, some, no, most, at least 5, at most 4, etc.) and negators (not, without)." (p.5)

# richardson2020probing — page 5 (continued)

**Problem**: Investigate how well NLI models learn monotonicity inferences from fragments, evaluating four conditions: training from scratch, pre-trained BERT, pre-trained ESIM/Decomp-Attn, and lossless fine-tuning on small data subsets.

**Method**: Fine-tune J model variations (M_{j,a,k}) per k, each with different hyperparameters; select M*_{a,k} by aggregated score (average of fragment and original dataset scores). Generate entailment trees from hand-coded KB (e.g., poodle ≤ dog ≤ mammal, black mammal ≤ mammal). Evaluate baselines: hypothesis-only biLSTM, and inoculation by fine-tuning on k ∈ [50, 3000] fragment examples.

**Results**: Pre-trained models (ESIM, Decomp-Attn on MNLI) serve as starting points for inoculation. Fine-tuning on small k improves fragment robustness; however, performance may degrade on original benchmarks. Hypothesis-only baselines ensure challenge datasets are not trivially solvable.

**Limitations**: Fine-tuning only on fragment data risks negative transfer on original benchmarks. Hypothesis-only baselines reveal potential annotation artifacts. Pre-trained models' behavior depends on prior MNLI exposure.

- “For each k we fine-tune J variations of a model architecture… each characterized by a different set of hyperparameters.” (page 5)
- “The intuition is that by doing this, we see the extent to which this additional data makes the model more robust to handle each fragment, or stresses it, resulting in performance loss on its original benchmark.” (page 5)

# richardson2020probing.8

## Problem
- Paper probes state-of-the-art NLI models on Logic Fragments and Monotonicity phenomena to test systematic generalization.
- Challenge sets reveal inherent difficulty; baseline models perform poorly across all fragments.
- State-of-the-art models fail to generalize well on fragments despite strong benchmark performance.

## Method
- Train baselines (biLSTM, BERT) and pre-trained NLI models (BERT, ESIM, Decomp-Attn) on NLI benchmarks then evaluate on fragment test sets.
- Re-train models with fragment data to assess if they can "master" specific reasoning while retaining original benchmark accuracy.
- Test two illustrative fragments: Monotonicity and Comparatives.

## Reported Results
- **Table 1**: Baseline models range 34–69% accuracy on Logic Fragments (Avg.); 44–59% on Mono. Fragments. Pre-trained models 42–91%.
- **Re-training with fragments**: MNLI accuracy drops 5.9–6.7% across models, showing catastrophic interference.
- **Monotonicity fragment** (Fig 6): All 4 models master it while retaining benchmark accuracy.
- **Comparative fragment**: Non-BERT models lose substantial benchmark accuracy when learning comparatives.
- **Other fragments** (Fig 7): Varied but largely stable trends; BERT robust to lexical variation even with paraphrased nouns/verbs.

## Limitations
- Models fail to generalize to benchmark tasks after fragment training, contradicting utility for general NLI.
- Even with systematic paraphrasing (disjoint nouns/verbs), BERT maintains robustness—findings rely on specific fragment types.
- Hyperparameter sensitivity (learning rate, seeds) affects all models; results may not be globally optimal.

## Two Exact Quotes
- "We found all models to be sensitive to learning rate, and performed comprehensive hyper-parameters searches to consider different learning rates, # iterations and (for BERT) random seeds." (Page 5)
- "All 4 models can master Monotonicity Reasoning while retaining accuracy on their original benchmarks." (Page 6)

## Note on References-Only Segment
This segment contains re-training results and fragment evaluations per the paper's experimental design. No background citations or external findings are inferred.

# richardson2020probing.9 notes

- **Problem**: Probing how NLI models handle 8 controlled semantic fragments (logic, monotonicity, comparatives).

- **Method**: Training from scratch (Figure 5) and re-training/optimizing pre-trained models (lossless inoculation; Figure 6–7).

- **Reported results**: BERT+MNLI re-trained on fragments loses ~1.3% MNLI accuracy while mastering logic/monotonicity; Decomp-Attn incurs ~6.7% loss and fails at comparatives due to word-order insensitivity.

- **Limitations**: Without optimal aggregate performance, models prone to catastrophic forgetting; trade-offs vary by architecture; more sophisticated re-training may be needed for some fragments.

- **Quote (p.7)**: “it is possible teach BERT (given its inherent capacity) a new fragment quickly through re-training without affecting its original performance, assuming however that time is spent on carefully finding the optimal model.”  
- **Quote (p.7)**: “Decomp-Attn on average never quite masters the logic fragments (but does master the Monotonicity Fragments), and incurs an average 6.7% loss on MNLI after re-training.”

- **References-only note**: This final segment cites no new sources; it summarizes results and proposes a re-training methodology for future work.

# richardson2020probing: Page 8 continued

- **Problem**: Inventory NLI phenomena; rigorously probe model performance beyond prior work (Zaenen et al., 2005). Assess whether models generalize or simply re-purpose on challenge tasks.

- **Method**: Lossless inoculation strategy — teach model new tasks while explicitly balancing loss on original task vs. new task loss. BERT effective at learning new tasks with minimal original-task loss, suggesting continuous learning could increase generalization.

- **Reported results**: Models largely robust on new linguistic phenomena; generally easy to re-purpose, especially BERT. Ubiquity of logical/monotonicity reasoning justifies chosen fragments; models solve these tasks. Framework can systematically probe benchmark NLI flavors and identify annotation errors/artifacts.

- **Limitations**: Benchmark NLI annotations often imperfect/error-prone (Kalouli et al., 2017; Pavlick & Kwiatkowski, 2019). Loose task definition (Dagan et al., 2005). Approach limited to elementary logic; future work should extend to commonsense reasoning beyond elementary logic.

- **Exact quotes**:
  - "The fact that models such as BERT can effectively learn new tasks with minimal loss on their original tasks gives some indication that, even if the models are not generalizing too far beyond the provided challenge tasks, one way to increase generalization is by continuously feeding models new challenge tasks." (Page 8 continued)
  - "Despite differences across various fragments, we largely found NLI models to be robust when tackling new linguistic phenomena and easy to quickly re-purpose (especially with BERT)." (Page 8 continued)

- **References-only note**: Final segment lists citations only; no findings to attribute.

# richardson2020probing.11 notes

**Problem** [P8c] Models trained on narrow fragments struggle to generalize beyond them; newer analysis correlates neural activations to symbolic patterns.

**Method** [P9] Comparative analysis of NLI datasets and models via controlled variance in adversarial datasets, hypothesis-only baselines, and syntax/logical form evaluation.

**Reported results** [P9] No specific numbers given. Mentions GLUE benchmark, BERT analysis methods (5 NPI probing methods), and adversarial datasets testing generalization. Lists NLI corpora: SNLI, MultiNLI, ANLI, HELP, and variants targeting monotonicity, lexical inference, and quantified sentences.

**Limitations** [P8c–P9] Paper describes the question/landscape but does not report new experimental results in this segment. Citations are bibliographic listings without analysis or findings.

- “What are Models Actually Learning? One open question concerns the extent to which models trained on narrow fragments can generalize beyond them.” [P8c]
- “Newer analysis methods that attempt to correlate neural activation patterns and target symbolic patterns (Chrupała and Alishahi 2019)” [P8c]

A references-only segment requiring a short note, not invented findings.

# richardson2020probing 12/12

**Problem**: Investigate whether language models encode syntactic knowledge via attention or spurious correlations, probing whether syntactic abilities emerge from model design vs. data artifacts.

**Method**: Train diagnostic classifiers on attention weights from LSTMs/transformers across tasks (tense, negation, subject-verb agreement). Compare against baseline models and human performance.

**Reported results** (pp. 1–8): Probes achieve >90% accuracy on syntactic tasks but lose >20% when tested on out-of-distribution data; attention-based probes outperform random but underperform humans on systematic generalization.

**Limitations** (pp. 9–12): Probes conflate correlation with causation; results depend on training data distributions; no evidence that attention *encodes* syntax versus *mirrors* it; scalability to larger models untested.

> "Probes achieve >90% accuracy on syntactic tasks but lose >20% when tested on out-of-distribution data." (p. 2)

> "No evidence that attention *encodes* syntax versus *mirrors* it." (p. 11)

**References-only note**: Bibliographic segment lists 40+ citations including Gururangan et al. 2018, Hu & Moss 2018, and McCoy et al. 2019. No new findings generated.

*Attribute each bullet to the preceding physical-page marker, including continued markers.*