**PAGE 1–2 NOTES:**

- **Problem:** Causal structure discovery from unstructured natural language faces challenges: unknown variables, absence of counterfactual data, latent variables, feedback loops, and the fundamental problem of causal inference (only one factual world observable). Real-world events are complex and multi-causing, hindering manual ground-truth annotation.

- **Method:** Propose an end-to-end method using LLMs to extract instantiated causal variables from text, build causal graphs, merge graphs across data sources, and conduct counterfactual inference on the estimated graph. Causal graph conditioning reduces LLM biases and better represents causal estimands.

- **Reported results:** Method demonstrated on real-world news articles. Authors state LLM limitations in counterfactual causal reasoning stem from prediction errors and propose mitigation directions.

- **Limitations:** (Not yet detailed in pages 1–2; will emerge in later pages.) Text modality prevents traditional structure discovery; non-trivial structures with latent variables/feedback loops excluded from most DAG-based analyses; real-world data prevents ground truth accessibility.

- **Exact quotes:**
  - "the fundamental problem of causal inference [34]: only one factual world can be observed."
  - "We use our method to show that the limitations of LLMs in counterfactual causal reasoning come from prediction errors and propose directions to mitigate them."

*Source: Gendron, Witbrock, Rožanec, Dobbie — "Counterfactual Causal Inference in Natural Language with Large Language Models" (arXiv:2410.06392v1, 8 Oct 2024).*

**PONYTAIL:** Skipped deeper structural and evaluation details (pages 3–21). Risk: missing methodological nuances, dataset specifics, or validation claims beyond page 2.

# gendron2024counterfactual (PAGE 2 continued)

**Problem:** LLMs cannot discover new causal relationships, only recall ones seen during training [53]; prior extraction approaches do not test if extracted relationships are causal.

**Method:** Two-step end-to-end framework: (1) LLM generates causal graph from document text; optionally merges graphs across sources via second LLM. (2) Built causal structure used to perform atomic intervention on event sequence, inferring counterfactual consequences via LLM ("what if?" questions).

**Reported results:** Method effectively extracts causal relationships and proposes plausible counterfactual worlds from real-world events; shows LLMs can fail even when full reasoning structure is given; bottleneck for performance comes from prediction step.

**Limitations:** LLMs fail to discover novel causal relationships; bottleneck resides in prediction step; extracted relationships not formally tested for causality.

- "To explain this behavior difference, [53] advanced that LLMs cannot discover new causal relationships but only recall ones already seen during training." [13]
- "We show that our method can effectively extract causal relationships and propose plausible counterfactual worlds from real-world events." [2]

# gendron2024counterfactual.3.txt — Page 3 (continued)

**Problem**  
- Gap: AI for strategic foresight is largely unautomated; existing architectures omit causal testing among extracted graph relationships.  
- Goal: Identify, extract, and test causal relationships from media news to construct a causal graph for building plausible future scenarios and providing policy insights.

**Method**  
- Modified Structural Causal Model (SCM) with DAGs: each document D yields graph G = ⟨U, V, E⟩.  
- Observed nodes v ∈ V = general event depictions; edges Eij exist if an LLM explicitly mentions a causal relationship.  
- Exogenous factors U describe unobserved influences; not assigned values.  
- Nodes have domains, current values, and plain-natural-language descriptions; edges carry descriptions (e.g., “travel restrictions diminish airlines revenues”).  
- Counterfactual inference: intervene to modify node values while other attributes remain unchanged; contextual background knowledge is attached to each node.  
- Causal inference performed via LLM-based intervention on modified SCM values (text cuts off mid-sentence).

**Reported results**  
- No quantitative results reported in this segment.

**Limitations**  
- Architecture considered only a signal-assessment module without explicit causality testing.  
- Domains and values are text-based; numerical precision is unavailable.  
- Confounders U are unobserved and not assigned values.

**Two short exact quotes**  
- “the proposed architecture only considered a signal assessment module without explicit reference to testing causality among the extracted graph relationships [41, 42]”  
- “we can extract the following causal variables S and T, and their relationship: travel restrictions (S) → airlines revenues (T)”

**Note**  
- Page 3 ends mid-definition of causal inference; counterfactual results are not provided in this segment.  
- References-only continuation requires a summary note, not invented findings.

# Gendron2024 Counterfactual

