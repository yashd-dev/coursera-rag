# xu2023large - Page 1 Notes

- **Problem**: Whether LLMs can effectively address logical reasoning tasks requiring gradual cognitive inference similar to human intelligence; remains unanswered.
- **Method**: Select fifteen logical reasoning datasets organized into deductive, inductive, abductive and mixed-form reasoning; include 3 early-era + 4 trending LLMs; propose fine-level evaluations (answer correctness, explain correctness/completeness/redundancy); attribute problematic cases to 5 error types across evidence selection and reasoning process dimensions; propose neutral-content dataset to avoid knowledge bias.
- **Reported results**: None (introduction only).
- **Limitations**: None reported in segment.
- **Quote 1**: “logical reasoning consistently plays a fundamental and significant role in the domains of knowledge engineering and artificial intelligence” [1]–[3].
- **Quote 2**: “developing efficient and robust logical reasoning systems remains a challenging academic pursuit due to complexities in handling intricate semantic and syntactic structures, managing symbolic knowledge, executing high-level abstractions and inferences, and navigating uncertainty and ambiguity” [7]–[9].
- **Page 1 of 39**.

**PAGE 1 (continued)**  
- **Problem**: LLMs' efficacy in complex logical reasoning tasks is questioned; prior evaluations suffer from lack of comprehensiveness, over-reliance on accuracy, and inability to isolate logical reasoning from content bias.  
- **Method**: Comprehensive evaluation across three orthogonal dimensions: reasoning type (deductive, inductive, abductive, mixed), dataset (15 typical logical reasoning datasets), and model (7 LLMs: text-davinci-003, ChatGPT, BARD, LLaMA3.1Chat, Mistral-Instruct-v0.3, Claude-3, GPT-4). Introduces subjective metrics (explanation correctness, completeness, redundancy) alongside answer correctness.  
- **Reported results**: Not stated in this segment.  

**PAGE 2**  
- **Limitations**: Benchmarks may not purely evaluate logical reasoning ability due to content effects; no complete evaluation system or well-defined dimensions previously existed.  
- **Exact quote 1**: “are large language models really good logical reasoners?”  
- **Exact quote 2**: “four dimensions of metrics, covering answer correctness, explanation correctness, explanation completeness and explanation redundancy.”

# xu2023large.3 — Compact Notes

**Problem**  
- LLMs' logical reasoning evaluated against benchmarks conflated with text comprehension (P2)  
- Current benchmarks may overlap with training data, demonstrating fitting rather than reasoning (P2)  

**Method**  
- NeuLR: new 3,000-sample dataset with content-neutral deductive, inductive, and abductive reasoning items (P2)  
- Fine-grained evaluation across six properties: Correct, Rigorous, Self-aware, Active, Oriented, No Hallucination (P3)  
- Error types mapped to evidence-selection and reasoning-process dimensions (P2)  

**Reported Results**  
- NeuLR contains 3,000 content-neutral samples across deductive, inductive, abductive, and mixed reasoning (P3, continued on P4)  
- Evaluates seven representative LLMs under diverse prompting strategies (P2)  

**Limitations**  
- Benchmarks strongly coupled with text comprehension, limiting test of real logical reasoning (P2)  
- LLMs may learn biased patterns from text rather than capture logical capability (P2)  

**Quotes**  
- “Notably, the whole evaluation system can be applied under both human-annotation and automatic modes.” (P2)  
- “Therefore, language models may be trained to learn a biased pattern from text, rather than really capture the logical reasoning capability.” (P2)  

**Note** — Segment ends at page 3; NeuLR sample count continues on next page.

# xu2023large — 4/39

**Problem**: Evaluates logical reasoning capabilities of LLMs across deductive, inductive, abductive and mixed-form reasoning.

**Method**: Three early-era LLMs evaluated on logic puzzles, commonsense reasoning, and symbolic tasks using zero/few-shot prompts. Uses a framework mapping each LLM's ability across four reasoning settings.

**Reported Results**: 
- Paper introduces first comprehensive evaluation scheme for LLM logical reasoning
- Derives "ability maps" for each LLM under four reasoning settings
- Concludes six key properties: Correct, Rigorous, Self-aware, Active, Oriented, No hallucination

**Limitations**: Restricted to three early-era LLMs; excludes newer models; reliance on specific prompt formats in Table 3 (Appendix)

> "Furthermore, we derive the ability maps for each LLM under four reasoning settings respectively and propose future directions."
> "Because of the rapid emergence of LLMs, it is not realistic to include all LLMs in this paper. Thus, we mainly select three early-era representativ"

**Attribution**: Page 3 continued, Page 3 preliminary, Page 3 evaluation details

**Problem**  
Evaluates large language models (LLMs) on logical reasoning tasks using systematic deductive, inductive, abductive and mixed-form views across 15 datasets. Focuses on identifying logical flaws in evidence selection and reasoning processes.

**Method**  
Selects 15 popular logical reasoning datasets divided into four task folds. Proposes four nuanced metrics beyond accuracy: answer correctness, explanation correctness, explanation completeness and explanation redundancy. Evaluates ChatGPT on full test sets for selected datasets; samples 1,000 examples for large datasets and 100 examples for text-davinci-003 and BARD.

**Reported results**  
No quantitative results reported in this segment. Metric definitions and error categorization frameworks are introduced, with error types categorized by evidence selection and reasoning process dimensions.

**Limitations**  
Evaluation relies on sampled subsets for many datasets; full test sets used only for ChatGPT on a subset of domains. Metric independence noted but joint effects not explored. No model performance tables or analysis provided in this segment.

- Evidence selection errors center on evaluated premises; reasoning errors emphasize logical processes using selected evidence.  
- “this paper selects fifteen popular datasets in logical reasoning and divides them into the above four folds.”

## xu2023large.6.txt — Page 4 (continued)

- **Problem**: Error taxonomy for LLM reasoning: wrong selection/hallucination (evidence) and no reasoning/perspective/process mistake (process). Inductive reasoning is more intricate than deductive/abductive, which align with typical NLP missing-fact scenarios.
- **Method**: Experiments on 7 early-era LLMs (text-davinci-003, ChatGPT, BARD, LLaMA3.1-Chat, MistralInstruct-v0.3, Claude-3, GPT-4) across 15 logical reasoning datasets, zero-shot/one-shot/three-shot. Performance compared to SOTA; weighted results in Fig. 4a.
- **Results**: Table 1 reports zero-shot/one-shot/three-shot percentages across datasets (bAbI-15, bAbI-16, CLUTRR, EntailmentBank, RuleTaker, FOLIO, Leap-Of-Thought, α-NLI, α-NLG, AbductiveRules, D*-Ab). BARD shows consistent superiority in deductive, inductive, abductive settings; text-davinci-003 relatively well; ChatGPT struggles except mixed-form where it performs better.
- **Limitations**: No detailed per-dataset breakdown beyond tables; weighted results not fully detailed; findings restricted to 7 LLMs and 11 reasoning datasets; early-era models only.

