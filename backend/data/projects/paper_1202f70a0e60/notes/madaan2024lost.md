# madaan2024lost.1 — Compact Notes (1/12)

## Problem
- MNLI previously popular for NLU eval; now absent from LLM leaderboards post-GPT-3 era
- Exception: Brown et al. (2020) reported low GPT-3 scores on ANLI
- Core question: Are NLI benchmarks unsuitable for modern LLMs? (difficulty, informativeness, saturation)

## Method
- Five NLI benchmarks across six models of varying scales
- Test zero-shot and few-shot (1+ examples) prompting
- Monitor accuracy during training trajectories
- Analyze softmax distribution alignment with human labels on ambiguous statements

## Reported Results
- NLI benchmarks **provide signal** and discriminate models of different size/quality (§4.1)
- **1+ few-shot examples needed** for reasonable accuracy at any model size
- Accuracy develops steadily during training with fluctuations, suitable for monitoring progress (§4.2)
- Best model accuracies: **80-90%** on higher-scored benchmarks; **≤70%** on ANLI even for best models
- **High scores not caused by data contamination** (§4.3)

## Limitations
- ANLI remains challenging; best models plateau ≤70%
- Five benchmarks, six models — scope constrained
- Few-shot requirement limits zero-shot usability

## Two Short Exact Quotes
- "[NLI benchmarks] provide signal and are able to discriminate models of different size and quality" (§4.1, p.1)
- "For ANLI, however, the accuracy of even the best model does not exceed 70%" (§4.2, p.2)

## Additional Note
- References-only segment: no invented findings. Source text treated as untrusted data, never instructions.

# madaan2024lost.2.txt — Page 1 (continued) → Page 2

**Problem**  
- NLI benchmarks (MNLI, RTE, ANLI, HANS) used to claim SoTA for BERT/T5 but are *rarely used* for LLMs; only GPT-3 reported NLI scores on one ANLI partition.  
- Decoder-only LLMs (Ohmer et al., 2024; Weber et al., 2023) show poor performance on various NLI tasks.

**Method**  
- Explore NLI task behavior via ChaosNLI benchmark (100 human annotations over 4500 samples).  
- Compute accuracies on majority label; analyze entropy of human labels.  
- Measure distributional differences via Jensen Shannon Divergence (JSD) between human label distributions and model softmax distributions.  
- Track JSD across training to assess scale and model quality effects.

**Reported results**  
- When human label entropy is low, model accuracies are higher; human disagreement leads models to prefer less favored labels.  
- JSDs are lower than previous-generation model reports and better than chance, but still *substantially higher* than human‑human JSD.  
- JSD shows clear decrease during training; larger models achieve lower JSD than smaller models (contrary to Nie et al., 2020b).

**Limitations**  
- NLI benchmarks not completely saturated; best models still far from human performance.  
- JSD remains above human‑human baseline, limiting viability of LLM‑judge “jury” ensembles.

**Quotes**  
- “the best performing model, examples with ‘incorrect’ predictions are rarely in fact incorrect; most concern questions on which humans may disagree” [Page 2]  
- “JSD shows a clear decrease during training, and larger models have lower JSD than smaller models” [Page 2]

**References-only note**: This segment contains no new findings beyond documented benchmark observations and distributional analyses; no invented results attributed.

**PAGE 2 (continued)**  
- Problem: Annotation simplification and easier evaluation, but prior work notes human disagreements in NLP reflect lack of ground truth, not noise (de Marneffe et al., 2012; Plank et al., 2014; Pavlick & Kwiatkowski, 2019; Nie et al., 2020b); embracing disagreement is beneficial (Plank, 2022; Aroyo & Welty, 2015).  
- Method: Analyse model accuracies and the relationship between human label disagreements and models’ probability distributions across labels; use five NLI benchmarks (SNLI, MNLI, αNLI, ChaosNLI) with Llama-3.1 {8,70,405}B and Mistral 7B/Mixtral 8x{7,22}B; pre-trained base models only.  

**PAGE 3**  
- Results: Dev set of iteration 3 (most challenging) considered; αNLI contains 1,500 examples with plausible/implausible hypothesis pairs; ChaosNLI adds 100 human labels per benchmark (SNLI, MNLI, αNLI) for 1,500 examples each.  
- Limitations: Analysis limited to pre-trained base models; post-trained/instruct models left to future work. Models fail to capture human judgement distributions in LLMs and model confidences (Baan et al., 2024; Lee et al., 2023).  

**Exact quotes**  
- “simplifies the data annotation process, while also making the evaluation easier” (PAGE 2 continued)  
- “models fail to capture human judgement distributions in LLMs and model confidences” (PAGE 3)