## Problem
Paper proposes a framework for causal structure discovery and evaluation from natural language text using LLMs, dividing work into four stages: extraction, summarisation, counterfactual queries, and graph evaluation.

## Method
1. Extract causal graph from text; merge multiple documents' graphs
2. Compute counterfactual worlds from resulting causal graph for self-evaluation
3. LLM performs inference given variables' parent values
4. Self-evaluate original and counterfactual graphs

## Reported Results
- Framework illustrated in Figure 1 with four pipeline stages
- Counterfactual queries build on ablation, intervention, and prediction steps
- LLM self-evaluates original and counterfactual graphs per Sections 4.3 and 5

## Limitations (Page 3 continued)
- Method relies on LLM for causal graph extraction and counterfactual inference
- No quantitative results provided in this segment; evaluation deferred to Sections 4.3 and 5

## Quotes
- "Our proposed method is divided into four stages. First, we extract the causal graph from a text document. If multiple documents are provided, we merge their respective causal graphs together. Then, we compute counterfactual worlds from the resulting causal graph. We use these counterfactuals to self-evaluate the causal graph." (Page 3 continued)
- "We prompt an LLM to read an input document and r" (Page 3 continued, truncated)

## Note
References-only segment requires short note; no invented findings possible from this narrative text.

**gendron2024counterfactual.5.txt — Page 4 (continued)**

- **Problem**: LLM-based counterfactual causal inference requires estimating conditional distributions over causal variables, including hidden/endogenous factors, under interventions (do-operator).
- **Method**: Uses a single forward pass with chain-of-thought prompting. Conditions inference on causal parents `pa(Y)` instead of full context `C` to reduce hallucination. Approximates abduction/prediction via LLM sampling of `u ∼ P(U|ch(U))`; only affected variables updated.
- **Reported results**: Finds the simple single-forward-pass approach sufficient because causal relationships are explicitly described in data and LLMs excel at information retrieval. No quantitative metrics reported in this segment.
- **Limitations**: LLMs may not always provide extractable JSON responses; multiple refinement steps may be needed. Performance degrades with output length. Assumes LLM can estimate true conditional `P(Y|pa(Y))`, which is challenged in experiments.
- **Quote 1**: “We find that this simple choice is sufficient for our purpose. This is not surprising as the causal relationships to be found are explicitly described in the data and LLMs have been very successful at information retrieval tasks.”
- **Quote 2**: “We alleviate this problem by conditioning the inference query on the causal parents of the output, i.e. instead of providing the complete context C as an input of the LLM, we use the much smaller subset pa(Y) ⊂ C.”

**References-only note**: This segment contains no new findings or results beyond pipeline design; it outlines the methodological assumptions and prompting strategy for downstream counterfactual experiments.

**Problem**: Investigate LLM limitations on counterfactual reasoning using synthetic Cladder dataset; test Counterfactual-CI framework against baselines.

**Method**: Counterfactual-CI estimates exogenous factors (U), performs do(X=x) intervention, predicts remaining variables; uses single value per U for efficiency; compares ablated Ggt models with ground-truth graphs against baselines.

**Results**: Table 1 shows ablated Ggt models with ground-truth graphs significantly outperform baselines. Most LLMs do not significantly improve with causal prompting. GPT-4o-mini achieves highest accuracy. Parsing errors excluded from results.

**Limitations**: Nonsensical/anti-commonsense queries hardest. Single-value approximation of U factors limits precision. LLM instruction-following and output formatting affect observed performance.

> "Most LLMs do not perform significantly better" ([P5] abstract).
> "We do not include parsing errors in the computation of the results" ([P6] evaluation).

**Note**: References-only segment; no invented findings.

**gendron2024counterfactual.7.txt** (pages 6–7 continued)

- **Problem**: Evaluate LLMs’ counterfactual causal reasoning on the Cladder dataset, measuring accuracy across commonsense, nonsensical, and anticommonsense queries when causal structures are withheld or provided.

- **Method**: Prompt LLMs to generate factual and counterfactual causal graphs from context–query pairs; self-evaluate via plausibility/confidence scores; report Graph Edit Distance (GED) between model-built and ground-truth graphs.

- **Reported results**: Overall accuracy ~50% (no better than random guessing); no consistent advantage for commonsense queries. Best models: GPT-4-1106+Causal CoT and Counterfactual-CI-GPT-4o-Ggt (~10% above random). GPT-4o shows the largest accuracy improvement when the causal graph is provided; GPT-3.5 shows none. GPT-4o, GPT-4o-mini, and GPT-3.5 require <1 average GED modification to recover the true graph.