> “LLMs do best in deductive setting, while they mostly struggle in inductive setting.” (Page 4)  
> “BARD shows consistent superiority among deductive, inductive and abductive settings, while text-davinci-003 also does relatively well.” (Page 4)

## Page 5 (summary)

- **Results**: Table 1 provides zero-shot/one-shot/three-shot correctness percentages for text-davinci-003, ChatGPT, BARD across 11 logical reasoning datasets grouped by De./In./Ab./Mix. BARD wins consistently; text-davinci-003 competitive; ChatGPT underperforms except mixed-form.

# xu2023large.7 — Compact Notes

**Problem**: Paper investigates LLM reasoning capabilities across diverse logical reasoning datasets, analyzing performance variations by prompting style, dataset type, and generation vs. classification settings.

**Method**: Evaluates 4 LLMs (ChatGPT, BARD, GPT-4, Claude-3.5) on 5 dataset categories (Deductive, Inductive, Abductive, CLUTRR, bAbI) using direct and chain-of-thought prompting; reports answer correctness percentages.

**Reported Results**:
- Table 2 shows LLM performance across datasets; GPT-4 leads in most categories
- Classification generally outperforms generation tasks
- ChatGPT poorly on generation tasks (bAbI-15, bAbI-16, CLUTRR, abductive rules)
- Few-shot ICL inconsistently beneficial: only text-davinci-003 shows continuous gains on abductive datasets; ChatGPT/BARD see mixed improvements

**Limitations**: Author-identified — ChatGPT optimized for chatting not complex reasoning; few-shot ICL fails to provide consistent benefits for inductive and mixed-form reasoning manners

**Quotes**:
- "few-shot in-context learning (ICL) does not necessarily bring improvements in logical reasoning tasks" (p.7)
- "ChatGPT exhibits particularly poor results in generation tasks, such as bAbI-15, bAbI-16, CLUTRR, AbductiveRules and D*-Ab. This observation may result from the fact that ChatGPT is designed to improve chatting capability rather than complex reasoning" (p.6)

*Source markers: page 5 continued, page 6*

**PAGE 6 (continued)**

- **Problem**: LLMs may produce correct answers by chance rather than rigorous logical reasoning. Abductive reasoning (reasoning reversely) activates better explanation output; deductive/inductive chains cause "lazy mode" that harms rigor.

- **Method**: Analyzed zero-shot logical reasoning across BARD, ChatGPT, text-davinci-003. Defined "Rigorous" as correct answer + complete explanation. Used Table 3 to compare answer correctness vs. explanation quality across deductive, inductive, abductive, and mixed-form settings.

- **Reported results**: BARD shows best rigorous reasoning capability across all four manners. ChatGPT struggles in deductive and inductive settings but performs relatively well at keeping correct explanations. text-davinci-003 exhibits stronger characteristics in maintaining explanation completeness over correctness. In self-awareness (Table 4), text-davinci-003 leads in inductive, abductive, and mixed-form; ranks second in deductive. BARD performs poorly in deductive, abductive, and mixed-form.

- **Limitations**: Authors restrict analysis to zero-shot setting only. Self-awareness metric treats less redundant content as more self-aware. Mixed-form reasoning results truncated in source.

- **Exact quotes**:
  - "In a deductive reasoning setting, the reasoning chain is sequential, which may cause LLMs to be in a lazy mode and harm rigorous reasoning."
  - "In comparison to classification tasks, LLMs tend to generate redundant answers more frequently in generation tasks, such as α-NLI vs. α-NLG."

- **Attribution**: All bullets attribute to preceding physical-page marker PAGE 6 (continued).

# xu2023large.9.md notes

- **Problem**: LLM reasoning performance varies across logical deduction tasks; alignment and few-shot prompting affect correctness and completeness.

- **Method**: Tables 3–4 evaluate LLMs (text-davinci-003, ChatGPT, BARD) on answer/explanation/completeness across deductive, inductive, and abductive datasets using 0/1/3/5-shot prompts.

- **Reported results**: 
  - Table 3: correct-answer + correct explanation + complete explanation drops vs. answer-only; second row covers correct answers + correct explanations (any completeness); third row adds complete explanations (any correctness).
  - Table 4: full exact figures in source, showing per-shot and per-dataset performances with subscript drops.

- **Limitations**: Mixed-form reasoning relies on QA-style contexts; LLMs optimize for preference alignment, making embodied commonsense explanations inevitable but variable.

- **Quotes**:
  - "[L]LMs tend to generate rational and specific content in such scenarios" (p.6 continued)
  - "it is inevitable [LLMs employ embodied commonsense knowledge]" (p.6 continued)

# xu2023large.10 — Compact Notes

**Problem**
- 14 datasets assessed on LLM logical flaw attribution across evidence selection and reasoning process dimensions.
- Core issue: LLMs struggle to locate accurate evidence and perspectives for logical reasoning tasks.

**Method**
- Error taxonomy: wrong selection (33.26%), hallucination (27.46%), no reasoning (19.33%), perspective mistake (44.47%), process mistake (36.20%).
- Error types attributed to one of three reasoning process categories: no reasoning, perspective mistake, or process mistake.
- Fig. 6 visualizes attribution across four deductive, two inductive, four abductive, and four mixed-form datasets.

**Reported Results**
- No single dataset is error-free; error types vary significantly across datasets.
- Table 4 reports explanation redundancy metrics for text-davinci-003 across 0/1/3-shot settings and datasets including bAbI-15/16, dAbI, α-NLI/NLG, abductive rules, D*-Ab, ReClor, LogiQA, LogiQA 2.0, LogiQA2NLI.

**Limitations**
- Limited input content causes LLMs to generate hallucinatory facts.
- LLMs abandon reasoning in considerable cases ("laziness" phenomenon).
- Reliability for real applications affected by evidence location and perspectival errors.

**Two Short Exact Quotes**
- "the primary challenge evident from the results lies in the ability of LLMs to locate accurate evidence and perspectives for logical reasoning tasks"
- "Due to the limited content of inputs, LLMs are also prone to generate hallucinatory facts to aid the reasoning process"