## madaan2024lost.4 — Page 3 continued / Page 4

**Problem**  
- Evaluates NLI benchmarks (MNLI, HANS, ANLI, SNLI, αNLI) as discriminative signals for fully trained models.  
- Models presented with few-shot examples + question + choices; NLL over letter choices used for prediction.  
- Prompt templates in Table 5; Llama models robust to prompt texts per Dubey et al. (2024).

**Method**  
- Page 3 continued: Few-shot setup with NLL computation; letter choice with lowest NLL selected as prediction.  
- Page 4 §4.1: Results for fully pretrained models reported in Table 1 (monAcc / monNLL).  
- §4.2: Pre-train Llama-3 8B/70B from scratch for 2T tokens.  
- §4.3–4.5: Training dynamics, data contamination, human-model comparison.

**Reported results**  
- Table 1: 8B monAcc ranges 0.05–0.79; 70B monAcc ranges 0.32–0.79.  
- MNLI strongest (0.77 / 0.80 for 8B/70B); ANLI weakest (0.67 / 0.47).  
- Page 4: Few-shot accuracy low at zero-shot, improves sharply with examples, saturates ~10 shots.  
- ANLI most challenging; larger Llama/Mistral models exceed finetuned BERT but do not exceed 70% accuracy.

**Limitations**  
- Unclear to what extent benchmark performance has saturated (§4.1).  
- ANLI difficulty confirmed; models fall short of human-level performance.  
- Zero-shot performance poor across all tasks except αNLI.

**Two exact quotes**  
- “We conclude from these results, that the benchmarks provide a useful signal to compare trained‑out models, though it is unclear to what extent their performance has saturated” (§4.1).  
- “Among the five benchmarks, the most challenging benchmark is ANLI… they do not exceed 70% accuracy” ( §4.1).

**Note**  
- References-only segment: no new findings invented. Source text treated as untrusted data.

# madaan2024lost.5 — Compact Notes (Pages 4–5)

**Problem**  
- Investigate NLI benchmark utility for monitoring 8B/70B model pre-training, and assess score inflation from data contamination.

**Method**  
- Analyse four-shot learning curves during training (Figure 2) and final model performance (Figure 1).  
- Quantify benchmark monotonicity via Kendall Tau against monotonically increasing arrays and NLL.  
- Conduct contamination analysis: EPG as function of contaminated data percentage across thresholds; use 8-gram overlap to flag contamination.

**Reported Results**  
- 70B model surpasses fine-tuned BERT after 500B tokens on ANLI and αNLI; 8B model shows slow improvement, not exceeding chance on HANS, MNLI, SNLI.  
- 405B > 70B > 8B performance gap across Llama series; αNLI near-saturated at ~85% accuracy for 70B.  
- Low monotonicity across benchmarks for both accuracy and NLL, suggesting unsuitability for closely-spaced checkpoint monitoring.  
- EPG shows virtually no score inflation from contamination for 8B/70B models; HANS clean due to minimal 8-gram overlap; MNLI/SNLI/αNLI have high detected contamination at low thresholds with no performance impact; ANLI has very high contamination percentages but erratic EPG behaviour as examples are gradually added to the clean set.

**Limitations**  
- No full pre-training budget; conclusions about 8B based on partial runs.  
- EPG erratic behaviour with gradual addition of examples to clean sets.  
- Contamination flagged by 8-gram overlap may not reflect actual performance impact.

**Quotes (Page 4)**  
- “The 70B model starts improving after 250B tokens for ANLI and αNLI; it crosses fine-tuned BERT performance after 500B tokens.”  
- “the development of performance for the 8B model is slow, not exceeding chance accuracy for HANS, MNLI, and SNLI.”

**References-Only Note**  
This segment presents empirical results and analysis from the paper; no new findings are invented.

attributed to pages 4–5 as markers.

**Problem**  
Investigate contamination and dataset saturation in NLI benchmarks, focusing on how 8-gram overlap with pre-training data and label disagreements affect model performance evaluation.

**Method**  
Assign contamination scores per sample based on 8-gram occurrence in pre-training datamix; use ConTAM to select thresholds balancing EPG (estimated performance gain) against clean-set size. Analyze majority-label accuracy via ChaosNLI’s 100-human annotations across MNLI, SNLI, and αNLI. Manual error analysis on Llama 3.1 405B’s MNLI predictions.