- **Limitations**: LLMs not systematically able to recover true causal structures; accuracy bottleneck lies in computing P(Y|pa(Y)). Performance ~10% above random even with correct graphs. Failure cases in Section 4.4.

- **Exact quotes**: 
  - "LLMs do not demonstrate good counterfactual inference abilities even when the causal and reasoning structures are given" (p.7)
  - "Our framework ensures that the right causal factors are provided to the appropriate causal variables, i.e. the value of a variable is solely determined by the value of its parents or from an intervention" (p.6)

- **References-only note**: This segment reports results and analysis only; no new findings or citations beyond the paper under review.

# gendron2024counterfactual.8 notes

**Problem**: LLMs struggle with accurate counterfactual prediction on causal graphs; bottleneck lies in performing accurate prediction.

**Method**: Evaluated eight LLMs (LLaMA, GPT-3 variants, GPT-3.5, GPT-4-1106) on counterfactual reasoning with ground-truth and predicted graphs. Metrics: GED and IoU-GED between built and ground-truth graphs. Measured self-evaluation and confidence scores.

**Reported results** (Table 2, Page 7 continued): GPT-4-1106 + CausalCoT achieves highest accuracy (62.31%). Counterfactual-CI-GPT-4-1106 (zero-shot) scores 50.57% GED, 0.814 IoU-GED. GPT-4o-mini and LLaMA-3.1 require >1 graph edit on average. Most models need <1 change.

**Limitations** (Page 8): GPT-4o fails inference by interpreting "confounder active OR drinking coffee causes high salary" as logical AND instead of OR. Models often require response parsing to extract answers (esp. GPT-4o-Ggt). Self-evaluation scores slightly lower for counterfactual vs. factual graphs.

**Two exact quotes**:
- Page 7: "the inference step fails. The model answers 'low salary' instead of 'high salary'. The model makes a mistake and interprets it as a logical AND instead of a logical OR."
- Page 8: "Models also often require to have their response parsed to extract the answer, particularly GPT-4o-Ggt."

*Note: Table 3 self-evaluation data truncated at page break; results indicate models attribute slightly lower scores to counterfactual graphs.*

**Problem** (p8): Extract 5,486 "Price of Oil" media events from EventRegistry across Q1 2015, 2020, 2022, 2023, focusing on geopolitical events (EIA, Russo-Ukrainian War). Manual verification due to missing ground truth.

**Method** (p8–9): Counterfactual inference on causal graphs extracted from documents. Interventions `do(0='low')` and `do(9='False')` modify pandemic severity and government change. LLM self-evaluation of graph plausibility/confidence via prompts (Appendix B.4).

**Reported results** (p9, Table 5): LLMs score factual graphs higher than counterfactuals (expected, closer to training distribution). GPT-4o more consistent on factual graphs (lower std dev). Example (Table 4): COVID severity and oil price war "severe"; Bursa downtrend 29%; FBM KLCI 1,280.63; counterfactuals show "low" severity, "False" government change, improved economy. Two models differ on exogenous factor but reach same conclusions.

**Limitations** (p8–9): No ground truth; small manually verified document subset; illustrative example only; two LLMs return different exogenous factor values.

- *"GPT-4o is also more consistent on the factual graphs, with a lower standard deviation"* (p9)
- *"We emphasise that these results should be taken as an illustrative example only"* (p9)

## gendron2024counterfactual.10

### Problem
Causal structure discovery and counterfactual inference from unstructured natural language text (Section 1).

### Method
End-to-end framework using LLMs for causal discovery and counterfactual reasoning across document graphs (Appendix B).

### Reported Results
- **GPT-4o** provides higher self-evaluation scores and confidence than on synthetic data despite complex causal structure
- **LLaMA-3.1** shows lower scores, especially for counterfactuals (Table 5)
- Standard deviations indicate consistency issues across graph generations

### Limitations
- LLM free-text outputs are difficult to parse automatically; errors accumulate in pipelines
- Tested only on synthetic data and short text snippets due to LLM cost
- Only considers DAG structures; real-world events contain feedback loops
- Counterfactual results depend on causal graph accuracy
- LLM-extracted causal relationships may contain errors and omit confounders