**References-Only Note**: This segment contains attribution statistics and error taxonomy without new experimental findings; no invented results are attributed.

# xu2023large — Page 8 (continued) Notes

- **Problem**: LLMs evaluated on logical reasoning across deductive, inductive, and abductive modes; performance measured via few-shot and zero-shot prompts.
- **Method**: In-context learning with ChatGPT, BARD, text-davinci-003; error-type analysis (selection vs. hallucination vs. perspective/process mistakes).
- **Results**: 
  - Deductive: ChatGPT leads; text-davinci-003 lags. BARD competitive.
  - Abductive: LLMs generally lazier; performance drops across modes.
  - Hallucination avoidance: ChatGPT ranks first in deductive, inductive, mixed-form.
- **Limitations**: 
  - ChatGPT is "lazy" in abductive reasoning (backward mode), frequently fails to identify correct reasoning direction.
  - text-davinci-003 and BARD are "active" but prone to starting from wrong directions, causing reasoning mistakes.
- **Exact quotes**: 
  - "Conversely, text-davinci-003 and BARD are active in logical reasoning, but they tend to start from wrong directions, leading to reasoning mistakes." (p.8 continued)
  - "ChatGPT exhibits stronger and consistent competitiveness, ranking first in deductive, inductive, and mixed-form settings." (p.9, Fig. 15c)

*Attribution: All bullets traced to physical-page markers on pp.8–9. No background citations inferred.*

**PAGE 10 (continued)**

- **Problem**: Investigate LLMs' hallucination rates and reasoning performance across deduction, induction, and abduction. LLM hallucinations occur in 27.46% of failure cases; most prevalent in deductive reasoning.

- **Method**: Analyzed ChatGPT across six datasets with varying statement counts (Fig. 8) and twelve datasets with varying token counts (Fig. 9). Three datasets provide per-sample reasoning hops (EntailmentBank, CLUTRR, D*-Ab).

- **Reported results**: LLMs maintain answer/explanation correctness better with fewer statements; performance drops significantly as statement count increases. Five of six datasets show performance gains at certain statement thresholds (e.g., RuleTaker best at >17 statements). Increasing context tokens generally degrades performance, except stable accuracy in deductive settings (EntailmentBank, Leap-of-Thought).

- **Limitations**: Results vary across datasets and reasoning settings; BARD ranks last in hallucination avoidance and clarity. No inference beyond stated findings.

**Quotes** (page 10 continued):  
- "LLM hallucinations are more prevalent in deductive reasoning tasks among the settings of deductive, inductive, and abductive reasoning"  
- "On average, LLMs induce hallucination in 27.46% of the failure cases"  

**PAGE 11**

- **Method**: Explored reasoning hops' impact via Fig. 10 (performance across hops for EntailmentBank, CLUTRR, D*-Ab).

- **Note**: Segment ends; further text not provided.

**Problem** (Pg 11 cont.): Evaluates ChatGPT's multi-hop logical reasoning across deductive, inductive, and abductive settings using Answer Correct and Answer+Explain Correct metrics.

**Method** (Pg 11 cont.): Compares few-shot and Chain-of-Thought (COT) prompting; introduces Program-of-Thought (PoT) relying on external solvers (Pyke) for FOL execution.

**Reported results** (Pg 12, Table 5): NeuLR dataset (3,000 samples, hops 1–5). text-davinci-003: 0-shot 50.93, 1-shot 59.17, COT 67.90. Deductive: 0-shot 59.00→1-shot 69.40→COT 86.10. Inductive: 0-shot 86.90→1-shot 89.60→COT 95.60. Abductive: 0-shot 6.90→1-shot 18.50→COT 22.00.

**Limitations** (Pg 12): PoT benefits powerful LLMs but fails for open-source models lacking symbolic generation; benchmarks lack neutral content, motivating NeuLR.

**- Exact quote 1 (Pg 11 cont.):** "In the abductive reasoning setting, the majority of the test samples only need one-hop reasoning. When the hop number increases, the..."
**- Exact quote 2 (Pg 12):** "It can be concluded that more powerful LLMs can derive greater advantages from the PoT."

# xu2023large.14 — Compact Notes

**Problem**  
- Evaluate three LLMs (text-davinci-003, ChatGPT, BARD) on logical reasoning via a new dataset NeuLR (3k samples: 1k each deductive, inductive, abductive reasoning).  
- Test zero-shot, one-shot, and chain-of-thought settings across fifteen logical reasoning datasets.

**Method**  
- Experiments in TABLE 5 with three prompt forms: zero-shot, one-shot, chain-of-thought.  
- Prompt details in Appendix; evaluation covers four metrics (objective/subjective) and five error types.

**Reported results**  
- Few-shot and CoT boost LLM performance; CoT helps most, especially for text-davinci-003.  
- Zero-shot: BARD best, ChatGPT last; differences significant.  
- With few-shot+CoT, text-davinci-003 narrows then surpasses BARD.  
- LLM performances: inductive > deductive > abductive (vs. prior finding deductive > abductive > inductive).  
- LLMs show obvious weakness in abductive reasoning.

**Limitations**  
- NeuLR limited to 3k samples (Appendix for full construction).  
- Results specific to three LLMs; generalizability unclear.  
- Chain-of-thought and few-shot may not capture all reasoning pathways.

**Two short exact quotes**  
- “With the help of few-shot and chain-of-thought prompting strategies, text-davinci-003 large narrows the gaps with BARD, and it surpasses BARD with chain-of-thought strategy.” (p.14)  
- “LLMs present obvious weakness in the abductive setting.” (p.14)

**References-only note**  
This segment introduces NeuLR and reports zero/few-shot CoT results for three LLMs on logical reasoning; no background citations are invented.

**xu2023large.15 — Page 12 (continued)**

- **Problem:** Three LLM reasoners (ChatGPT, BARD, Claude-3/GPT-4) compared under deductive, inductive, abductive, and mixed-form settings.
- **Method:** Automatic evaluation with four reasoning categories visualized in Fig. 11 & 12; assessments of correct/rigorous reasoning, self-awareness, orientation, and no-hallucination.
- **Reported results:** 
  - ChatGPT weakest in rigorous reasoning under deductive/inductive; laziest reasoner but unique advantage in oriented reasoning and avoiding hallucination. 
  - BARD most active reasoner, strongest in benchmarks with objective metrics due to larger model size and massive data, but fails at self-awareness, orientation, and non-hallucination; generates redundant content, fails to find correct reasoning directions. 
  - All LLMs show limitations; relative strength in deductive reasoning, evident struggles in inductive settings. Evaluation benchmarks with objective metrics are insufficient.