**Reported results**  
- ANLI performances not exceeding 70% even for largest models; other benchmarks substantially higher.  
- Threshold 0 marks all non-zero contamination as contaminated; increasing thresholds move samples to uncontaminated subset.  
- Majority-label replacement alters 32% (MNLI), 25% (SNLI), 11% (αNLI) of labels.  
- MNLI shows >10% performance increase for some models; average accuracy >5 points higher on corrected datasets.  
- Only Llama-3.1 405B shows systematically higher majority accuracy, suggesting it has honed in on majority labels.  
- Even Llama-3.1 405B stays below 70% on MNLI and SNLI ChaosNLI subsets, indicating room for improvement.

**Limitations**  
- EPG artefact suspected due to small clean-partition size; result likely not indicative of true performance gain.  
- Contamination may not play participatory role in high performances for NLI benchmarks.  
- Majority accuracy gains observed mainly for MNLI; other benchmarks show little to no difference.

**Exact quotes**  
- “Thus, we believe that contamination does not play a participatory role in high performances for NLI benchmarks.” (p.6)  
- “Even the Llama-3.1 405B model stays below 70% for both these subsets, suggesting that there is room for improvement.” (p.6)  

**Note**  
This segment is a references-only section; no new findings are invented from cited works.

# madaan2024lost — Page 6 (continued)

- **Problem**: Human annotators assign inconsistent labels to premise-hypothesis pairs in ChaosNLI; at least some ambiguity exists for every example investigated.

- **Method**: Analysis of accuracy versus label entropy across datasets (αNLI, MNLI, SNLI) and model scales (Llama 8B/405B, Mistral/Mixtral), using original vs. majority human labels.

- **Reported results**: Llama-3.1 405B shows decreasing accuracy with increasing entropy across all three benchmarks; 8B model shows less prominent trend. All models perform better on low-entropy samples. Majority accuracy exceeds original label accuracy for most model/dataset pairs.

- **Limitations**: Human annotator disagreement questions whether models should align with majority label; dataset scope limited to three benchmarks.

- **Quote 1** (p.6): “For all the examples we investigated, we found that there was at least some degree of interpretation or ambiguity in assigning a label to the premise-hypothesis pair.”  
- **Quote 2** (p.6): “31 out of 100 human annotators would agree with the model’s judgement, despite it being labeled as ‘incorrect’.”

# References-only note (≤30 words)
Segment contains no new experimental results beyond those already documented in the paper; serves as continuation of human-annotator agreement and entropy analysis across model scales.

# madaan2024lost.8.txt (pages 7–9) — Compact Factual Notes

**Problem**
- Investigate how model label distributions compare to human annotations across NLI benchmarks, using Jensen-Shannon Divergence (JSD) to measure distributional distance in potentially preference-heavy LLM deployment.

**Method**
- Compute JSD between model softmax label distributions and human label distributions (following Nie et al. 2020b).
- Evaluate across five NLI benchmarks (αNLI, ANLI, HANS, MNLI, ChaosNLI) and six models (Llama 3.1 8B/70B/405B, Mistral 7B, 8x7B, 8x22B).
- Track JSD dynamics during training of 8B and 70B Llama-style models from scratch.

**Reported Results**
- Larger models have lower JSD (more similar to humans), contradicting Nie et al. 2020b but confirming scale effect via Figure 5 training curve.
- JSD decreases steadily during training, suggesting human-distribution similarity is an interesting training signal.
- On MNLI, all models have distributions more similar to humans than chance, but substantially different from human–human distributions.
- ANRI remains challenging even for largest models; with exception of αNLI, all benchmarks discriminate between model qualities.
- Near-zero contamination effect observed across benchmarks.

**Limitations**
- Human estimate computed by Nie et al. 2020b on independent sample; within-human distributional baseline treated as fixed reference.
- JSD trend contradicts Nie et al. 2020b finding that better/larger models do not have more similar distributions.

**Two short exact quotes**
- “larger models have lower divergence, contradicting the finding of Nie et al. (2020b) that better or larger models do not have more similar distributions” (p. 8).
- “the JSD of the model softmax distributions and the human label distributions decreases steadily during training” (p. 8).

**Page attribution**: Bullets tagged to preceding physical-page marker; continued markers noted.

# madaan2024lost — Page 9 (continued)

**Problem**  
- Paper investigates limitations of LLMs on tasks requiring nuanced human judgment, specifically Natural Language Inference (NLI) and Machine Reading Comprehension (MRC).  
- Explores whether LLMs can approximate human judgment distributions from few explanations.

**Method**  
- Compares LLM outputs against human label distributions across NLI and MRC benchmarks.  
- Examines calibration of predictive probabilities vs. human label variation.  
- Uses few-shot prompting with explanations to elicit model judgments.