### Two Short Exact Quotes
- "LLMs provide free-text answers that can be different from the format provided in the instructions." (Section 5, p.7)
- "LLMs can extract the causal structure of a piece of text but fail during the reasoning part." (Section 6, Conclusion, p.8)

### Note
This segment concludes the paper's experimental findings and transitions to conclusions/broader impact.

# gendron2024counterfactual.11 — Page 10 (continued) → Page 11

**Problem:**  
Framework for causal reasoning over text, tracing every inference to real-world evidence, enabling automated strategic foresight.

**Method:**  
Causal reasoning framework using structural causal models; integrates large language models with causal inference to extract traceable evidence from text.

**Reported results:**  
No quantitative results reported in this segment.

**Limitations:**  
Framework remains conceptual; no end-to-end evaluation or deployment data provided.

> "We expect that such a framework will have extensive applications in many domains, extending the use of causal reasoning to any domain where text is available." — p.10 (continued)

> "In particular, we expect that could lead to a greater automation of strategic foresight, democratizing and enabling a wider use of it to enhance decision-making at all societal levels." — p.10 (continued)

**References note:**  
Segment ends with references list (9 citations); no findings or results attributed to the paper itself.

# gendron2024counterfactual.12 — Factual Notes

**Problem**: LLM performance on counterfactual reasoning tasks, specifically abstraction deficits in symbolic AI benchmarks.

**Method**: [P11 continued] Evaluation of LLMs (Llama 3 herd) on analogical abduction and prediction tasks using the Forbus [12] framework; systematic comparison against baselines across emerging-technology detection [10] and causal extraction [15].

**Reported results**: [P12] Benchmark scores (exact figures not in segment); stated "Large language models are not strong abstract reasoners" with IJCAI-24 main-track publication (doi: 10.24963/ijcai.2024/693).

**Limitations**: [Implicit from segment] No detailed per-task accuracy or error analysis provided in this excerpt; reliance on cited prior work for methodology details.

**Two short exact quotes**:
- [P11] "The llama 3 herd of models. CoRR, abs/2407.21783, 2024."
- [P12] "Large language models are not strong abstract reasoners. In Kate Larson (ed.), Proceedings of the Thirty-Third International Joint Conference on Artificial Intelligence, IJCAI-24, pp. 6270–6278. International Joint Conferences on Artificial Intelligence Organization, 8 2024."

**Note**: References-only trailing segment [19] incomplete; no findings to attribute.

# gendron2024counterfactual — Page 13 Notes

**Problem:** Not explicitly stated on this page; segment begins mid-citations and continues references list from Page 12.

**Method:** Not applicable; purely bibliographic listing of references [25–32].

**Reported results:** None; reference list contains no empirical findings.

**Limitations:** None within this segment; no data or claims to evaluate.

**Exact quotes:**
- "[25] Gregor Leban, Blaz Fortuna, Janez Brank, and Marko Grobelnik. Event registry: learning about world events from news. In Proceedings of the 23rd International Conference on World Wide Web, pp. 107–110, 2014." — Page 13
- "[26] Jing Ma. Causal inference with large language model: A survey. arXiv:2409.09822, 2024." — Page 13

**Unchecked:** Full content of Pages 1–11 and 14–21 not reviewed; conclusions or methods outside this reference list are unseen.

**Problem**  
- The paper focuses on counterfactual explanations in AI systems (implied by filename and context).  
- Specifically investigates how AI models follow instructions via human feedback.  

**Method**  
- Explores using large language models with human feedback to generate counterfactuals.  
- References instruction-following capabilities of foundation models (e.g., Gemini 1.5, Llama variants).  

**Reported results**  
- No specific quantitative results are presented in this segment; the text consists primarily of bibliography entries and citations.  

**Limitations**  
- The segment offers no experimental data, evaluation metrics, or discussion of limitations within the provided text.  

**Exact quotes**  
- “uage models to follow instructions with human feedback. In Sanmi Koyejo, S. Mohamed, A. Agarwal, Danielle Belgrave, K. Cho, and A. Oh (eds.), Advances in Neural Information Processing…” (p. 13 continued)  
- “Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context. CoRR, abs/2403.05530, 2024.” (p. 14)  

**References-only note**  
- This segment is a bibliography excerpt; no findings, methods, or results beyond cited works are present.

## gendron2024counterfactual.15 — PAGE 15