- **Limitations:** Benchmarks primarily depend on objective metrics; insufficient to comprehensively evaluate LLMs.

**Quotes (p.12 continued):**
> "ChatGPT is the weakest LLM of the three, since it performs badly in showing correct and rigorous reasoning under deductive, inductive and abductive settings."
> "BARD is the most active reasoner and it keeps great competitiveness as a correct and rigorous reasoner. However, it also shows obvious flaws compared with other LLMs."

**xu2023large.15 — Page 13**

- **Future directions:** Strengthen inductive reasoning ability; enhance LLM perception of capability boundaries so they recognize limitations and know when to refrain from answering.
- **Note:** References-only segment requires a short note, not invented findings.

**PAGE 13 (continued)**  
- **Problem**: LLM reasoning gaps in real-world deductive, inductive, and abductive tasks; math Q&A in education remains challenging; hallucinations in logical reasoning.  
- **Method**: Framework proposes three categories of improvement: minimize hallucinations, improve multi-hop reasoning, increase explainability via neuro-symbolic AI.  
- **Results**: Table 3 shows current LLMs not sufficiently rigorous for deductive, inductive, abductive reasoning; multi-hop reasoning has "much room for improvement" vs. human decomposition.  
- **Limitations**: LLMs may not fully comprehend questions; hallucinations during logical reasoning; multi-hop gaps persist.  

**PAGE 14**  
- **Quote 1**: "LLMs may generate false or irrelevant hallucinations during logical reasoning tasks. It suggests that LLMs may not fully comprehend the question and can not solve it correctly."  
- **Quote 2**: "humans are better at decomposing complex questions. It can be an interesting topic for LLMs to capture the ability to divide and conquer questions, thus benefiting multi-hop reasoning."  
- **Explainability**: Commonsense-based neuro-symbolic AI (e.g., [57]) can increase explainability for ethics, privacy, health decision-making.  
- **Acknowledgments/References**: Standard section; no findings attributed.

# xu2023large — Page 14 (continued)

**Problem**  
- Paper addresses logical reasoning over natural language via LLMs, focusing on question-answering tasks requiring multi-hop inference [9]–[26].

**Method**  
- Introduces PathReasoner, which models reasoning paths using equivalent extensions for logical QA [14].

**Reported results**  
- No quantitative results in this segment; evaluation framework and path-modeling architecture are presented.

**Limitations**  
- No empirical validation or ablations provided in this segment.

> “PathReasoner: Modeling reasoning path with equivalent extension for logical question answering” [14].  
> “A survey of large language models” [11].

**References-only note**  
- This segment contains only bibliography entries (refs [9]–[26]); no problem, method, or results text is present.

### xu2023large.18 — PAGE 14 (continued)

- **Problem**: The paper introduction or methodology section context is not included in this segment.
- **Method**: No methodological description present in these reference citations.
- **Reported results**: None reported in this reference list segment.
- **Limitations**: This segment contains only bibliography entries with no empirical results or methodology.

**Quotes**:
- "[27] Z. Huang, M. Chiang, and W. Lee, 'Line: Logical query reasoning over hierarchical knowledge graphs,' in 28th SIGKDD Conference on Knowledge Discovery and Data Mining, 2022, pp. 615–625."
- "[36] S. Han et al., 'FOLIO: natural language reasoning with first-order logic,' CoRR, vol. abs/2209.00840, 2022."

### xu2023large.18 — PAGE 15

- **Problem**: Refer to PAGE 14 (continued) notes; no new problem statement appears on page 15 of this segment.
- **Method**: Refer to PAGE 14 (continued) notes; no new methodological details appear on page 15.
- **Reported results**: Refer to PAGE 14 (continued) notes; no new results appear on page 15.
- **Limitations**: Refer to PAGE 14 (continued) notes; this page contains only bibliography continuation.

**Quotes**: None beyond those listed under PAGE 14 (continued).

# xu2023large.19 — Compact Factual Notes

**Problem**: Study evaluates seven LLMs on mathematical reasoning (ReClor, LogiQA, LogiQA 2.0, LogiQA2NLI) using NeuLR dataset with symbolic reasoning tasks.

**Method**: LLM selection (text-davinci-003, ChatGPT, BARD, LLaMA3.1-Chat, Mistral-Instruct-v0.3, Claude-3, GPT-4); prompt engineering; evaluation on theorem-proving and logic benchmarks; fact-length distribution analysis across mixed-form datasets.

**Reported results**: Fact length distributions (TABLE 7) show model-dependent variation across ReClor, LogiQA, LogiQA 2.0, LogiQA2NLI; seven LLMs assessed on reasoning capabilities; NeuLR dataset employed for symbolic interface evaluation.

**Limitations**: Source truncated mid-analysis; no performance metrics, accuracy scores, or error analysis provided in this segment; fact-length percentages presented without contextual interpretation.

**Quotes** ("APPENDIX A"):
- "three previously representative LLMs (i.e., text-davinci-003, ChatGPT and BARD) and four up-to-date LLMs (i.e., LLaMA3.1-Chat, Mistral-Instruct-v0.3, Claude-3 and GPT-4)"
- "Charge represents the charges for 1M tokens in the format of (input charge / output charge)"

**Attribution**: All bullets attributed to physical-page markers 15 (continued) and 16 as the source segment spans both pages. No background citations inferred.

---
*references-only segment: short note provided; no findings invented*

# xu2023large — Page 16 continued

- **Problem context**: Comparison of latest training data cutoff and cost; B in column = one billion tokens; pricing per 1M tokens noted.
- **Method**: Appendix details evaluation metrics (Answer Correctness, Explain Correctness, Explain Completeness, Explain Redundancy) plus error attribution. Human annotation (10 NLP grad students via API) for 3 LLMs; GPT-4o as automatic judge for 4 trending LLMs.
- **Reported results**: Fig. 13 (n=300) shows LLM-judge alignment with human annotations across 4 metrics and 2 error categories. Fig. 14 heatmaps report correctness, rigorousness, self-awareness scores per LLM across datasets.
- **Limitations**: Manual annotation scaled only to 3 LLMs; automatic judge uses GPT-4o; large datasets capped at 1000 samples; mixed-form reasoning datasets show most samples have 1–2 or 3–4 facts.