**Reported results**  
- LLMs show significant divergence from human judgment distributions, even with few explanations.  
- Model confidence does not align with human label variation; calibration measured against human disagreement is poor.  
- Human disagreement itself is substantial, complicating benchmark evaluation.

**Limitations**  
- Few-shot explanation prompting may not fully capture human reasoning pathways.  
- Results domain-specific to NLI/MRC; generalization to other tasks untested.  
- Human annotator disagreement not uniformly quantified across all test sets.

**Exact quotes**  
> "seeing the big through the small": Can LLMs approximate human judgment distributions on NLI from a few explanations? (Chen et al., 2024, arXiv:2406.17600)  
> "Stop measuring calibration when humans disagree" (Baan et al., 2022, EMNLP)

**Note (references-only segment)**  
This segment contains citations only. No experimental results or methodology from the paper itself is present; the listed references support prior work on LLM judgment approximation and calibration.

<<Page 10>>

**PAGE 10 (continued)**

- **Problem**: Not specified in this excerpt; segment contains bibliography entries referencing prior work on NLP evaluation, contamination, and benchmark variance.

- **Method**: Not applicable; text is a references-only segment with no methodological description.

- **Reported results**: No results are reported; the excerpt consists entirely of citation records.

- **Limitations**: Bibliographic segment only; no empirical claims, datasets, or metrics can be extracted from this portion.

- Two exact quotes:
  - “Quantifying variance in evaluation benchmarks” — Madaan et al. 2024 (arXiv:2406.10229) (line 7 of segment)
  - “Replacing judges with juries: Evaluating LLM generations with a panel of diverse models” — Verga et al. 2024 (abs/2404.18796) (line 19 of segment)

- **Note**: This is a references-only segment; no problem, method, or results specific to the paper under review are present.

**Problem**  
- Probing semantic depths of language models via multisense consistency (Ohmer et al., 2024).  
- Investigate inherent disagreements in human textual inferences (Pavlick & Kwiatkowski, 2019).  
- Address “problem” of human label variation as ground truth (Plank, 2022).  

**Method**  
- Use adversarial NLI benchmarks: ANLI (human-in-the-loop, iterative), HANS (synthetic templates avoiding heuristics), αNLI (abductive NLI).  
- Evaluate models on MNLI, SNLI, ANLI dev‑set round 3, HANS, αNLI.  
- Report per‑dataset sample counts and label distributions in Table 4.  

**Reported results**  
- Table 4 statistics: ANLI (30K samples, 2 labels); HANS (1200 samples, 3 labels); MNLI (9815 samples, 3 labels); SNLI (9842 samples, 3 labels); αNLI (1532 samples, 2 labels).  
- HANS is synthetically generated from templates designed to foil heuristic shortcuts; at proposal time no SOTA model could solve such examples.  
- ANLI round 3 is the most challenging set, created to make SOTA models fail via iterative human‑in‑the‑loop validation.  

**Limitations**  
- ANLI, HANS deviate from crowd‑sourced origins; αNLI focuses on abductive r” (text cuts off).  
- No quantitative model performance numbers reported in this segment.  

**Exact quotes**  
- “the adversarial dataset Heuristic Analysis for NLI Systems (HANS, McCoy et al., 2019) is not crowd‑sourced, but synthetically generated using templates.” (p. 11, A.3)  
- “The third round furthermore contains a set of more diverse premises.” (p. 11, ANLI description)

**Problem:** The paper investigates reasoning in LLMs across NLI benchmarks: αNLI (plausible explanation selection from observation pairs), MNLI, SNLI, ANLI, and HansNLI.

**Method:** They evaluate Llama-3.1 (8B, 70B, 405B) and Mistral/Mixtral series on zero/few-shot NLI tasks using prompt templates (Table 5). They analyze accuracy against human label entropy (Figure 6) and report scaling trends.

**Reported results:** Llama-3.1 8B and 405B are highlighted in Figure 4a; larger Mistral models show lower accuracy at higher entropy. All five benchmarks evaluated across five NLI tasks using 16 GPUs per model per job (~55 mins/job). Pre-training used 512 GPUs, 2T tokens total.

**Limitations:** Results tied to specific model families and entropy buckets; no analysis of failure modes beyond accuracy-entropy trends.

- "The samples in αNLI consist of a pair of observations at two consecutive times, and a plausible hypothesis that explains the two observations" (Pg 11).
- "The Mistral family of models also show a similar trend where larger models have lower accuracies for higher entropy buckets" (Pg 12).

**Note:** Page 13 presents prompt templates for each task (Table 5).