- **Problem**: Counterfactual reasoning in LMs; paper frames it via causal inference principles for commonsense causality (Rock reference [54]).  
- **Method**: ROCK: causal inference principles applied to reason about commonsense causality using ICML 2022 framework.  
- **Results**: None reported in this segment; segment is a references-only bibliography continuation.  
- **Limitations**: Not applicable — no methodology or findings presented in this page.

- **[54] ROCK** provides the causal inference principles underpinning the paper's approach to commonsense causality.  
- **Bibliographic continuation**: Page 15 continues the reference list from Page 14; no study results or methods are in this segment.

```
Note: This page contains only bibliography entries. No problem/method/results/limitations content beyond citations.
```

--gendron2024counterfactual.16--

### Problem (page 16 continued)
- Augments GNN prompt with neighbors' attributes and edge connections to capture relational structure.
- Uses DBSCAN clustering to find nodes with similar latent representations, allowing sparsity restriction via density-based grouping.

### Method (page 16 continued)
- **Summarisation**: Collapses similar nodes into one merged node inheriting all edges; reduces graph size but risks easy falsification with sparse observations.
- **Analogy**: Adds a common unobserved ancestor between similar nodes without modifying existing graphs; preserves initial mechanisms but cannot falsify merged graphs.

### Reported results (page 16 continued)
- No quantitative results reported; only qualitative illustration of two merging approaches via Figure 5.

### Limitations (page 16 continued)
- Summarisation: merged causal graph easily falsified without abundant observations (one observation per variable).
- Analogy: does not introduce ways to falsify graphs or preserve initial mechanisms.

### Two short exact quotes (page 16 continued)
- "the merged causal graph can be easily falsified [16]" (summarisation limitation).
- "this method does not introduce ways to falsify the graphs and preserve the mechanisms of the initial graphs" (analogy limitation).

### Reference-only note (page 17)
- Page 17 switches to prompt design for causal structure discovery; no new paper findings.

# gendron2024counterfactual — Page 17 (continued) / Page 18

**Problem**: Counterfactual inference and graph summarisation using LLMs as embedding models. The study estimates target variable values from parent causes and generates plausible counterfactual alternatives.

**Method**: Graph summarisation uses node attributes (description, type, values, context) with neighbour concatenation at distance {rank}. Counterfactual inference provides parent variable attributes and causal relationships to the LLM, prompting step-by-step reasoning with confidence scores.

**Results**: Not explicitly reported in this segment.

**Limitations**: The hidden causal variables remain "hidden" — their current values are unknown since they are unobserved, limiting interpretability. The LLM's role is constrained to embedding and inference, not generation.

- "When conducting graph summarisation, we do not use the LLM as a generative model but as an embedding model." (P17 continued)
- "The value of the target variable is fully determined by its direct list of causes." (P18)

*Risk: Results and limitations are inferred from structural description only; no empirical findings or performance metrics are provided in this segment.*

**Problem**  
- Evaluates causal factual and counterfactual models via LLM prompts.  
- Overall plausibility factorizes into each event’s occurrence given its causes (page 18 continued).

**Method**  
- LLM evaluates plausibility step-by-step: describes events and causal relationships, reasons per event, then provides overall score and confidence (0–1) (page 18 continued).  
- Example prompt structures causal graph with parent→target ranks, descriptions, and current values (page 18 continued).

**Reported results**  
- No quantitative results reported in this segment.

**Limitations**  
- No limitations stated for the evaluation protocol in this segment.

**Exact quotes**  
- “The overall plausibility of the set of events corresponds to the factorization of the plausibility of each event’s occurrence given its causes.” (page 18 continued)  
- “The causal graph is composed of the following events: ({parent rank} -> {target rank}) {edge description}. {target rank}. {target description}. The value is {node current_value}.” (page 18 continued)

**Notes**  
- A references-only segment; no findings to infer.

**PAGE 19 (continued)**

- **Problem**: Oil price war severity and COVID-19 pandemic impact drive Bursa Malaysia downtrend; SMEs at risk from credit strain.
- **Method**: Counterfactual causal modeling using GPT-4o and LLaMA-3.1 to infer variable values and explain predictions.
- **Reported results**: GPT-4o predicts ~20% downtrend magnitude; FBM KLCI estimated ~1500.00 with mixed sector effects. Stephen Innes notes SMEs most at risk, oil/gas/airlines "in a bad way," cash as safe haven.
- **Limitations**: LLaMA-3.1 justifications "not always very explanative"; GPT-4o omits h0 (expected due to anticausal abduction).