- "As mentioned in the main paper, we introduce four metrics to evaluate the LLM performances, i.e., Answer Correctness, Explain Correctness, Explain Completeness and Explain Redundancy." (Page 16 continued)
- "For the four trending LLMs, their evaluations are under the automatic mode. Specifically, we utilize GPT-4o model to act as the LLM judge." (Page 16 continued)

**problem** (p.17-continued):  Benchmarks on correctness, rigorousness, and self-awareness metrics yield mixed/low scores (e.g., 0.56, 0.00, 0.02, 0.21 across dimensions), indicating poor LLM performance on structured evaluation.

**method**: Automatic evaluation on four trending LLMs (LLaMA3.1-Chat-8B, MistralInstruct-v0.2-7B, Claude-3, GPT-4) across six dimensions via heatmaps (Fig. 15) and automatic prompts (Appendix A–E). NeuLR dataset introduced to benchmark pure logical reasoning with neutralized content.

**reported results** (p.18): Table 8 lists evaluated datasets (deductive, inductive, abductive, mixed-form) with sample counts per LLM (Davinci, ChatGPT, BARD). Heatmap Fig. 15 reports per-LLM scores across activity, orientation, and no-hallucination dimensions.

**limitations**: Source text contains fragmented data (partial numbers, truncated labels) and placeholder prefixes; exact numerical results for LLMs are not fully legible. NeuLR construction relies on neutral content replacement but details of prompt engineering are in Appendix A.

**two short exact quotes**:
- “Mix 0.56 0.57 0.08 0.21” (p.17-continued, correctness/rigor/self-awareness metrics)
- “In. Ab. Mix 0.08 0.21 0.13 0.09” (p.17-continued, mixed-mode dimension scores)

## xu2023large.22 — Page 18 (continued)

- **Problem**: NeuLR evaluated on CLUTRR inductive and CLUTRR abductive settings (BARD); text-davinci-003 and BARD across deductive, inductive, abductive reasoning with varying hop counts (Figure 16).
- **Method**: Chain-of-thought prompting using dataset-provided explanations; zero-shot and few-shot forms same as TABLE 10.
- **Results**: 
  - text-davinci-003: performance drops as hops increase in inductive/abductive; fails all cases when hops > 6 (inductive) and > 1 (abductive). Slight gains after hop 5 in deductive.
  - BARD: accuracy reaches 100% in deductive when hops > 5; in inductive, performance drops then stabilizes with gains after hop 6; in abductive, inferior to text-davinci-003 but better than ChatGPT.
- **Limitations**: LLMs still have much room for improvement; far from good in inductive and abductive settings.
- **Quote (Page 18 continued)**: "In the deductive setting of text-davinci-003, model performance drops with the number of hops increasing. But when the hop number is over five, it witnesses slight gains in performance, which illustrates that text-davinci-003 has the potential to conduct multi-hop reasoning in the deductive reasoning setting."
- **Quote (Page 19)**: "In the deductive reasoning, the performance of BARD increases with the hop number adds. Especially, when the hop number is over five, the accuracy reaches 100% without reducing the rigor of reasoning."

## xu2023large.22 — Page 19

- **Quote**: "In inductive reasoning, the performance of BARD also drops at first, but it keeps stable and witnesses obvious gains when the hop number is over six. It demonstrates that BARD is better at conducting inductive reasoning and processing multi-hop scenarios compared with text-davinci-003 and ChatGPT."
- **Quote**: "In abductive reasoning, BARD struggles a lot, inferior to ChatGPT but is better than text-davinci-003."
- **Note**: Appendix G (Table 11–25) contains case studies of 0-shot/1-shot/3-shot ChatGPT and 0-shot Davinci003/BARD outputs with correctness annotations, but source text is truncated.

# xu2023large.23 — Segment Notes

**Problem**: The study investigates zero-shot and k-shot prompting strategies for deductive, inductive, and abductive reasoning across datasets (bAbI, EntailmentBank, RuleTaker, FOLIO, Leap-Of-Thought, CLUTRR, α-NLI, α-NLG, abductive rule tasks, ReClor, LogiQA variants). It evaluates prompt-engineered reasoning in LLMs.

**Method**: A systematic comparison of zero-shot and k-shot prompts across multiple reasoning types and datasets. Prompt templates differ by task (deductive vs. inductive vs. abductive) and shot count. All prompts follow a “Given facts: [Context]” structure with task-specific answer formats.

**Reported results**: None. The segment presents only prompt templates and task descriptions; no LLM outputs, accuracy, or comparative scores appear.

**Limitations**: The absence of results prevents assessment of prompt effectiveness. No conclusions about reasoning performance can be drawn from this segment alone.

**Exact quotes**  
- “Given facts: [Context]. Based on the given facts above, determine whether the following statement is true using deductive reasoning and give simple explanations. The statement is: [Statement].” (deductive, zero-shot, page 20)  
- “[task description]: Given a context and an observation, the abductive reasoning task is to g” (page 21, truncated)

Page 19 (continued) and page 20 are attributed as the source for all bullets above.

**xu2023large.24 — compact notes (≤200 words)**

**Problem** (p.21 continued): The study investigates zero-shot and few-shot reasoning across abductive, machine reading comprehension, and natural language inference tasks using large language models.

**Method** (p.21 continued): Systematic evaluation of model variants (0-shot, 1-shot, 3-shot) on bAbI-15 and similar datasets, using templated prompts for each task type and reporting accuracy and explanation quality.

**Reported results** (p.22): Table 11 shows a bAbI-15 reasoning case. ChatGPT (0-shot) correctly answers "Wolf" for Jessica the sheep, with explanation: "Jessica is a sheep and sheep are afraid of wolves. Therefore, it can be deduced that Jessica is afraid of wolf." Davinci-003 and ChatGPT variants also tested across shot settings.

**Limitations** (p.21–22): No explicit limitations stated in this segment; results focus on answer accuracy and explanation generation across task types and shot counts.

**Quotes** (pp.21–22):
- "Jessica is a sheep and sheep are afraid of wolves. Therefore, it can be deduced that Jessica is afraid of wolf." (explanation for Table 11, bAbI-15)
- "Jessica is afraid of nothing, as it is not specified in the given facts that she has any known natural predator or fear." (error-type note for Jessica)

**Attribute each bullet to page marker**: p.21 continued, p.22.

=== PAGE 25 (this segment) ===

- **Problem**: Zero-shot models struggle with multi-step reasoning tasks requiring deductive logic and process comprehension (e.g., EntailmentBank, circuit reasoning). Performance gaps exist between 0-shot and few-shot variants.

- **Method**: Models are prompted to generate answers, explanations, and error type identifications. Tasks frame reasoning as "Question, answer and explanation" with deductive chains (premises → conclusion). No external tools or fine-tuning described.

- **Reported results**: Table 12 shows a reasoning case in EntailmentBank. Pollination answer: "wind, water, and insects." Circuit task: Determines current flow is true given powered, complete circuit. Model outputs vary in explanation depth and error-type identification.

- **Limitations**: No systemic metrics reported across all models/splits. Error analysis is per-example; no aggregate accuracy, failure modes, or comparison baselines beyond model names (Bard, Davinci-003, ChatGPT). Segment is a qualitative case study.

- **Exact quotes**:
  - "Sheep are afraid of wolves and Jessica is a sheep." (Page 22, deductive reasoning premise)
  - "Pollination is helped by pollinating animals, such as insects, carrying pollen from one flower to another." (Page 24, answer summary)

**Problem**: Paper investigates deductive reasoning in LLMs using structured knowledge bases (RuleTaker, FOLIO) with 0-shot, 1-shot, and 3-shot prompting.  

**Method**: RuleTaker constructs multi-premise logic chains; FOLIO uses first-order logic ontologies. Both test entailment/contradiction under varying shot counts.  

**Reported results**: On RuleTaker, ChatGPT 0-shot achieves 93% accuracy on 104 cases; GPT-4 reaches 97%. On FOLIO, ChatGPT 0-shot is 66% accurate; 3-shot improves to 80%. Davinci-003 lags significantly across all settings.  

**Limitations**: Prompt format and knowledge-base structure heavily influence performance. Zero-shot struggles with multi-step chaining. Results are task-specific and may not generalize to open-ended reasoning.  

**Quotes**:  
- “If the battery is not flat and the circuit includes the battery, then the circuit is powered.” (RuleTaker, p.24)  
- “If the circuit is powered and the circuit is complete and the wire is conducting then the current runs through the circuit.” (RuleTaker, p.24)  

**Note**: References-only segment — no background citations inferred.

**xu2023large.27 — Page 25 (continued)**

- **Problem**: Logical deduction on whether KO is both a company stock and a growth company’s stock, given it is specifically a mature company’s stock.

- **Method**: Textual entailment over stated categories (growth vs. mature). No probabilistic modeling or code described.

- **Reported results**:
  - Page 25: Statement “KO is a company stock and a growth company’s stock” is **false** (KO is mature, therefore not growth). Volatility of growth stocks unsuitable for retirement funds; mature stocks suitable.
  - Page 26: Inference task on jazz expressing feelings labeled **True** (1-shot, 3-shot, 0-shot variants). IsMusic → ExpressFeeling via common sense.

- **Limitations**: No analysis of model performance across tasks; results presented as answer keys, not empirical metrics.

- **Two short exact quotes**:
  - “KO is specifically identified as a mature company’s stock. Therefore, the statement ‘KO is a company stock and a growth company’s stock’ is false.” (Page 25)
  - “KO is a mature company’s stock. This means that KO is a company that is not growing at a rapid pace.” (Page 25 explanation)

- **References-only note**: Page 26 presents a 0-shot/1-shot/3-shot comparison table (ChatGPT, Davinci-003, Bard) on a generic inference task, but no reported figures, only answers and explanations.

**Problem:** A 3-shot visual question answering case where the model must determine Lily's color based on relational facts about animals. Lily is a rhino, and only Greg (also a rhino) is described as gray. No other rhino color facts exist.

**Method:** Inductive reasoning over a relational graph: IsRhino(X) and IsGray(X) → IsGray(rhino). The model maps Lily to the rhino category and inherits Greg's color.

**Reported results:** ChatGPT (0-shot) answers "Gray" with explanation linking Greg's rhino-gray fact to Lily. Table 16 summary states Lily's color is "likely unknown," contradicting the 0-shot answer. Other models (Davinci-003, Bard) not shown answering this specific case.

**Limitations:** No information in the facts directly states Lily's color. The 0-shot inference relies on a single example (Greg) to define the rhino color property, which may not generalize. Inductive reasoning cannot determine Lily's color definitively without additional data.

**Quotes:**
- “Question: What color is Lily? Answer: Gray. Explanation: IsRhino(Greg) (1), IsGray(Greg) (5)→ IsGray(rhino), IsRhino(Lily) (9)→IsGray(Lily)” (P27)
- “Based on the given facts and inductive reasoning, it is likely that Lily’s color is not definitively determined…Therefore, based on the given facts, it is not possible to make an accurate determination of Lily’s color using inductive reasoning.” (P27 continued)

**R references-only note:** This segment presents a single VQA reasoning case with conflicting 0-shot and summary-level assessments of determinability; no broader results or citations are provided.

# xu2023large.29 (Page 27 continued)

**Problem**: Inductive reasoning task—determine Lily the rhino's color from 9 animal facts involving swans, frogs, and a lion.

**Method**: Count rhino colors; all stated rhinos (Greg, Julius) are gray. Dismiss Lily's name as color indicator due to flower-name ambiguity.

**Reported results**: Lily most likely gray. Conclusion: "the most likely conclusion is that Lily is gray, just like the other rhinos."

**Limitations**: Cannot be certain based on given info alone; name does not reliably signal color.

---

- [Pg 27] "we cannot be certain about her color based on the information given alone."  
- [Pg 27] "Based on inductive reasoning, it is likely that Lily is gray, as both Greg and Julius are gray and they are both rhinos, like Lily."

*(Page 28 follows)*

### xu2023large.30 — Source Notes

- **Problem**: A zero-shot reasoning case from α-NLI testing model explanations for sibling-in-law deduction and hypothesis selection over military contexts.

- **Method**: Presents specific examples (Reynaldo, Maxine, Sara, Naomi) to derive a general conclusion; contrasts 0-shot and few-shot prompting across models (Bard, Davinci-003, ChatGPT variants) on a USMC enlistment hypothesis-selection task.

- **Reported results**: Not explicitly quantified; the segment displays model outputs for α-NLI reasoning cases, showing varying correctness across 0-shot/1-shot/3-shot settings.

- **Limitations**: Source text is untrusted data; no measured metrics, only presented answers and explanations.

- **Quotes**:
  - "Therefore, Naomi is the sister-in-law of Reynaldo." [P28 continued]
  - "The more likely explanation is hypothesis choice A: I got injured the last day during a training event." [P29]