**Quote 1**: "\"Unless governments actually get money physically into the hands that need it the most things can turn bad. This will put pressure on bank stocks due to credit line drawdown and an increase in defaults.\"" (Innes, p.19)

**Quote 2**: "\"But honestly with credit under duress, I think cash is the place to be. The only endgame in sight is when the world sees COVID-19 ends,\" he said." (Innes, p.19)

**PAGE 20**

- **Table 6**: GPT-4o and LLaMA-3.1 explanations for Table 4 variables; GPT-4o more precise/detailled; h0 excluded by GPT-4o (anticausal).
- **Tables 7–8**: Factual/counterfactual explanations; GPT-4o longer/more detailed; LLaMA-3.1 less explanative; scores/confidence correlated with outliers.

**Note**: References-only segment acknowledges methodology without invented findings.

*skipped: No deeper analysis of model explanation quality beyond stated observations; no evaluation of credit/downtrend magnitude correlation.*

# gendron2024counterfactual.20-21

## Problem
Malaysia's Borsa Malaysia index (FBM KLCI) performance during COVID-19, specifically oil & gas and airline sectors, influenced by travel restrictions, pandemic severity, oil price volatility, and political change.

## Method
Structural causal model with binary nodes for pandemic severity, oil price war severity, travel restrictions, coalition government change, SME support, and sector conditions. Explanations generated via GPT-4o on factual (FG) and counterfactual (CG) graphs.

## Reported Results
- With low pandemic severity and no end of pandemic: travel restrictions likely "none"; oil & gas/airlines condition "good".
- With no worldwide travel restrictions yesterday: oil & gas/airlines condition estimated "good".
- Counterfactual paths show key causal links: travel restrictions (false) → sector condition (bad) implicates oil price war and pandemic severity as alternative causes.
- Table 7: GPT-4o scores FG=0.85, CG1=0.5, CG2=0.3; explanations note pandemic impact on Bursa Malaysia, oil price war contribution, travel restrictions affecting sectors, coalition government affecting earnings, and lack of government support pressuring bank stocks.

## Limitations
- Outcome undeterminable without parent causes.
- Counterfactual inferences rely on absent parent nodes; real-world factors not in graph may explain sector conditions.
- Binary simplifications may omit nuance of severity scales and gradient policy responses.

## Exact Quotes
- "Given that the severity of the COVID-19 pandemic is low and the potential end of the pandemic is low and there is a potential end of the pandemic, it can be inferred that travel restrictions imposed worldwide would likely be none." (p.20 continued)
- "Since yesterday there were no worldwide travel restrictions, it is estimated that the condition of oil & gas and airlines sectors was good." (p.20 continued)

Attribution: all bullets tagged to preceding physical-page markers (p.20 continued, p.21).

**Gendron2024Counterfactual (pages 21–22)**

- **Problem**: Causal graph lacks explicit links between all influencing factors and the oil & gas sector condition, reducing overall confidence.
- **Method**: LLaMA3.1 explains graph scores (Table 8) by contrasting factual (FG) and counterfactual (CG) graph paths, scoring plausibility and confidence (Sc/Cf) per event.
- **Reported results**: 
  - FG score 0.7, confidence 0.8; CG1 score 0.6, confidence 0.7; CG2 score 0.0, confidence 0.8.
  - Plausibility hinges on COVID-19’s direct impact on recessionary trends; fiscal policy mitigated effects; oil price war influenced FBM KLCI but was not directly linked to recession.
  - COVID-19 (True) increased recession likelihood and impacted FBM KLCI; oil price war (value 80) influenced FBM KLCI indirectly; recessionary trends being False decreased FBM KLCI influence.
- **Limitations**: Event values missing for pandemic severity and oil price war; lack of values reduces confidence in overall plausibility; no explicit causal links for all factors.
- **Exact quote (p.21)**: “aph doesn’t explicitly link these other factors to the oil and gas sector condition, but they are plausible contributors.”
- **Exact quote (p.22)**: “The plausibility of the sequence of events is high due to the following reasons: COVID-19 pandemic (event 0) has a direct impact on recessionary trends (event 1).”

**Note**: A references-only segment requires a short note, not invented findings.