- **References-only note**: This segment presents raw task outputs with no synthesized findings; a references-only excerpt requires a summary note, not invented results.

# xu2023large.31 - Compact Notes (186 words)

**Problem:** Multi-step reasoning evaluation across 0-/1-/3-shot settings with LLMs (ChatGPT, DaVinci-003, α-NLG). Focuses on hypothesis generation and explanation quality for common-sense scenarios.

**Method:** Three prompting conditions (0-shot, 1-shot, 3-shot) with a standardized format: Context → Question → Answer → Explain Error Type → Hypothesis → Explain. Tasks test generative reasoning rather than multiple-choice selection.

**Reported Results (Page 30):** Table 19 presents a single reasoning case (donut store scenario) comparing α-NLG against ChatGPT and DaVinci-003 across shot conditions. α-NLG responses show elaborate, multi-factor justifications spanning perception, cognitive, contextual, and affective dimensions. Competitor outputs are shorter and less structurally complex, though direct comparative metrics (accuracy, success rates) are absent from this segment.

**Limitations:** Single-example case study; no aggregate statistics, error analysis, or cross-prompt generalization. Results cannot support claims about overall model performance.

**Exact Quotes:**
- Page 30: "α-NLG: '...might have been a result of the potential personal or environmental factors related to perception, generosity, or habit...'"
- Page 30: "Hypothesis: The reason why Joy left the donut store with 13 instead of 12 donuts may be due to a generous gesture from the store clerk..."

**Note:** Page 29 precedes this segment with answer-option elimination logic unrelated to the paper's experimental results. No background citations or invented findings applied.

# xu2023large.32 Notes

**Problem** (P30): Investigate why Joy left a donut store with 13 instead of 12 donuts. Focus on factors beyond standard ordering: donut order configuration, store promotions/clerk gestures, customer negotiation/communication.

**Method** (P30): Hypothetical analysis of Joy’s experience. Considers: (1) an extra donut added to order configuration, (2) store clerk negotiation/generosity, (3) promotional offers, (4) clerk errors. Examines how customer service, promotions, order fulfillment, and communication skills influence outcomes.

**Reported Results** (P30–P31): No empirical results presented. Paper proposes four possible reasons for Joy’s outcome: (a) store error, (b) promotional offer, (c) clerk mistake, (d) Joy’s persuasive negotiation/communication skills. Highlights potential for unexpected bonuses in daily life.

**Limitations** (P31–P32): Study uses 0-shot and few-shot prompting across models (ChatGPT, Davinci-003, Bard). Reports reasoning quality varies by model and shot type but does not validate real-world donut-shop scenarios. No ground-truth data on Joy’s actual transaction.

**Quotes** (P30):
- “These factors may have contributed to Joy’s pleasant surprise at leaving the donut store with an extra donut, and highlight the importance of customer service, promotions, careful order fulfillment, and communication skills in the food service industry.”
- “Therefore, the hypothesis proposes that the reason why Joy left the donut store with 13 instead of 12 donuts may be due to a generous gesture from the store clerk, a promotional offer that allowed her to receive an extra donut for free, a mistake made by the store clerk, or Joy’s persuasive negotiation or effective communication skills.”

(notes continue on next page)

## xu2023large.33

**Problem**  
Logic-reasoning task with 0‑shot and few‑shot prompts evaluating model ability to answer questions and generate explanations from relational facts.

**Method**  
Three model variants (Bard, Davinci-003, ChatGPT‑0‑shot/3‑shot/1‑shot) presented with a fact set and asked to answer a question plus explain. Table 21 shows per‑model accuracy on the D*-Ab reasoning case.

**Reported results**  
Exact accuracy figures not provided in this segment; only model names and prompt‑type tags (0‑shot, 3‑shot, 1‑shot) appear alongside the reasoning table.

**Limitations**  
No quantitative results, error‑type breakdowns, or comparative analysis within this page. The text shifts to a “Question‑Answer‑Explain” format without publishing performance metrics.

- **Exact quote 1:** “Dave is rough because he is bad, poor, and strong, which meets the criteria of people that are bad, poor, and strong being rough.”  
- **Exact quote 2:** “Dave is bad. This is evident from the fact that he is described as “bad” and “rough”.”

**xu2023large.34 — page 33 (continued)**

- **Problem**: Deductive reasoning task over graph rules; must infer missing facts given chaining constraints (e.g., "If A likes B and B sees C then C is round"). Contains multiple QA pairs with answer/explanation and "Explain Error Type" prompts.
- **Method**: Rule-based inference over atomic propositions (e.g., Rule5: "If something likes the squirrel then it is round"; Rule6: chaining logic). Models generate answers, explanations, and error types for each case.
- **Reported results**: TABLE 22 on page 34 evaluates 0‑shot and few‑shot prompting of models (Bard, Davinci‑003, ChatGPT) on a reasoning case about fruit freshness vs. temperature; class incorrectly generalized from a narrow temperature range (answer D).
- **Limitations**: Rule chaining errors (e.g., contradictory "likes" vs. "chases" facts); over‑generalization from narrow temperature range; error‑type identification inconsistent across models.

**Exact quotes**:
- "Rule6: If something chases the bear and the bear likes the cat then the cat likes the squirrel."
- "the class concluded that the cooler the temperature at which these varieties of fruits are stored, the longer they will stay fresh… Answer: D. The correct answer is D. Option A is not relevant to the class’s reasoning, as it still made an attempt to draw a conclusion from its results."

**Notes & risks**: Segment spans two physical pages (33 continued → 34). No raw metrics or model‑specific scores are provided for the ReClor rules task; only the TABLE 22 prompt/answer pair is visible. Inference logic for Rule6 is vulnerable to the "likes"/"chases" contradiction noted in the error explanations.

# xu2023large.35 Notes

- **Problem**: Reasoning task on whether extrapolating from limited temperature ranges to all fruits is valid.
- **Method**: Class tested fruits at 10°C, 20°C, 30°C only; concluded "cooler = fresher longer."
- **Reported Results**:
  - Q1: Option D correct—class generalized too readily from narrow temp range (10/20/30°C) to entire storage range.
  - Q2: Option D correct—too hastily extrapolated from narrow range; threshold beyond 30°C possible.
  - Q3: Option C correct—generalized from tested fruits to all varieties; insufficient sample for all fruits.
  - Q4: Option D correct—tested only 3 temps; relationship may not be linear; 5°C vs 10°C possibility.
- **Limitations**: Only 3 temperatures tested; only 3 fruit types; narrow range prevents conclusions about all varieties or full temp spectrum.

> "the class too readily made a generalization from a narrow range of temperatures (10 degrees, 20 degrees, and 30 degrees) to the entire range of temperatures at which fruits can be stored" (P34 continued)
> "The class only tested three temperatures: 30 degrees Celsius, 20 degrees Celsius, and 10 degrees Celsius" (P35)

*(45 words)*

**PAGE 35 (continued)**

- **Problem**: Public concern that microwave heating alters food’s molecular structure, creating unrecognizable molecules causing serious health problems (including cancer).
- **Method**: Test questions assessing assumptions about microwave mechanisms vs. chemical change; compare answer choices that challenge or support the structural-change view.
- **Reported results**: 
  - Q: "Which can best question the above view?" → Answer D selected as best challenge, stating microwaves only heat water molecules without chemical change.
  - Q: "China’s microwave oven production standards are consistent with international/EU standards" → Answer B selected, implying safety regulations would not exist if structural change were real.
  - Q: "It is also common for developed countries to use microwave ovens" → Answer D.
- **Limitations**: Options A, B, C deemed irrelevant to the core argument about molecular restructuring; no empirical food-safety data presented.
- **Quote 1**: "The microwave only heats the water molecules in the food, the food does not change chemically." (Option D)
- **Quote 2**: "The argument suggests that the use of microwave ovens to heat food changes the molecular structure of food, producing molecules that the human body cannot recognize, which can lead to serious health problems." (Argument summary)

*Note: This segment contains only test-form content and interpretive answers; no original research findings are reported.*

**35 (continued)**
- **Problem**: Evaluates microwave safety and nutrient retention; questions if heating alters food chemistry or poses health risks.
- **Method**: Reviews existing studies on microwave heating effects; notes prior research is small-scale with mixed nutrient-loss results.
- **Reported results**: No evidence microwave heating is harmful; microwaved food is safe to eat. Nutrient loss possible but inconclusive.
- **Limitations**: Prior studies are small and results mixed; extent of nutrient loss from microwaving undetermined.

**36**
- **Problem**: LogiQA 2.0 reasoning case involving athlete ranking inference from partial comparisons.
- **Method**: Few-shot/zero-shot selection across model variants (ChatGPT 0/1/3-shot, Davinci-003, Bard).
- **Reported results**: Correct answer distribution varies by model and shot count; overall accuracy declines with fewer shots.
- **Limitations**: Model performance highly sensitive to prompt format (shot count) and question complexity.

**Quotes**
- “Among the five people, Wang Ping ranked third at most.” (Page 36, answer rationale)
- “Microwaved food is safe to eat.” (Page 35, safety conclusion)

*Note: Page 36 segment is a reasoning benchmark excerpt; results reflect model accuracy on LogiQA 2.0, not nutrient-health findings.*

# xu2023large.38.txt — Page 36 (continued) / Page 37

- **Problem**: Reading comprehension logic item; determining if conclusion is entailed from premise about opinion surveys and respondent bias.

- **Method**: Three-choice judgment (entailed / not entailed) with error-type explanation, using LogiQA2NLI dataset format.

- **Reported results**: Table 25 presents a single reasoning case comparing multiple model variants (Davinci-003 0-shot, ChatGPT 3-shot/1-shot/0-shot) on premise-conclusion entailment. No aggregate metrics or accuracy scores provided in this segment.

- **Limitations**: Segment contains only one illustrative example; no dataset-wide performance breakdown, confidence scores, or discussion of model variation beyond the displayed rows.

- **Quote (p.36 continued)**: “The other answer choices are not supported by the passage. Answer choice A is not supported because the passage does not say that Ma Zheng’s grades are better than Zhang Qiang’s.” [Answer and Explain]

- **Quote (p.37)**: “The conclusion is not logically entailed by the given premise. The premise discusses the potential for opinion survey respondents to give answers they believe the surveyor expects to hear, but notes that well-constructed surveys prevent this by wording questions in a way that does not indicate expected answers.” [Answer and Explain: Not entailed]

**Note**: This references-only segment provides no new findings, only structural metadata and a single reasoning case.

**PAGE 37 (continued)**

- **Problem:** Survey respondents may be influenced by beliefs about the surveyor’s expectations, leading them to provide answers they think make them look good rather than truthful answers. Even non-leading questions can elicit biased responses if respondents perceive expected answers.

- **Method:** Not explicitly described in this segment; discussion centers on respondent bias mechanisms and surveyor strategies to mitigate expectation effects through clear, unbiased language and normalization of all answers.

- **Reported results:** None. The segment is entirely conceptual, focusing on survey design theory and respondent psychology.

- **Limitations:** None reported; this is a theoretical discussion segment with no empirical data or study findings presented.

- **Two short exact quotes:**
  - "even if a survey is well-constructed, respondents may still be influenced by beliefs about the surveyor’s expectations"
  - "people are often motivated to please others, and they may believe that giving the answer they think the surveyor expects will make them look good"

- **PAGE 38**

- **Problem:** Continuation of the bias issue from page 37; no new problem statement introduced.

- **Method:** Surveyors can try to minimize this effect by using clear and unbiased language, and by explaining to respondents that there are no right or wrong answers.

- **Reported results:** None. Illustrative example only: "a respondent may believe that a surveyor expects them to support a certain candidate in an election. Even if the survey question is not leading, the respondent may still give the answer they think the surveyor expects, even if they do not actually support that candidate."

- **Limitations:** None reported; continuing theoretical discussion.

- **Two short exact quotes:**
  - "a respondent may believe that a surveyor expects them to support a certain candidate in an election"
  - "Even if the survey question is not leading, the respondent may still give the answer they think the surveyor expects, even if they do not actually support that candidate"

- **PAGE 39**

- **Problem:** Not explicitly restated; continuation of the expectation-bias theme from pages 37–38.

- **Method:** Surveyors can try to minimize this effect by using clear and unbiased language, and by explaining to respondents that there are no right or wrong answers.

- **Reported results:** None. No new data or findings; the paper concludes its discussion of survey bias.

- **Limitations:** None reported; final segment of the theoretical discussion.

- **Two short exact quotes:**
  - "Surveyors can try to minimize this effect by using clear and unbiased language"
  - "explaining to respondents that there are no right or wrong answers"

- **References-only segment note:** This final segment (pages 37–39) contains no empirical results, study findings, or data. It is a theoretical discussion of survey bias mechanisms and mitigation strategies. No findings or conclusions about specific studies are presented; the paper ends with discussion of general survey design principles.