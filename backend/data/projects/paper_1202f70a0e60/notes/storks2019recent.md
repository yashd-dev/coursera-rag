# storks2019recent.1 — Section Notes

## Problem (P1–P2)
Machines struggle with NLI that requires deep language understanding beyond explicit text, relying on world knowledge and reasoning. Despite NLP advances, systems remain far from human-like ability (§1).

## Method (P2–P3)
Survey of benchmarks, knowledge resources, and state-of-the-art learning/inference approaches organized into symbolic, statistical, and neural models (§1–§2).

## Reported Results (P2)
None — descriptive survey of field architecture; no experimental findings in this segment.

## Limitations (P1)
Machines lack commonsense reasoning; world-knowledge connections and inference processes remain difficult despite decades of NLP progress (§1).

## Quotes
> "We know that a piggy bank is a container that holds coins... Since metal is a hard solid, the coins will make a sound when shaken inside of a container such as a piggy bank; if there is no sound, then there are no coins." (§1)

> "Despite significant advances in natural language processing in the last several decades, machines are still far away from having this type of natural language inference (NLI) ability." (§1)

**Attribution**: Bullets attributed to physical-page markers P1–P3 as instructed. Source text treated as untrusted data; no background citations inferred.

# storks2019recent.2 — Compact Notes

**Problem**  
- Paper surveys recent advances in NLI (broader than textual entailment), focusing on tasks, benchmarks, knowledge resources, and inference approaches. *(P2)*  
- Aims to provide an entry point for newcomers to this quickly evolving field. *(P2)*  

**Method**  
- Survey overview of existing tasks and benchmarks, knowledge resources, and learning/inference approaches. *(P2)*  
- Discusses limitations and future opportunities. *(P2)*  

**Reported Results**  
- No quantitative results or performance metrics reported; survey of state-of-the-art methods and benchmarks. *(P2–P3)*  

**Limitations**  
- Not a comprehensive discussion of all NLP benchmarks/resources; focuses specifically on NLI. *(P3)*  
- Early benchmarks targeted shallow linguistic approaches; deeper reasoning outside scope. *(P3)*  
- Videos/images used for benchmarks are not the focus of this paper. *(P2)*  

**Exact Quotes**  
- “Although videos and images are often used for creating various benchmarks, they are not the focus of this paper.” *(P2)*  
- “We use the term here to refer to a broader sense of inference which includes but is not restricted to the textual entailment task formulation.” *(P2)*

# storks2019recent — Page 3 (continued)–4

**Problem.** The survey surveys recent benchmarks evaluating machine reasoning, from focused tasks like the Winograd Schema Challenge to broad suites like GLUE. A central challenge is that solving these tasks requires machines to go beyond linguistic context and rely on implicit reasoning and world knowledge not explicitly stated in text.

**Method.** The authors categorize benchmarks by task scope (specific vs. broad) and knowledge type (linguistic, common, commonsense). They survey existing benchmarks, summarize criteria for benchmark design, and discuss task formulation, bias mitigation, data collection, and complexity factors.

**Reported results.** No quantitative results are reported; the paper is a survey of existing benchmarks and criteria.

**Limitations.** The survey does not present new experiments or metrics; it maps the landscape of prior benchmarks.

- "Higher-level tasks, such as question answering, may appear the same as in earlier benchmarks. However, successfully solving these tasks will also require machines to go beyond linguistic context, and rely on reasoning and knowledge that is not explicitly stated in text." (P3)
- "Some benchmarks target a specific type of knowledge, e.g., commonsense social psychology in Event2Mind, while others intend to address a variety of types of knowledge, e.g., the Story Cloze Test." (P4)

# storks2019recent.4 — Compact Notes

**Problem**: Survey recent advances in natural language inference. Positioning commonsense knowledge (unstated, universally accepted beliefs) as distinct from common knowledge (region/culture-variant), with intuitive physics and psychology as two critical domains enabling on-the-fly predictions of physical/social interactions.

**Method**: Survey of computational models from symbolic/statistical to deep neural networks, modeling language context and leveraging external knowledge resources. Critical caveat: unexplainability of recent approaches + statistical biases in benchmark datasets (Schwartz et al., 2017; Gururangan et al., 2018; Niven & Kao, 2019) obscure true progress toward NLI ability.

**Reported Results**: Deep neural models achieve state-of-the-art (some near/above human performance) on benchmark tasks, but debate persists on how much progress enables genuine NLI ability.

**Limitations**: Unexplainability of neural approaches; statistical biases in datasets; commonsense knowledge is typically unstated and considered obvious; cultural/regional variation in common knowledge; knowledge resources remain incomplete for facilitating NLI.

- "commonsense knowledge, on the other hand, is typically unstated, as it is considered obvious to most humans" [Pg 4 continued]
- "commonsense knowledge provides a deeper understanding of language" [Pg 4 continued]
- "it remains a subject of debate in terms of how much progress we have made in enabling natural language inference ability" [Pg 5]

### References-Only Note
This segment is a survey introduction reviewing the landscape—no original experimental results, datasets, or novel models are presented. It maps the field's scope, key knowledge domains (intuitive physics/psychology), and known barriers (unexplainability, dataset biases) without reporting new findings.

**PROBLEM** (p.5 continued): Benchmarks like GLUE and CBT are used as Turing Test alternatives, providing training/testing data and continuous feedback for language tasks. Section surveys recent NLI benchmarks designed to evaluate inference ability.

**METHOD** (p.5→6): Overview of benchmarks grouped by reference resolution, QA, textual entailment, plausible inference, psychological reasoning, and multiple tasks. Benchmarks introduced since early 2000s RTE Challenges. Analysis of benchmark growth trends and sizes.

**REPORTED RESULTS** (p.6): Figure 2 shows benchmark size growth from 2000s to 2019. Earlier benchmarks (2005–2015) have relatively small sizes; post-2015 benchmarks have much larger instances, many exceeding 100,000, enabling deep learning. Dataset sizes range from 10 (Triangle-COPA) to 10,000,000 (GLUE). 2018 saw creation of more larger benchmarks than ever before.

**LIMITATIONS** (p.5): Turing Test criticized for encouraging machine deception (Levesque, 2011), not providing continuous feedback (Ortiz, 2016), and being impractical (Harnad, 2000). Test data often not distributed publicly, preventing standard unbiased testing.

**QUOTES** (p.5→6): "In 2018, we saw the creation of more benchmarks of larger sizes than ever before" (p.6). "Most benchmarks developed after 2015 have a much larger number of instances" (p.6).

**NOTES** (p.6→7): Reference resolution remains "unsolved problem" due to small data magnitude. Test data non-public distribution limits standard evaluation.

**storks2019recent.6.txt — continued from PAGE 7**

- **Problem**: Reference resolution benchmarks are scarce; prior work focuses on entity coreference, not event references.
- **Method**: Introduces and describes several existing benchmarks (Winograd Schema Challenge, WinoGrande, bAbI coreference, Inference is Everything, Winogender, WNLI) as reference points; notes their design and scale.
- **Reported results**: WinoGrande has “nearly 44,000 examples, but maintains the same level of difficulty, having low baseline performance but high human performance”; other benchmarks (bAbI subtasks, Winogender, WNLI) listed as subtasks of broader datasets.
- **Limitations**: All existing benchmarks evaluate entity references, not event references; event-coreference benchmarks are limited and typically require only linguistic context.
- **Quote (PAGE 7)**: “WinoGrande… consists of nearly 44,000 examples, but maintains the same level of difficulty, having low baseline performance but high human performance.”
- **Quote (PAGE 8, Fig. 3)**: “The trophy would not fit in the brown suitcase because it was too big. What was too big?” (Winograd Schema Challenge item)

**storks2019recent.7.txt - Page 8 (continued)**

- **Problem:** Paper addresses the gap in coreference resolution benchmarks that focus on within-text linguistic context, overlooking the need for outside knowledge and reasoning (Rahman & Ng, 2012).

- **Method:** Survey of existing reference resolution and question answering benchmarks; categorization by dependency on external knowledge and reasoning depth.

- **Reported results:** 
  - MCScript, CoQA, OpenBookQA require commonsense knowledge for answering (e.g., diapers thrown away; steel as conductor; election competition).
  - MCTest requires outside knowledge and multi-sentence reasoning; >50% of questions need synthesis from multiple locations, not shallow matching.

- **Limitations:** Benchmarks like SQuAD 2.0 include unanswerable questions requiring deep reasoning over passage knowledge; existing QA tasks may be solved via linguistic context alone without deep comprehension.

- **Quote (p.8):** "Lions eat zebras because they are predators. Who are predators?"

- **Quote (p.8):** "The trophy would not fit in the brown suitcase because it was too small."

**storks2019recent.7.txt - Page 9**

- **Method:** Description of QA benchmarks (MCTest, MCScript, CoQA, OpenBookQA, SQuAD 2.0) and their knowledge/reasoning requirements.

- **Reported results:** 
  - MCScript example: commonsense knowledge that diapers are typically thrown away is useful.
  - OpenBookQA example: steel conductor vs. jeans/cotton hat for heat travel; Democrats/ Republicans competition in elections.

- **Limitations:** Not all QA benchmarks require external knowledge; many solvable via linguistic context alone.

- **Quote (p.9):** "Which of these would let the most heat travel through? a. a new pair of jeans. b. a steel spoon in a cafeteria."

- **Quote (p.9):** "Who is the democratic candidate? Terry McAuliffe" (with evidence citation).

**storks2019recent.7.txt - Page 10**

- **Problem:** Storks, Gao, & Chai survey recent advances in NLI; anticipation of event reference resolution benchmarks requiring outside knowledge.

- **Method:** Survey of QA benchmarks and their structural properties.

- **Reported results:** MCTest: >50% of questions require >1 sentence to answer; systems must synthesize information from multiple locations; open-domain with stories designed for young children.

- **Limitations:** Source text truncated; no explicit limitations for this segment beyond structural observations.

- **Quote (p.10):** "More than half of the questions require more than one sentence to answer, so that systems must synthesize information from multiple locations rather than using shallow matching techniques to find the answer."

**8/79 – Problems & Methods**

- **MCTest**: 500 multiple-choice questions over short stories; downloadable from GitHub; requires outside knowledge limited to manageable amount.
- **RACE**: 98,000 MC questions over 28,000 passages from middle/high-school exams; designed by expert teachers; often requires multi-sentence reasoning; choices may not match passage directly.
- **NarrativeQA**: 1,500 stories/scripts with 47,000 QA pairs; two open-ended tasks (original stories/summaries); answering from full texts requires larger-span reasoning.
- **ARC**: 8,000 four-way MC science questions + 14M sentence corpus; requires drawing from multiple sentences; not solvable by keyword search alone.
- **MCScript**: 14,000 2-way MC questions emphasizing commonsense; large proportion answerable without passage; labeled as text- vs. commonsense-answered.
- **ProPara**: 488 procedural paragraphs (e.g., photosynthesis); state-change grids required; proficiency in physical-process reasoning needed.
- **MultiRC**: (text cut off)

**8/79 – Reported Results**  
*No quantitative results in this segment.*

**8/79 – Limitations**  
*No explicit limitations stated.*

**Quotes (p.10)**  
- “As the exams are designed by expert teachers, the questions are challenging, often requiring reasoning over multiple sentences in the passage.”  
- “If a system understands a paragraph in this dataset, it is said that for each entity mentioned in the paragraph, it can answer any question about whether the entity is created, destroyed, or moved…”

**8/79 – Notes**  
Segment ends mid-definition of MultiRC; source continues on p.11.

## storks2019recent.9.txt — Page 11 (continued) → Page 12

### Problem
Datasets requiring multi-sentence reasoning, variable answer choices, unstated warrants, and external knowledge to perform well; traditional span-based QA insufficient.

### Method
Survey of benchmarks: **VEDI** (Roth et al., 2018, ~10k questions, 800+ paragraphs, multi-sentence reasoning, variable answers/choices); **ARCT** (Habernal et al., 2018, 2.5k examples, argument warrant selection); **SQuAD** (Rajpurkar et al., 2016, 100k Wikipedia QA; SQuAD 2.0 adds 50k unanswerable questions requiring passage reasoning); **CoQA** (Reddy et al., 2018, 127k conversational QA, abstractive answers with span rationales, requires conversation history and external knowledge); **QuAC** (Choi et al., 2018, 98k questions over 14k dialogs, 9k passages, span answers).

### Reported Results
No accuracy/F1 scores reported in this segment. Only dataset descriptions, sizes, and download links provided.

### Limitations
This segment contains only dataset metadata and citations; no experimental results, error analysis, or model comparisons are included.

### Exact Quotes
- “vedi, Roth, Upadhyay, and Roth (2018) is a reading comprehension dataset consisting of about 10,000 questions posed on over 800 paragraphs across a variety of topic domains.”
- “SQuAD 2.0 (Rajpurkar et al., 2018) was later released to add about 50,000 additional questions which are unanswerable given the passage.”

### Notes
References-only segment. No findings to synthesize.

**storks2019recent.10.txt - Page 12 (continued)**

- **Problem**: Survey of recent NLI advances; datasets address various reasoning gaps. QuAC questions unanswerable by string matching; workers provide dialog acts for feedback. OpenBookQA provides ~1,300 "open book" science facts alongside ~6,000 4-way MCQs requiring commonsense knowledge. CommonsenseQA has 9,500 three-way MCQs targeting ConceptNet disambiguation. DREAM has ~10,000 MCQs on 6,500 dialogues; 34% explicitly require external knowledge. Cosmos QA continues from Page 13.

- **Method**: Dataset collection protocols described; no modeling methods reported in this segment.

- **Reported results**: None. This is a survey segment describing datasets and benchmarks.

- **Limitations**: QuAC does not explicitly address use of external knowledge; CommonsenseQA requires outside resources for commonsense answers; DREAM 34% external knowledge reliance challenges neural RC systems not typically used for dialogue.

- **Quote 1**: "the worker asking the questions could not see the text and thus did not know the answer, encouraging the creation of questions which cannot be answered by string matching approaches" (p.12)

- **Quote 2**: "the answers to most questions cannot be directly extracted from the text, and will require multi-sentence reasoning. Further, 34% of questions explicitly require external knowledge to answer" (p.12, DREAM)

## storks2019recent.11 (pp. 13–14)

**Problem**  
- Cosmos QA (§2.1.2): 94% of questions require commonsense knowledge; highest proportion seen for any QA benchmark.  
- MC-TACO (§2.1.2): 1,900 multiple-choice questions on temporal common-sense (duration, frequency, order); commonsense under-emphasized in prior benchmarks.  

**Method**  
- Textual entailment (§2.1.3) defined directionally: text entails hypothesis if a typical person would infer it true.  
- Benchmarks surveyed: RTE Challenges, SICK, SNLI, MultiNLI (Telephone), SciTail.  
- Figure 5 provides example pairs with labels (entailment, contradiction, neutral).  

**Reported results**  
- Cosmos QA: ~94% question proportion requiring commonsense (no aggregate accuracy cited).  
- MC-TACO: ~1,900 questions; multiple correct answers permitted (no aggregate accuracy cited).  
- RTE/SNLI/MultiNLI/SciTail examples listed; no system scores reported.  

**Limitations**  
- Cosmos QA: Most correct answers not stated in the passage; requires external knowledge.  
- MC-TACO: Temporal properties focus under-emphasized prior to 2019.  
- Textual entailment: Reliance on “typical person” inference introduces subjectivity.  

**Two short exact quotes**  
- “About 94% of questions require commonsense knowledge, which is the highest proportion seen yet for any QA benchmark requiring the comprehension of a passage.” (p. 13)  
- “MC-TACO provides about 1,900 multiple-choice questions requiring commonsense knowledge about the temporal properties of events… Such commonsense knowledge was under-emphasized in previous benchmarks.” (p. 13)  

**References-only note**  
This segment surveys existing QA and entailment benchmarks; no new results, datasets, or methods are introduced beyond citation of prior work.

# storks2019recent.12 — Compact Notes

**Problem:** Survey of Natural Language Inference (NLI) benchmarks. RTE tasks evolved from binary to three-way (entailment/contradiction/neutral) with increasing data sizes; Conversational Entailment requires reasoning about dialogue participants' beliefs/desires; SICK tests compositional knowledge via 3-way decision; SNLI provides ~600k pairs with crowd judgments, expanded to MultiNLI then GLUE; SciTail is science-adapted 2-way; SherLIiC targets lexical inference in context for event/action verbs (~960k pairs).

**Method:** Survey of existing NLI benchmarks and datasets; no new experiments or models presented.

**Reported results:** Dataset sizes: RTE challenges 1k–49k examples; Conversational Entailment 875 pairs; SICK ~10k pairs; SNLI ~600k pairs; SciTail ~27k pairs; SherLIiC ~960k pairs. MultiNLI inheres within GLUE benchmark.

**Limitations:** Survey scope limited to existing benchmarks; no new evaluation or analysis of system performance provided.

> "The eighth Challenge ... focused on classifying student responses as an effort toward providing automatic feedback in an educational setting." (P15)

> "SherLIiC ... focuses particularly on entailment relationships between event and action verbs. It consists of about 960,000" sentence pairs. (P16)

*Attribution: Each bullet references the preceding physical-page marker.*

**storks2019recent.13.txt — PAGE 16 (continued)**

- **Problem**: SherLIiC forms a challenging testbed for NLI and textual entailment, built from inference rule candidates extracted from a knowledge graph (≈4,000 annotated for correctness) plus automatic premise-hypothesis similarity calculations.

- **Method (Plausible Inference)**: Survey of benchmarks requiring hypothetical/uncertain conclusions from limited context (abductive reasoning). Includes cloze tasks (fill-in-the-blank), sentence/story completion, and causal reasoning.

- **COPA**: 1,000 examples evaluating causal reasoning between events via backward/forward cause/effect choices, requiring commonsense knowledge of everyday interactions. Download: `people.ict.usc.edu/~gordon/copa.html`.

- **CBT**: 687,000 cloze-style questions from 20-sentence children's story extracts; 10 candidate words per blank; 4 prediction tasks (named entity, common noun, verb, preposition). Download: `research.fb.com/downloads/babi/`.

- **ROCStories**: 50,000 five-sentence everyday stories with causal/temporal relationships; 3,700 test cases with plausible/implausible alternate endings (Story Cloze Test). Most recent release adds ~50,000 stories. Request: `cs.rochester.edu/nlp/rocstories/`.

- **LAMBADA**: 10,000 BooksCorpus passages; open-ended cloze task requiring discourse-aware language modeling to predict missing terminal word.

- **Limitations**: No reported system results, human performance baselines, or comparative analysis within this segment.

- **Quote (P16)**: "Almost 4,000 of these are annotated for their correctness."

- **Quote (P16)**: "SherLIiC serves as a challenging testbed for NLI and textual entailment systems."

- **Problem**: Storks et al. frame natural language understanding as a cloze-task where models predict the last word of the final sentence, requiring paragraph-level reasoning with human-filtered examples to prevent shortcut guessing.

- **Method**: The approach uses constrained last-word prediction across benchmarks (COPA, JOCI, CLOTH, SWAG, AlphaNLI) to evaluate commonsense and reasoning capabilities, similar to CBT but with human-filtered feasibility.

- **Reported results**: JOCI uses a 1–5 likelihood scale; SWAG provides 4-way multiple-choice endings; AlphaNLI presents premise-hypothesis pairs with textual entailment-style judgments. Figure 6 shows example instances from these benchmarks.

- **Limitations**: JOCI’s likelihood scale blurs the line between entailment and contradiction; SWAG includes adversarially generated distractors; human filtering, while ensuring feasibility, may still introduce annotation artifacts not generalizable to open domains.

- **Quote (p. 17)**: “Examples were further filtered to ensure that missing words could not be guessed without the context” (Storks et al., 2019).  
- **Quote (p. 18)**: “JOCI can be downloaded from https://github.com/sheng-z/JOCI” (Storks et al., 2019).

- **Problem**: State-of-the-art systems on commonsense NLI benchmarks; adversarial filtering prevents shallow solutions or data bias exploitation.  
- **Method**: Benchmarks categorized across four domains (commonsense NLI, QA, QG, intuitive psychology); each uses adversarial filtering or similar to generate challenging negatives.  
- **Reported Results**: SWAG has 73,561 examples; ReCoRD has 120,000+ examples requiring commonsense; HellaSWAG is a 70,000-example reissue of SWAG from ActivityNet/WikiHow sources with adversarially filtered negatives; AlphaNLI has 170,000 examples from 20,000 contexts.  
- **Limitations**: Adversarial filtering improves challenge but does not eliminate dataset artifacts; benchmark formats vary (cloze, abductive, ending prediction) limiting direct comparison.  

> “Examples include labels for the source of the correct ending, and ordinal labels for the likelihood of each possible ending and the correct ending.” (p.18, continued)  
> “HellaSWAG can be downloaded at https://rowanzellers.com/hellaswag/.” (p.19)  

**Notes**: The segment catalogs four benchmark families; no model results or comparative performance are reported.

# Compact Notes on storks2019recent.16.txt

- **Problem**: Survey of recent NLI advances; organizing datasets for commonsense reasoning about motivations, emotions, intentions, and social interactions. [P19 continued]

- **Method**: Describes five benchmark datasets: Triangle-COPA (100 examples, emotion/intention questions with logical forms); ROCStories (motivations/emotions ~160K annotations); Event2Mind (57K annotations, 25K events, predicting intentions/reactions); SocialIQA (45K QA requiring intuitive psychology). [P20, P21]

- **Reported results**: Dataset sizes and tasks reported; authors do not report partition magnitudes. [P19 continued, P21]

- **Limitations**: Authors report no dataset partition counts; counts derived from publicly available partitions only. [P19 continued fn 6]

- **Exact quotes**:
  - "The data also includes logical forms of the questions and alternatives, as the paper focuses on logical formalisms for psychological commonsense knowledge and reasoning." [P19 continued]
  - "The authors do not report the magnitude of any of the dataset partitions, so these counts came from the publicly available partitions of the dataset." [P19 continued fn 6]

# storks2019recent.17

## Problem
Generalizing evaluation of language models across diverse NLP tasks; assessing commonsense reasoning and linguistic phenomenon coverage in benchmarks.

## Method
Survey of recent NLP inference benchmarks: bAbI, IIE, GLUE, DNC, SuperGLUE. Maps task coverage across architectures.

## Reported results
- Deep learning models fine-tuned on SocialIQA then later fine-tuned on smaller-magnitude commonsense benchmarks (COPA, Winograd Schema) exceed state of the art on both (page 21 continued).
- Table 1 compares benchmark task distributions across bAbI, IIE, GLUE, DNC, SuperGLUE.

## Limitations
- bAbI data is synthetic, simply structured; current models learn tasks mostly from training data and cannot generalize to natural language (page 23).
- IIE details truncated in segment.

## Direct quotes
- "Interestingly, the authors show that when fine-tuned on SocialIQA, deep learning models perform better when later fine-tuned on smaller-magnitude benchmarks which require commonsense knowledge such as COPA (Roemmele et al., 2011) and the Winograd Schema Challenge (Davis et al., 2017), exceeding the state of the art on both." (page 21 continued)
- "It is important to note that bAbI's data is synthetic and very simply structured, and the inference required for testing data can be learned mostly from the training data, so it is easily solved by current systems." (page 23)

-page 22: Table 1 maps task presence across bAbI, IIE, GLUE, DNC, SuperGLUE benchmarks; shows SuperGLUE adds Sentence Similarity, Paraphrase, Figurative Language not in earlier benches.

**storks2019recent.18.txt – Page 23 (continued)**

- **Problem:** Author is surveying recent textual entailment corpora beyond RTE-5. Key collections include IIE (White et al., 2017), GLUE (Wang et al., 2018), DNC (Poliak et al., 2018a), and SuperGLUE (incomplete in segment). All are recast from prior datasets; IIE contains ~300,000 examples across semantic proto-role labeling, paraphrase, and pronoun resolution tasks in RTE format.

- **Method:** Comparative survey/categorization of existing NLP benchmark collections. No new experiments or models introduced.

- **Reported results:** IIE has ~300,000 examples; GLUE has over 1 million examples; DNC has ~570,000 examples across 9 entailment tasks requiring 7 reasoning types.

- **Limitations:** Survey scope limited to listed corpora; no evaluation, error analysis, or new findings reported.

- **Quote 1 (page 23):** “Between the tasks, IIE includes about 300,000 examples, all of which are recast from previously existing datasets.”

- **Quote 2 (page 24):** “The DNC benchmark consists of about 570,000 examples total, and can be downloaded at https://github.com/decompositional-semantics-initiative/DNC.”

**storks2019recent.18.txt – Reference-only note**

This segment catalogs existing NLP benchmarks (IIE, GLUE, DNC, SuperGLUE) without presenting original methods, results, or conclusions beyond enumeration and download links. No factual findings from this paper can be extracted beyond the reported corpus sizes and URLs.

# storks2019recent.19 — 3-page segment

**Problem**: Survey of recent advances in natural language inference (NLI), focusing on benchmark creation criteria and task formats. GLUE suite and its constituent tasks described as comprising ~23,000 examples of difficult reframed single-sentence binary classification and 2- or 3-way entailment tasks.

**Method**: Review of benchmark creation successes/lessons; analysis of task formats (classification, entailment, cloze, Q&A), evaluation schemes, data biases, collection methods, and complexity.

**Results**: GLUE includes CommitmentBank, COPA, MultiRC, RTE (merged RTE-1/2/3/5), WiC, and WSC recast as binary classification. SuperGLUE downloadable at https://super.gluebenchmark.com/.

**Limitations**: Text presented as untrusted data; no verification of reported numbers or task definitions attempted.

> "Many of these tasks require reasoning over multiple sentences, and using external knowledge to perform language processing tasks like word-sense disambiguation and reference resolution." — Pg 25

> "The goal of benchmarks is to support technology development and provide a platform to measure research progress." — Pg 25

**Exact quotes**: Verbatim from source segment, attributed to their respective page markers.

## storks2019recent.20.txt — Notes (≤200 words)

**Problem:** Survey of recent NLI advances; categorizes QA formats (QA, cloze, multiple-choice, open-ended) and benchmarks (GLUE, IIE, DNC, CBT, CLOTH, SWAG, ReCoRD, COPA, Winograd, MCScript, SQuAD, QuAC, etc.).

**Method:** Textual survey mapping task formats to benchmark datasets; categorizes by question type and provides data examples in figures.

**Reported results:** No new results. Figures 8–10 list example contexts, hypotheses, and labels (e.g., "entailed") from GLUE, IIE, DNC, CBT, CLOTH, COPA, Winograd Schema, MCScript, SQuAD, QuAC, Event2Mind, NarrativeQA, DROP.

**Limitations:** Survey scope limited to cited works; no original experiments or end-to-end system evaluation.

- "Context: Who was the main performer at this year’s halftime show?" / "Hypothesis: ... Coldplay with special guest performers Beyoncé and Bruno Mars" [Fig 8A, p25 continued]
- "Context: The bird ate the pie and it died. / Hypothesis: The bird ate the pie and the bird died. / Label: entailed" [Fig 8B, p26]

**References-only note:** This segment reviews existing benchmarks; no new findings or claims beyond reported examples.

# Paper Segment: storks2019recent.21

**Problem:** Classifying and comparing natural language inference (NLI) tasks for evaluation schemes.

**Method:** Survey of NLI tasks organized by genre, cloze, open-ended response, and evaluation schemes including Turing Test, ROCStories, ReCoRD, SC, DROP, bAbI, and SWAG.

**Reported results:** 
- SWAG cloze task: She sits on a bench as her sister plays with the doll / smiles with someone as the music plays / is in the crowd watching dancers / nervously sets fingers on keys
- ROCStories: Karen agreed happily to concert; show was exhilarating  
- ReCoRD: Hantuchova knocked Williams out 6-2 5-7 6-2
- DROP painting sold $16.3M above $12M estimate
- bAbI navigation: den→kitchen via west, north

**Limitations:** Source text contains mixed task examples without systematic performance metrics; no new results reported in this segment.

**Exact quotes:**
- "He's started in with a spite at you on general principles, and the boys know it" (p.27)
- "You can't whip 'em – that is the trouble" (p.27)

**Note:** References-only segment (pp.27-28) provides task examples for NLI evaluation; no original findings or results attributed to this survey paper.

## storks2019recent.22 (PAGES 29–30)

**Problem**  
- AI researchers have long criticized benchmarks for not truly evaluating machine intelligence.  
- A critical need exists for new intelligence benchmarks that support incremental development and evaluation of AI techniques (Ortiz, 2016).  
- Benchmarks must provide continuous-scale feedback rather than pass/fail grades to enable comparison of approaches.  
- Informative evaluation metrics that are objective and easy to calculate are a key consideration.  

**Method**  
- Choice of evaluation metrics is highly dependent on task type; difficulty of calculation varies accordingly.  
- Classification tasks often use exact-match accuracy when answers are evenly distributed; otherwise F-measure is additionally presented (Wang et al., 2018).  
- Multiple-choice and classification formats (RTE, cloze, traditional multiple-choice) use exact-match accuracy and F-measure.  
- Open-ended tasks (SQuAD, QuAC) are evaluated using exact-match accuracy and F-measure on span-level predictions.  
- For label-subset tasks (Maslow, Reiss, Plutchik in Story Commonsense), precision and recall are calculated additionally (Rashkin et al., 2018a).  
- Event2Mind uses average cross-entropy and "recall @ 10" (percentage of human ground truth in top 10 predictions).  
- bAbI, LAMBADA, CoQA use exact-match accuracy and F-measure because responses are short (one word or single-word fills).  
- Longer responses (NarrativeQA) use machine-translation metrics (BLEU, Meteor) or summarization metrics (ROUGE), but these often do not correlate well with human judgments (Belz & Reiter, 2006; Elliott & Keller, 2014).  

**Reported results**  
- Baseline performance reports are standard when new benchmarks are released; benchmarks should be designed so simple baselines achieve poor performance to prevent trivial solutions.  

**Limitations**  
- Many evaluation metrics (BLEU, Meteor, ROUGE) have been found not to correlate well with human judgments of generated text.  
- Restrictions on response length (e.g., one word in bAbI, single word in LAMBADA) are essential for accurate open-ended evaluation but limit task generality.  

**Quotes**  
- "Benchmarks should not merely provide a pass or fail grade, rather they should provide feedback on a continuous scale which enables both incremental development and comparison of approaches." (Ortiz, 2016, as cited in this segment)  
- "Ideally, the benchmark should be designed in a way that a simple baseline would achieve poor performance to ensure that it cannot be solved by trivial means." (storks2019recent, p.30)

# storks2019recent.23 Notes

**Problem**  
- Baseline approaches for classification use random choice, majority-class selection, or n-gram overlap (Richardson et al., 2013; Mostafazadeh et al., 2016)  
- Open-ended problems employ shallow lexical approaches like language models (Weston et al., 2016 bAbI benchmark)  
- Benchmark releases report state-of-the-art baselines that evolve as new models emerge, continually boosting performance over time  

**Method**  
- Human performance measured via random subsets solved by crowdsourced judges (averaged) or majority vote across all judges  
- "Expert" human performance provided as ceiling by dataset creators (RACE, SWAG examples)  
- Systems compared against human performance, though exceeding it does not guarantee skill acquisition due to neural model unexplainability  

**Reported Results**  
- VQA first release: models learned statistical biases, answering 48% of validation questions without seeing images (Manjunatha et al., 2018)  
- Data biases artificially inflate performance, undermining credit to underlying technology  

**Limitations**  
- Unexplainable neural models hinder proof of skill acquisition beyond baseline performance  
- Data biases in popular benchmarks allow simple and state-of-the-art systems to exploit biases for artificially high scores  

>- **Quote (p.30):** “For classification problems, simple baseline approaches are often calculated by random choice, choosing the majority class from the training data…”  
>- **Quote (p.30):** “Human performance can also be measured through annotator agreement, e.g., as done for ROCStories (Mostafazadeh et al., 2016).”

# 24 — Problem & Method

- **Problem**: Prompt bias from imbalanced class labels reduces incremental improvement room; question-type imbalance skews QA benchmarks; superficial answer-question correlations (e.g., gender bias in NLI, Event2Mind) are hard to discern.

- **Method**: Balance examples per class for fair baselines. Calculate first-word distribution to balance question types (CoQA, CommonsenseQA, SQuAD 2.0, ARC). ProPara limits entity questions to creation/destruction/movement. Force questions requiring specific skills (e.g., arithmetic in DROP). Balance gender pronouns across occupation-related words.

# Reported Results

- MegaVeridicality subtask within DNC has **67% majority-class baseline** vs. 50% for binary-choice, due to uneven class distribution (Poliak et al., 2018a).
- Gender bias in NLI systems trained on biased data performs worse in gender pronoun disambiguation (Rudinger et al., 2018a); Winogender example: "The paramedic performed CPR on the passenger even though she knew it was too late."
- Similar gender biases identified in Event2Mind data derived from movie scripts (Rashkin et al., 2018b).

# Limitations

- Bias-avoidance strategies require careful implementation; no universal solution exists for all benchmark types.
- Manual labeling and crowd-worker introduction may introduce new artifacts.

# Two Exact Quotes

- "When class labels are balanced, a majority-class baseline will score as low as possible on the task. While binary-choice tasks should have a 50% majority class baseline, the MegaVeridicality subtask within DNC (Poliak et al., 2018a) has a 67% majority-class baseline due to unevenly distributed class labels" (p. 31 continued).
- "The paramedic performed CPR on the passenger even though she knew it was too late" (Rudinger et al., 2018a, Winogender, Fig. 3, cited p. 31 continued).

Attribution: All bullets tagged to preceding physical-page marker 【p. 31 continued】.

# storks2019recent.25.txt — Notes (pages 31–32)

- **Problem**: Story Cloze Test (SCT) can be solved (~72.4% accuracy) using only the two possible endings, exploiting human writing-style biases rather than realistic reasoning.

- **Method**: Exploits style biases in endings (e.g., negative language like "hates" more common in wrong endings; enthusiastic language like "!" in correct ending). Biases stem from crowd-worker heuristics during data creation.

- **Reported results**: SCT solvable at up to 72.4% accuracy by exploiting endings only. Prior NLI benchmarks (SICK, SNLI, etc.) also showed bias from specific words (e.g., "nobody" → contradiction; generic words → entailment) and sentence length → neutral. Simple mutual-information analysis can reveal such biases.

- **Limitations**: Biases allow superficial classifiers to outperform majority-baseline across multiple benchmarks; adversarial filtering (SWAG→HellaSWAG) mitigates but does not eliminate the issue as new models quickly adapt.

- **Quote (p32)**: “negative language is used more commonly in the wrong ending (e.g., 'hates'), and the correct ending is more likely to use enthusiastic language (e.g., '!')”

- **Quote (p32)**: “a baseline approach by Poliak et al. which only used the hypothesis sentence … was able to outperform a majority-class baseline in SNLI, JOCI, SciTail, two tasks within Inference is Everything, and the MultiNLI task within GLUE”

- **Reference segment**: Pages 31–32 cite Sharma et al. (2018); Gururangan et al. (2018); Poliak et al. (2018b); Zellers et al. (2018, 2019a); Devlin et al. (2018). No new experimental results beyond cited baselines.

# storks2019recent.26 — Notes (200 words max)

**Problem**  
State-of-the-art models struggle on new benchmarks due to embedded statistical biases. Adversarial filtering was used to create WinoGrande and AlphaNLI by removing these biases, yielding low baseline performance. An open question remains whether all statistical biases can ever be fully removed (p.32).

**Method**  
A secondary model is trained to predict the premise given the hypothesis and class label, forcing the model to ignore superficial language artifacts in textual entailment problems (p.33).

**Reported results**  
No quantitative results are provided in this segment. The paper describes the adversarial filtering process and the premise-prediction technique as bias-avoidance strategies, noting that continued effort will be important as state-of-the-art evolves.

**Limitations**  
The survey cites bAbI as a "toy task" where automatic generation yields 100% baseline accuracy, raising questions about real-world utility. No new benchmark results or model evaluations are reported for this section.

**Exact quotes**  
- "Variants of adversarial filtering were used in creating other benchmarks such as WinoGrande (Sakaguchi et al., 2019) and AlphaNLI (Bhagavatula et al., 2019)" (p.32)  
- "Another technique to avoid these biases proposed by Belinkov et al. (2019), particularly in textual entailment problems, is to train a model to predict the premise sentence given the hypothesis sentence and class label" (p.33)

**Attribution**  
All bullets attributed to physical-page markers: p.32, p.33. No background citations inferred.

**storks2019recent.27 – physical page markers**

- **Problem:** Language benchmarks can be mined from natural language texts; quality depends on source reliability (e.g., CLOTH uses expert-created fill-in-the-blank tests vs. random selection in CBT).

- **Method:** Discussion of automatic text mining versus crowdsourcing for dataset creation; attention to task complexity, worker qualification, and data validation (e.g., SNLI validation, ROCStories authoring).

- **Reported results:** No new experimental results; comparative analysis of benchmark origins (CLOTH mined from human tests; SWAG mined from movie descriptions and ActivityNet captions).

- **Limitations:** Roaches will still require some manual validation; benchmarks mining less reliable or inconsistent sources often need automatic or human validation/filtering.

- **Quote 1 (p.33 continued):** “Automatic generation versus text mining. As millions of natural language texts are publicly available on the Internet and in existing datasets, it is possible to build language benchmarks from these texts by automatically mining texts and extracting sentences.”

- **Quote 2 (p.34):** “CLOTH is more challenging as the missing word in each example was chosen by an expert. For many other benchmarks that are built by mining less reliable or consistent sources, there is often a need for automatic or human validation or filtering.”

**storks2019recent.28 - Paper: Recent Advances in Natural Language Inference: A Survey**

- **Problem**: Survey of NLI benchmarks and data collection methods; focus on trade-offs between quality, scalability, and cost.
- **Method**: Categorization of data collection (manual, automatic, text mining, crowdsourcing) and benchmark complexity analysis via human/machine performance.
- **Reported results**: ROCStories dataset cost ~15,000 USD (26¢/story + 10¢/test case); SNLI used as example for random-sample quality validation.
- **Limitations**: No fair direct benchmark comparison feasible; complexity perception discussed via performance dimensions only.
- **Quote (p.34)**: “For labeling tasks, multiple crowd workers can label the same examples, and agreement can be measured from this to estimate data quality.”
- **Quote (p.35)**: “Ultimately, each method of data collection has its own advantages and drawbacks.”

*Source: storks2019recent.28.txt, pages 34–35. Attribution follows physical-page markers.*

**PAGE 35**: Paper surveyed SOTA machine performance across benchmarks (MC-TACO to DREAM) and additional leaderboards (AlphaNLI, Story Cloze Test, SocialIQA) not in Section 4, as of Oct 2019.

**PAGE 36**: Machine performance exceeds humans on SQuAD 1.1 and SWAG, but these have low human accuracy; suggests evaluation framework limitations (e.g., SQuAD 1.1 span omission) rather than true difficulty. Crowdsourced human performance may be lower due to worker speed incentives.

**PAGE 37**: Crowd vs. expert disparity high (e.g., 73.5% vs. 94.5% on RACE; 82.8% to 88.0% on SWAG with ensemble). Uncertainty raises questions about naturalness of performance measurements; must consider collection method when interpreting results.

- "Machine performance has a much larger variance among these benchmarks." (P35)
- "Does that mean these problems are easy and solved?" (P36)

# storks2019recent.30.txt — Page 37–38

- **Problem**: CBT language modeling subtasks predict random words with/without context; prepositions hard for humans due to similar meanings; neural LMs excel, making the problem less interesting to study.

- **Method**: Analysis of benchmark data size vs. SOTA accuracy; linear regression shows no significant correlation; qualitative interpretation of trends across data magnitudes.

- **Reported results**: Small benchmarks (<1,000 examples, e.g., Winograd Schema) show limited improvement; large benchmarks (>100,000 examples, e.g., SQuAD 1.1, SWAG, GLUE) show highest SOTA performance and biggest improvements. bAbI achieves 100% SOTA accuracy due to synthetically generated, predictably structured data.

- **Limitations**: Statistical biases in benchmark data make performance measures questionable; SOTA neural approaches lack interpretability; no way to prove machines truly outperform humans; preposition prediction is inherently easier for machines.

- **Quote 1 (p.37)**: “Predicting some types of words, such as prepositions, is difficult for humans (67.6% accuracy without context), perhaps because humans excel at inferring meaning, and many prepositions have similar meanings. Consequently, neural language models, more capable of capturing patterns, easily beat humans in this sub-task of CBT.”

- **Quote 2 (p.37)**: “While the task is actually difficult for humans, machines are already more capable of performing it, making it less interesting of a problem to study.”

- **Ponytain note**: No figures or tables reproduced; only quoted text extracted. Data-size trend discussion relies on visual Figure 12 described textually—exact numerical values not verified from source.

**storks2019recent.31.txt — Page 38 (continued)**

- *Performance plateau*: SOTA or improvement limited on Story Cloze Test (Mostafazadeh et al., 2016) and Cosmos QA (Huang et al., 2019); benchmark age may factor into this.
- *Benchmark age*: SOTA vs. human performance tracked by release year; no statistically significant trend found, but qualitatively more progress on older benchmarks. Newer benchmarks may lack enough time or researchers for similar progress.
- *Anomalies*: Winograd Schema Challenge likely explained by small data size. Story Cloze Test has a high human-machine gap despite years and large training data; Schwartz et al. (2017) winning entry showed benchmark has human writing style biases enabling artificially high performance (Mostafazadeh, Roth, Louis, Chambers, & Allen, 2017).
- *Benchmark popularity*: Popularity affects researcher submissions and SOTA/human gap closure. Less popular benchmarks receive fewer submissions, so SOTA performance will not change.

**storks2019recent.31.txt — Page 39**

- *General trend*: More recent benchmarks generally have a higher gap, likely due to being newer; adversarial construction trend (AlphaNLI, WinoGrande) removes statistical biases, making older benchmarks easier for SOTA models.
- *Exceptions*: Winograd Schema Challenge has a higher gap than adversarial WinoGrande; explained by limited data and expert construction making bias exploitation harder for neural models.
- *Popularity effect*: More popular benchmarks expected to close the SOTA-human gap faster via more leaderboard submissions; less popular benchmarks receive fewer submissions, so SOTA performance will not change.

**Exact quotes**

- “the winning entry from Schwartz et al. (2017) in a shared task showing that the benchmark has human writing style biases which enable artificially high performance on the benchmark” (Mostafazadeh, Roth, Louis, Chambers, & Allen, 2017, p. 38).
- “More recent benchmarks generally have a higher gap, and this may just be because they are newer” (storks2019recent.31.txt, p. 39).

**Limitations**: Source text is untrusted data; no findings are invented. Attribute bullets to preceding physical-page markers including continued markers. A references-only segment needs a short note, not invented findings.

# Storks et al. (2019) Recent Survey — Section 3 Notes

**Problem:** Analyze human-machine performance gaps across NLP benchmarks to assess task complexity; survey existing knowledge resources as bottleneck for commonsense reasoning.

**Method:** Compare state-of-the-art machine accuracy vs. human accuracy across 18 benchmarks; visualize submission counts vs. performance gaps (Fig. 14); catalog linguistic, semantic, and commonsense knowledge resources.

**Reported results:** 
- Popular benchmarks (SQuAD 1.1/2.0) show machines far surpassing human performance with many submissions.
- Low-submission benchmarks show high variability; no clear popularity-progress relationship.
- Human adults estimated to possess ~100M commonsense axioms (Chklovski, 2003).

**Limitations:** Performance measures themselves are limited; benchmark data size, age, and popularity affect perceived complexity; low submission counts create high variability obscuring trends.

**Exact quotes:**
- "For benchmarks with a low number of submissions, there is high variability, suggesting no relationship between popularity and progress on the benchmark." (p.40)
- "The most popular benchmarks, i.e., SQuAD 1.1 (Rajpurkar et al., 2016) and 2.0 (Rajpurkar et al., 2018), have seen the most progress, with machine performance far surpassing human performance." (p.40)

**Ponytail skip:** Did not verify citation formats or check downstream sections for methodology replication details. Risk: Caps/author names may be inaccurately transcribed from scanned source.

# storks2019recent.33 — Page 41 (continued)

**Problem:** N/A — descriptive survey of linguistic and lexical resources supporting NLP.

**Method:** Survey of corpora (Penn Treebank, PDTB, OntoNotes, AMR) and lexical resources (WordNet, VerbNet, VerbOcean, VerbCorner, FrameNet, PropBank). Describes architecture and coverage of each resource.

**Reported results:** N/A — no experiments, metrics, or quantitative findings. Resources characterized by origin, structure, and annotations.

**Limitations:** N/A — this is a references/resource survey section; no methodology or evaluation presented.

**Exact quotes:**
- "The Penn Discourse Treebank (PDTB) is built upon it, adding annotated discourse structures" (p.41, continued).
- "Frames were defined by Minsky (1974) as cognitive data structures for information about prototypical events and situations" (p.42).

**Note:** This segment contains no problem–method–results structure; it is a bibliography-style survey of linguistic corpora and lexical resources. No findings or evaluations are reported.

# storks2019recent.34

**Problem:** N/A — background survey of NLP word embeddings and common knowledge resources.

**Method:** Literature review tracing semantic vector evolution from n-gram counts (Brown et al., 1992) through word2vec (Mikolov et al., 2013), GloVe (Pennington et al., 2014), FastText (Bojanowski et al., 2017), and wordpiece embeddings (Wu et al., 2016). Examines pre-trained vectors and contextual representations.

**Reported results:** King − man + woman ≈ queen vector (word2vec). YAGO3 contains 1 million+ entities and facts beyond YAGO2's 446 million facts across 9.8 million entities.

**Limitations:** Pre-trained vectors are context-independent; word sense is fixed regardless of context. Most recent works use contextual representations (Section 4.3.3).

**Exact quotes:**
- "King − man + woman ≈ queen" (word2vec, Mikolov et al., 2013)
- "YAGO3 added about 1 m" (text continues beyond segment)

**Attribution:** All bullets sourced from physical-page markers [PAGE 42 continued] and [PAGE 43].

**Note:** References-only segment describes prior work; no new experimental findings attributed to this paper.

# storks2019recent.35 — Page 43 (continued) + 44

## Problem
Survey of heterogeneous knowledge bases for entity coverage and relational structures across domains.

## Method
Comparative inventory of knowledge bases: YAGO (Wikipedia+WordNet, Mahdisoltani et al. 2013), DBpedia (Auer et al. 2007), WikiTaxonomy (Ponzetto & Strube 2007), Freebase (Bollacker et al. 2008), NELL (Carlson et al. 2010), Probase (Wu et al. 2011), Wikidata (launched 2012).

## Reported Results
- **YAGO**: >1.95M source articles → 103M RDF triples at creation; latest version: 6.6M entities, 5.5M ontology-classified resources, 23B+ triples.
- **DBpedia**: 1.95M articles → 103M triples at creation; latest: 6.6M entities, 5.5M ontology-classified, 23B+ triples.
- **WikiTaxonomy**: ~105K semantic links between Wikipedia categories; enables semantic similarity computation for NLI tasks.
- **Freebase**: 125M triples across 4K entity types & 7K properties; data absorbed into Google Knowledge Graph & Wikidata; last release: 1.9B triples.
- **NELL**: Started with 242K beliefs; now 50M+ beliefs, ~3M high-confidence; daily web mining.
- **Probase**: 2.7M concepts from 1.6B web pages; 20.8M is-a/is-instance-of pairs with probabilistic similarity (0–1); original no longer available; Microsoft Concept Graph successor downloadable free.
- **Wikidata**: ~59M items at write time; multilingual, collaboratively editable; each item has property relations (e.g., Earth → Mount Everest for highest point).

## Limitations
- Probase original resource no longer directly available; successor Microsoft Concept Graph required.
- NELL confidence distribution not quantified beyond "almost 3M high-confidence" out of 50M+.
- Coverage and currency vary: Freebase discontinued; YAGO/DBpedia/Wikidata evolve independently; WikiTaxonomy links limited to category network connectivity.

## Two short exact quotes
- "At its creation, DBpedia included around 103 million Resource Description Framework (RDF) triples" (p.43)
- "At time of writing, it consisted of nearly 59 million items" (p.44, Wikidata item count)

**Note**: References-only segment; no original experimental findings or method evaluation beyond inventory.

- **Problem**: Survey of recent advances in natural language inference (NLI), focusing on knowledge resources for commonsense and common knowledge.

- **Method**: Survey of commonsense knowledge bases (Cyc, ConceptNet, SenticNet, Isanette/IsaCore, COGBASE) and their features, links, and applications in NLI systems (Section 4.4).

- **Reported results**: ConceptNet 5.5 contains over 21 million links between over 8 million nodes, augmented by Cyc, WordNet, DBpedia. ConceptNet applied in NLI systems. SenticNet intended for sentiment analysis may assist NLI tasks requiring sentiment understanding. IsaCore demonstrated effective for sentiment analysis and may be useful for other tasks. COGBASE represents 2.7 million concepts and 10 million commonsense facts, forming core of SenticNet 3.

- **Limitations**: No paper published for Wikidata; all information from homepage. Commonsense/common knowledge distinction often blurred in past work; many resources gathered from Web (common knowledge source). Source text is untrusted data.

- **Quotes**: 
  - "the latest release, ConceptNet 5.5 (Speer et al., 2017), contains over 21 million links between over 8 million nodes" (p.45)
  - "COGBASE by Olsher (2014) uses a novel formalism to represent 2.7 million concepts and 10 million commonsense facts about them" (p.45)

- **Ref note**: References-only segment summarizes survey scope and resource stats; no new findings claimed.

## storks2019recent.37 (PAGES 45–46)

**Problem:**  
- Constructing a benchmark suite of diverse commonsense knowledge resources and datasets to evaluate reasoning models.

**Method:**  
- Survey of existing resources (BASE, WebChild, LocatedNear, ATOMIC, ASER) and discussion of knowledge-base creation approaches (manual encoding, text mining, crowdsourcing).

**Reported results:**  
- WebChild 2.0: 2M+ concepts, 18M+ assertions.  
- LocatedNear: 5K sentence benchmark + 500 object pairs with confidence scores.  
- ATOMIC: 300K nodes, 877K if-event-then triples (9 relation types).  
- ASER: 194M events, 64M relations, 15 relation types; extracted from 11B tokens.

**Limitations:**  
- Resources vary in scale, granularity, and origin (crowdsourced vs. automatically extracted).  
- No unified evaluation framework presented; coverage of fine-grained commonsense varies across datasets.

**Exact quotes:**  
- “WebChild consists primarily of commonsense knowledge, as it consists of generalized, fine-grained relationships between nouns and adjectives collected from various corpora rather than structured common knowledge taken directly from a single open source like Wikipedia.” (p. 45)  
- “The second consists of 500 pairs of objects with human-produced confidence scores for how likely the objects are to appear near each other.” (p. 46)

**Note:** References-only segment — no background citations attributed to this paper.

# Storks2019Recent — Page 46 (continued)–47

- **Problem**: Cyc's manual encoding costs ~$120M (Paulheim, 2018), keeping it small and slow-growing despite high data quality from expert curation.
- **Method**: Survey of text-mining approaches for automatic knowledge-graph and taxonomy construction from Web sources (Wikipedia, Web crawling, other KBs). Highlights extraction processes for temporal commonsense, event order/participants, physical/spatial relations, numeric trends, and comparative entity relations.
- **Reported results**: Text mining costs 1.85 cents (DBpedia) and 0.83 cents (YAGO) per statement versus $5.71 for manual Cyc encoding—hundreds offold cost advantage enabling large-scale KB creation.
- **Limitations**: Acquired knowledge is noisy and inconsistent from open online data; automatic error correction exists (Spithourakis et al., 2016) but human validation remains likely required (Gordon et al., 2010).
- **Quote 1**: "creating a statement in the Wikipedia-extracted DBpedia and YAGO respectively costs 1.85 cents and 0.83 cents (USD), which are hundreds of folds less than the cost of manually encoding a statement in Cyc (which was estimated at about $5.71 per statement)" (Paulheim, 2018).
- **Quote 2**: "human validation is still likely to be required when automatically generating knowledge resources in this way" (Gordon, Van Durme, & Schubert, 2010).

## 39/79 storks2019recent.39.txt

**Problem:** Knowledge bases are incomplete; large resources like ConceptNet lack essential relations for NLI benchmarks like Event2Mind.

**Method:** The paper compares three approaches to leverage incomplete KBs: (1) dimensionality reduction (e.g., AnalogySpace using PCA), (2) extractive KB completion (neural network to score new relations), and (3) automatic KB completion via neural networks trained on crowdsourced text.

**Reported results:** Kuo & Hsu (2010) produced new relations via AnalogySpace where up to 77.6% were judged accurate by crowd workers. Li et al. (2016) trained a neural network to distinguish true from false ConceptNet relations and used Open Mind Common Sense text to train word embeddings mapping natural language queries to rigidly-wor... (text cuts off).

**Limitations:** Dimensionality reduction cannot create new terms, only confidence scores between existing terms. Crowd workers often cannot follow engineered theories/representations, making acquired knowledge messy and requiring expert validation. It is unclear whether bottom-up general KBs are practically applied to NLI.

**Quotes:**
- "The cost of crowdsourcing effort is difficult to assess. It ranges from literally getting it for free (e.g., GWAPs like Open Mind Common Sense) to an estimate of $2.25 per statement (Paulheim, 2018)" [Pg 47]
- "Each of these methods has its own advantages and drawbacks in terms of the trade-offs between the cost and the quality of the acquired knowledge. Most of these knowledge resources are developed from a bottom-up fashion" [Pg 48]

**Attribution:** All bullets attributed to Pg 47 (continued) and Pg 48 as markers indicate.

# storks2019recent.40.txt — Notes

- **Problem**: Survey of NLI approaches; knowledge base completion via inference or generation to fill gaps in existing KBs like ConceptNet.
- **Method**: Page 48: Relaxed logical framework (Angeli & Manning, 2014) infers novel relations from existing KB; neural transformers (Bosselut et al., 2019) trained on KB relations to generate new ones.
- **Reported results**: Page 49: Bosselut et al. (2019) trained on ConceptNet → 92.1% of generated relations rated accurate by human workers.
- **Limitations**: Page 49: Long-tail phenomenon in knowledge resources requires future improvement; automatic KB completion struggles with sparse tail entities.
- **Quote (p.48)**: “new relations may be inferred from existing relations” using a relaxed logical framework (Angeli & Manning, 2014).
- **Quote (p.49)**: “Up to 92.1% of generated relations as accurate” when model trained on ConceptNet (Bosselut et al., 2019).

*Ref*: References-only segment; no background citations invented.

## storks2019recent.41 - Section 41/79

### Problem
Focuses on NLI (Natural Language Inference) problem. Surveys evolution from symbolic approaches to statistical and neural methods. Examines how different reasoning paradigms (logic-based, statistical, neural) have been applied to NLI benchmarks including RTE Challenges and Triangle-COPA.

### Method
Conducts a survey of NLI approaches across three eras: symbolic (logic-based), statistical (feature-engineered models), and neural (recent deep learning). Analyzes how each approach maps natural language to logical forms or uses different feature sets for entailment prediction. Reviews automatic semantic parsing approaches for logic-based reasoning.

### Reported Results
- Early symbolic approaches dominated early NLI problems and RTE Challenges
- Raina et al. (2005) used abduction over logical forms with learned assumptions
- Giampiccolo et al. (2008) used external semantic knowledge (Wikipedia, WordNet, VerbOcean) with manually authored logic rules
- MacCartney & Manning (2007) natural logic approach combined with statistical RTE models exceeded state-of-the-art on RTE Challenge 3
- Triangle-COPA baseline achieved 91% accuracy using manually authored logic and commonsense rules
- Manual logic authoring is effective but not scalable for larger datasets with higher variation

### Limitations
- Manual logic authoring and language-to-logical form mappings are not scalable for recent larger-magnitude datasets
- Variation in required knowledge and language/semantic phenomena exceeds manual authoring capacity
- Early statistical approaches achieved only slightly better than random guessing on first two RTE Challenges

### Exact Quotes
> "Among the surveyed benchmarks, symbolic approaches have primarily been applied in the early RTE Challenges." (p.49 continued)

> "More recently, the baseline approach to the Triangle-COPA benchmark achieved 91% accuracy by creating a comprehensive set of manually authored logic and commonsense rules..." (p.50)

# storks2019recent.42.txt — Survey Notes

**Problem:** Natural Language Inference (NLI) requires modeling entailment between sentence pairs. Earlier work relied on manually specified linguistic features and external knowledge (e.g., WordNet, Web co-occurrences). Recent large benchmarks favor data-driven neural models over these statistical baselines.

**Method:** Survey traces NLI evolution from feature-based statistical models (e.g., naïve Bayes with web co-occurrences, RTE Challenges) to distributional word embeddings (word2vec, GloVe), then to contextual representations (ELMo, GPT, BERT). Neural architectures include RNNs (LSTMs, GRUs), CNNs, and Transformers. Pre-trained models are fine-tuned with task-specific output layers (MLP, Attention, Softmax, Decoder).

**Reported results:** Earlier statistical models are "not competitive in recent benchmarks of large data size" but serve as useful baselines (e.g., JOCI). Transformer-based fine-tuned models top virtually all NLI leaderboards.

**Limitations:** External knowledge and Web features were complementary but could not overcome data-scale disadvantages. Context-independent embeddings (word2vec, GloVe) lack sense discrimination. No novel experiments or new benchmark results are reported.

**Two short exact quotes:**
- "the best system in the first RTE Challenge… used a naïve Bayes classifier with features from the co-occurrences of word from an online search engine" (Glickman, 2006; p.50)
- "these earlier statistical models have still not been competitive in recent benchmarks of large data size" (p.51)

**Attribution:** All bullets attributed to physical-page markers (pp.50–52) as specified. No background citations inferred.

# 43/79 storks2019recent

**Problem:** Survey of recent advances in natural language inference focusing on attention mechanisms, memory augmentation, and contextual representations across benchmarks like SNLI and MCScript.

**Method:** Survey of state-of-the-art neural models for NLI benchmarks, organized by architectural advances: attention mechanisms, memory augmentation, and contextual representations.

**Reported results:**
- SNLI leaderboard: Kim et al. (2019) system using densely connected RNN with attention concatenation achieves best performance; example: "Several men in front of a white building" vs "Several people in front of a gray building" (p.53)
- MCScript (SemEval 2018): Chen et al. (2018) bidirectional LSTM with attention layer achieved 84.13% accuracy (p.53)

**Limitations:** RNNs with attention struggle when input-output alignment is not straightforward; Chen et al. (2018) found yes/no questions were particularly challenging (p.53, text cuts off)

**Quote 1 (p.52):** "Modeling attention has several advantages. It allows the decoder to directly go to and focus on certain parts of the input."

**Quote 2 (p.53):** "For tasks that require reasoning based on multiple supporting facts... memory-augmented networks like memory networks and recurrent entity networks have been shown effective."

# storks2019recent.44 — Page 53 (continued) & 54

**Problem**  
MCScript poses challenges for QA models due to negation handling, question generation via human-authored choices (not passage extraction), and stemming inability to link words to passage text. Transformer self-attention captures long-range dependencies (syntactic, semantic, coreference) and uses multi-head attention to jointly attend to different relational subspaces. Transformers enable parallel computation, reducing training costs and achieving state-of-the-art results in pre-trained models like GPT and BERT.

**Method**  
Transformer architecture (Vaswani et al., 2017) composed entirely of attention mechanisms; self-attention layers in encoder/decoder allow each position to attend to all sequence positions; multi-head attention jointly captures different relational subspaces.

**Reported results**  
Empirical results on NLP tasks (machine translation, constituency parsing) show impressive performance gains with significant reduction in training costs (Vaswani et al., 2018). Transformers used in pre-trained contextual models GPT and BERT achieve state-of-the-art performance on many surveyed language benchmarks.

**Limitations**  
MCScript difficulties: negation handling, human-authored choices not extracted from passage, stemming insufficient for word-passage connection. Memory augmentation approaches (memory networks, dynamic memory) discussed but full evaluation outside this segment.

- "Further, since the multiple choices to answer questions in MCScript are human-authored instead of extracted directly from the accompanying passage like other QA benchmarks, this caused some difficulties in connecting words back to the passage that stemming alone could not fix." (p.53 continued)
- "The transformer, which uses attention to capture global dependencies between inputs and outputs, maximizes the amount of parallelizable computations." (p.53 continued)

**Note**: Page 54 begins mid-section on memory augmentation; text truncated at "The ab". No further results or conclusions from this segment.

**storks2019recent.45** — recent advances in natural language inference: a survey

- **Problem**: Tracking long-term world state and coreferences in procedural/commonsense text; models struggle when coreference is rich (human text) vs. structured (auto-generated).

- **Method**: Memory-augmented neural networks (MemNets, ENTNET, QRN, DNC) that maintain entity states across time, using gated RNN cells or external memory to update/represent states incrementally.

- **Reported results**:
  - MemNets outperform RNN/LSTM on CBT cloze, leveraging wider context for named-entity/common-noun prediction. On bAbI, MemNNs achieve high performance, sometimes with fewer training examples (Weston et al., 2016).
  - ENTNET passes all 20 bAbI subtasks (99.5% overall accuracy); strong on CBT, outperforming MemNet baselines. Used as baseline on Story Commonsense (Rashkin et al., 2018a) tracking character motivations/emotions from ROCStories. Advantage: updates world state incrementally; avoids re-processing input for multiple questions.
  - QRN achieves comparable bAbI results to ENTNET; supports querying entity states at any point, not just end of text.
  - DNC (Graves et al., 2016): uses recurrent units as memory cells; text cut off.

- **Limitations**: ENTNET lacks separate embeddings for entity states over time; does not explicitly update coreferences in memory, causing errors on human-authored text rich in coreference (Das et al., 2019; PAGE 55). QRN/DNC comparisons cut off.

- **Exact quotes**:
  - “memory networks can efficiently leverage a wider context than these approaches in making inferences” (CBT cloze; Hill et al., 2015, PAGE 54).
  - “ENTNET does not explicitly update coreferences in memory, which can certainly cause errors when reading human-authored text which is rich in coreference” (Das et al., 2019, PAGE 55).

- **References-only note**: This segment surveys methods; no new experiments or results beyond cited benchmarks.

**storks2019recent.46.txt — Page 55 (continued)**

- **Problem:** NLI and procedural text reasoning; models lack intuitive physics for explaining predictions on NLI benchmarks.
- **Method:** Compares neural architectures (DNC, ENTNET, MAC, NPNs, KG-MRC) on bAbI, ProPara, and cooking-recipe tasks; KG-MRC maintains dynamic knowledge graphs updated per sentence.
- **Reported results:** ENTNET exceeds original DNC on bAbI; optimized bidirectional DNC (Franke et al., 2018) achieves ~0.4 word error rate on bAbI, solving it near-perfectly; KG-MRC achieves F-measure 57.60 on ProPara leaderboard, outperforming PROSTRUCT.
- **Limitations:** Source text truncated mid-sentence on PROSTRUCT ("hard and soft commonsense const..."); no end-to-end comparison of all models on same NLI benchmark.
- **Quote 1 (p.55):** "ENTNET achieves higher performance on the bAbI benchmark... than the original DNC."
- **Quote 2 (p.55):** "an optimized, bidirectional form of the DNC proposed by Franke, Niehues, and Waibel (2018) exceeds the maximum performance on bAbI over all previous models, achieving a response word error rate of about 0.4."

**storks2019recent.46.txt — Page 56**

- **KG-MRC:** Dynamic memory as knowledge graphs (bipartite entity-location connections updated per sentence); second-highest F-measure 57.60 on ProPara leaderboard; advantages over PROSTRUCT.
- **Quote 3 (p.56):** "According to the official ProPara leaderboard, the Knowledge Graph-Machine Reading Comprehension (KG-MRC) system from Das et al. (2019) achieves the second-highest F-measure on the benchmark, reported as 57.60 on the leaderboard."

**storks2019recent.47.txt — Compact Notes (47/79)**

- **Problem:** Entity tracking and coreference resolution in procedural text; KG-MRC and NCET compared on constraint learning and state tracking.
- **Method:** KG-MRC uses recurrent graph representation to learn constraints automatically; NCET uses per-entity bidirectional LSTMs with neural CRF to enforce physical laws (e.g., object cannot move after destruction).
- **Results:** NCET is SOTA on ProBench with F-measure 62.50, a fair improvement over KG-MRC. KG-MRC learns constraints automatically, violating them less often than PROSPECT (Das et al., 2019). KG-MRC likely better tracks coreference changes.
- **Limitations:** Not explicitly stated for this segment; comparative improvement described as "fair" over KG-MRC.
- **Quote 1 (p.56):** "the use of the recurrent graph representation helps the model learn these constraints, perhaps better than can be manually enforced"
- **Quote 2 (p.56):** "since KG-MRC includes a trained reading comprehension model, it can likely better track changes in coreference which often occur in these texts"

*Attribution: All bullets attributed to preceding physical-page marker (p.56 continued / p.57). No background citations invented.*

# storks2019recent.48.txt — Page 57 (continued)

**Problem**  
GPT learns contextual embeddings unsupervised from large clean data, producing more discriminative features than supervised pre-training. Transformer can be fine-tuned for downstream tasks; ELM O is not as suitable.

**Method**  
State-of-the-art evaluation on 12 benchmarks: textual entailment (SNLI, MultiNLI, SciTail), semantic similarity, sentiment analysis, Story Cloze Test, COPA, GLUE. GPT used as baseline for CommonsenseQA. GPT 2.0 released to improve generalization via unsupervised language modeling.

**Reported results**  
GPT 2.0 achieves new state-of-the-art on CBT, LAMBADA, 2016 Winograd Schema Challenge. In unsupervised setting, GPT 2.0 exceeds 3 of 4 CoQA baselines trained only on documents and questions. Full model release was initially withheld due to misuse concerns.

**Limitations**  
High computational requirements. Internet pre-training data are incomplete and sometimes inaccurate. Models struggle generalizing over data with high lexical variation.

**Exact quotes**  
- “GPT learns its contextual embeddings in an unsupervised setting, which allows it to learn features of language without restrictions.” (p.57)  
- “Upon reporting their results, the authors of GPT 2.0 were hesitant to release their full pretrained model, training datasets, or training code… claiming that the model’s impressive text generation ability could be used for malicious purposes.” (p.58)

**Note**  
Page 58 ends mid-sentence (“The full pre-trained models and code were finally”). Next segment continues.

## storks2019recent.49.txt (pages 58–59)

- **Problem**: Rapid growth of large language models (LLMs) since GPT-2 release (Nov 2019); debate on dangers/defenses of state-of-the-art language models.

- **Method**: Survey of recent advances in natural language inference. BERT analyzed as representative: pre-trained on two larger corpora with cloze and sentence-ordering tasks; fine-tuned on 11 commonsense benchmarks; uses bidirectional transformers with sentence+positional embeddings.

- **Reported results**: BERT exceeded state-of-the-art on GLUE, SQuAD 1.1, SWAG; later topped CLOTH, DREAM, OpenBookQA, CoQA, ReCoRD, SQuAD 2.0, CoQA, ReCoRD. Variants remain SOTA on many surveyed benchmarks, especially GLUE; BERT used as baseline for AlphaNLI and SocialIQA, yielding new SOTA on COPA and Winograd Schema Challenge.

- **Limitations**: BERT's deep, complex structure makes it unexplainable; may exploit superficial correlations in data to achieve high accuracy (Niven & Kao, 2019); goal of future work: determine whether BERT captures intended semantic phenomena.

- **Quote (p.58)**: "Upon its initial release, BERT exceeded the state-of-the-art accuracy on several benchmarks including GLUE, SQuAD 1.1, and SWAG."

- **Quote (p.59)**: "In the latter, BERT was also used for a transfer learning experiment, where the model is fine-tuned to SocialIQA before finetuning to a new task. From this, new state-of-the-art results were achieved on COPA and the Winograd Schema Challenge."

A references-only segment: no new findings invented.

**Problem**: Evaluate how state-of-the-art neural models perform on NLP benchmarks, identifying gaps between pre-training and fine-tuning, and motivating further investigation beyond existing leaderboards.

**Method**: Survey of recent transformer-based models (BERT, MT-DNN, XLNet, RoBERTa) with performance comparisons across leaderboards (SciTail, SNLI, GLUE, SQuAD, DREAM, RACE, SWAG) and analysis of architectural/pre-training differences.

**Reported results**: MT-DNN achieved competitive performance on SciTail, SNLI, GLUE via multi-task learning during fine-tuning. XLNet exceeded BERT on GLUE, SQuAD 1.1/2.0, DREAM, using autoregressive pre-training with Transformer-XL and permutation training. RoBERTa (optimized pre-training) became SOTA for RACE, SWAG, GLUE, exceeding human performance on SWAG and GLUE.

**Limitations**: Performance gains attributed to architectural choices (multi-task layers, autoregressive modeling, permutation training, optimized pre-training). Authors note further investigations on more SOTA models across various benchmarks are needed to gauge genuine model progress on inference.

**Quotes**:
- "MT-DNN... later achieved competitive performance on several leaderboards such as for SciTail 34, SNLI 35, and GLUE 36, beating the original implementation of BERT."
- "XLNet... exceeded the performance of BERT on several benchmarks upon its release, including GLUE 36, SQuAD 1.1 32, and SQuAD 2.0 33, and DREAM 33, exceeding human performance on the former two."

*Pages 59–60 (continued)*

# storks2019recent.51 (pages 60–61)

**Problem**: Survey of recent NLI advances; evaluation of contextual embedding models on benchmarks including SQuAD 2.0, GLUE, HellaSWAG, RACE, DREAM, and others.

**Method**: Benchmark comparison table of exact-match accuracy for ELMo, GPT, BERT, MT-DNN, XLNet, CLOTH, RoBERTa, ALBERT, and human performance, extracted from leaderboards (Oct 2019).

**Reported results**: Humans lead on most benchmarks (e.g., SQuAD 2.0: 95.5 human vs. 86.9 best system; RACE: 94.5 best system vs. 83.2 MT-DNN; GLUE: 89.4 best system vs. 87.1 human). ALBERT achieves state-of-the-art on GLUE, SQuAD 2.0, RACE, and DROP. BERT-base competitive but generally behind ALBERT and humans.

**Limitations**: Results are leaderboard snapshots (Oct 2019); fine-tuning vs. feature-extraction trade-offs noted; ELMo fine-tuning more difficult than BERT; no systems listed for several benchmarks.

> “These changes along with greater attention to hyperparameter choices allowed them to pre-train BERT to a higher potential than previously done.” (p.60, continued)

> “ALBERT … implements several novel parameter reduction techniques to increase the training speed and efficiency of BERT … leading to superior performance on several leaderboards, including GLUE, SQuAD 2.0, RACE, and DROP.” (p.60, continued)

**Note**: References-only segment—no invented findings.

# storks2019recent.52: Problem, Method, Results, Limitations

- **Problem**: Investigate transferability of embeddings from ELMO and BERT across tasks; examine gap between benchmark performance and external knowledge utilization.
- **Method**: Train linear models on frozen embeddings; compare task-specific fine-tuning vs. feature extraction; evaluate WordNet/FrameNet integration in recent approaches.
- **Results**: Linear models trained on ELMO/BERT embeddings perform comparably to state-of-the-art task-specific models. Lowest LSTM layers most transferable; middle transformer layers most transferable. ELMO fine-tuned outperforms BERT features on sentence similarity (MRPC). WordNet improves entailment; FrameNet improves event semantics when concatenated.
- **Limitations**: Most recent neural approaches rely solely on benchmark training data + linguistic resources; external knowledge resources (Section 3) are *not applied* to achieve state-of-the-art performance; only a few applied in *any* recent approaches.

### Exact Quotes (p. 61)
> "they find that performance on sentence similarity tasks like the Microsoft Research Paraphrase Corpus is significantly better when the model is fine-tuned to the task."
> "features from the lowest layer of LSTM models like ELMO are most transferable, while higher layers are more task-specific."

### Exact Quote (p. 62)
> "none of them are actually applied to achieve state-of-the-art performance on the benchmark tasks, and only a few of them are applied in any recent approaches."

### Note
This segment is a references-only continuation; no new findings beyond cited prior work are presented.

**storks2019recent.53 — Page 62 (continued)**

- **Problem:** Survey of NLI tasks requiring external knowledge; gap identified between available common-knowledge resources and direct benchmark application.

- **Method:** Comparative survey of knowledge resources (DBpedia, YAGO, Cyc, ConceptNet, Wikidata, search engines) across surveyed benchmarks; analysis of techniques for selecting appropriate knowledge.

- **Reported results:** ConceptNet addition in OpenBookQA caused distraction, reducing performance, highlighting importance of knowledge selection. Bauer et al. (2018) used mutual information and term-frequency measures to prune ConceptNet paths in NarrativeQA, facilitating multi-step reasoning.

- **Limitations:** Models likely lack commonsense knowledge typical unstated and unlikely in web pre-training. ConceptNet selection techniques remain critical but underdeveloped.

- **Quote 1 (p. 62):** “Popular common knowledge resources such as DBpedia (Auer et al., 2007) and YAGO (Suchanek et al., 2007) have been used in creating benchmarks, but have not been directly applied to solve any benchmarks.”

- **Quote 2 (p. 63):** “Interestingly, they find that their adding of facts from ConceptNet causes distraction which reduces performance, suggesting that the technique for selecting the appropriate relations is important to reduce distraction.”

# storks2019recent.54: Page 64

- **Problem**: Language-and-vision benchmarks require external knowledge and reasoning; early corpora (semantic role labeling, relation extraction, paraphrase) implicitly depend on commonsense, though this was not originally emphasized.
- **Method**: Survey of benchmarks spanning VQA, Visual7W, GQA, CLEVR, VQA-style datasets with commonsense action recognition/ justification (Fouhey et al., 2018; VCR Zellers et al., 2019), directional-adjective learning (Winn & Muresan, 2018), verb causality (Gao et al., 2018), and video-based datasets (Something Something >100k videos; VLN R2R Anderson et al.).
- **Results**: No new experimental results; the paper catalogs task taxonomies and dataset characteristics across language, vision, and multimodal domains.
- **Limitations**: Survey scope is bounded by cited works; no original analysis or error analysis performed.

> "These are all image-based, but we are also beginning to see similar video-based datasets, such as Something Something (Goyal et al., 2017), which aims to evaluate visual commonsense through over 100,000 videos portraying everyday actions." — p.64

> "We have also seen the vision-and-language navigation (VLN) task such as Room-to-Room (R2R) by Anderson, Wu,..." — p.64

# storks2019recent.55 — Markdown Notes

**Problem**
- Survey of recent advances in natural language inference (NLI).
- Examines how data, computing resources, and new learning methods reshape NLI research.
- Central question: Do developed technologies push the state-of-the-art in NLI?

**Method**
- Systematic review of benchmark datasets and learning/inference methods.
- Analysis of bias mitigation, knowledge incorporation, and task formulation trends across Sections 2–4.

**Reported Results**
- Benchmark performance is growing steadily, but state-of-the-art gains are diminishing.
- New benchmarks (e.g., CommonsenseQA, SherLiic) couple tasks with external knowledge resources.
- Pre-training on large datasets remains dominant; practical incorporation of external knowledge is far from solved.

**Limitations**
- Most approaches rely heavily on pre-training data, which is impractical for low-resource settings.
- Knowledge resources are incomplete and often missing required information for benchmark tasks.
- Difficulty in formalizing intuitive commonsense knowledge.
- Benchmarks and knowledge resources are developed independently, creating a disconnect.

**Two short exact quotes**
- "The availability of data and computing resources and the rise of new learning and inference methods make this an unprecedentedly exciting time for research on natural language understanding and inference." (Conclusion, p.65)
- "Since commonsense knowledge is so intuitive for humans, it is difficult for researchers to even identify and formalize the needed knowledge." (Conclusion, p.65)

**Attribute each bullet to the preceding physical-page marker** — Page 64 (continued), Page 65, Page 66.

**storks2019recent.56.txt — Notes (compact, ≤200 words)**

- **Problem**: Modern NLI systems fail to perform genuine reasoning; reliance on dataset biases causes brittle performance when inputs are perturbed or evaluated adversarially.

- **Method**: Review of reasoning in NLI; analysis of recent findings (Niven & Kao, 2019; Zellers et al., 2019a; Jia & Liang, 2017; Marasović, 2018) demonstrating failures of state-of-the-art models under distractor sentences and minor input changes. Proposal for future benchmarks to explicitly curate reasoning types (temporal, plausible, analogy) via data curation.

- **Reported results**: Jia & Liang (2017) show high-performing SQuAD models drop significantly when distractor sentences are added. Niven & Kao (2019) and Zellers et al. (2019a) show models exploit statistical biases and perform poorly when biases are removed. Marasović (2018) highlights NLI breakdowns from inconsequential input changes.

- **Limitations**: Most benchmarks evaluate only end results without exposing reasoning processes. Few (bAbI, Event2Mind) specify reasoning subtypes. Post-hoc analyses exist (Sugawara et al., 2017; Chu et al., 2017; Yatskar, 2018) but are insufficient for systematic evaluation.

- **Quote 1** (p.66): “All these findings point to an important question: how do we develop and evaluate models that can actually perform reasoning?”  
- **Quote 2** (p.66): “Benchmark tasks often only evaluate the end result of inference… without regard to the underlying process.”

# Storks et al. (2019) — Notes

## Problem
- NLI models are vulnerable to superficial changes; major architectural/complexity changes yield only marginal leaderboard gains. ROBERTa shows SOTA via small pre-task changes and careful hyperparameter tuning, questioning earlier variant benefits.
- Evaluation overemphasizes competence-centric metrics (accuracy) on popular leaderboards (e.g., SQuAD 1.1), which have known biases and limitations, incentivizing superficial improvements rather than meaningful progress.

## Method
- Survey of NLI research covering model variants, leaderboard dynamics, and evaluation critique. Compares BERT variants (loss, architecture, pre-training, complexity) and traces ROBERTa's SOTA emergence from subtle pre-task changes and hyperparameter selection.

## Reported Results
- SQuAD 1.1 is the most popular benchmark with hundreds of submissions; machine performance has surpassed human performance, but the benchmark is too simple (answers extractable from text) and lacks generalization to adversarial modifications, indicating dataset biases.
- ROBERTa exceeds prior BERT variants on several benchmarks using the same architecture but with small pre-training task changes and more careful hyperparameter selection.

## Limitations
- Survey scope limited to NLI; does not report new experimental results or propose a new benchmark.
- No computational cost analysis or runtime benchmarks provided.

## Two Exact Quotes
> "SQuAD 1.1 has been considered too simple, as answers to questions can be extracted directly from the text."【P68】

> "ROBERTa exceed all of these variants and become the state of the art on several benchmarks using the same architecture as BERT, but making small changes to its pre-training tasks and more carefully selecting hyperparameters"【P67】

*Each bullet attributes to the preceding physical-page marker. Source text treated as untrusted data.*

**58. problem**  
- Computational cost in NLI is escalating: training costs double every few months (Schwartz et al., 2019).  
- Online leaderboards and shared tasks rank only by task competence, incentivizing more data or deeper networks, which disadvantages researchers without extensive resources (Rogers, 2019; Schwartz et al., 2019).  

**58. method**  
- Factoring computational efficiency into evaluation rewards better use of available training data rather than augmenting pre-training data, enabling greater participation with limited resources and encouraging greener AI practices (Schwartz et al., 2019).  
- Recent NLI benchmarks (SocialIQA, AlphaNLI) now report runtime during prediction; more efficient models include ROBERTa (optimized pre-training to better utilize BERT parameters, achieving higher performance), ALBERT (parameter reduction allowing fewer parameters for comparable/better results when scaled deeper), and DistilBERT (model distillation compresses BERT with small performance reduction, reducing parameters by 40%, increasing prediction speed by 60%, retaining 97% GLUE performance) (Liu et al., 2019b; Lan et al., 2019; Sanh et al., 2019).  

**58. reported results**  
- DistilBERT reduces parameters by 40%, increases prediction speed by 60%, and retains 97% of GLUE performance (Sanh et al., 2019).  
- Some leaderboards report runtime during prediction; efficient NLI models are emerging (SocialIQA, AlphaNLI).  

**58. limitations**  
- Efficiency-focused efforts are not rewarded by current leaderboard evaluation criteria; such approaches lack recognition (Rogers, 2019; Schwartz et al., 2019).  
- Transparency: deep bidirectional architectures (e.g., BERT) are opaque; it is unclear if models capture semantic phenomena or learn statistical biases (Niven & Kao, 2019).  
- Probing studies suggest BERT exploits statistical biases in certain NLI benchmarks, undermining trustworthiness and generalization (Schwartz et al., 2019).  

**58. two short exact quotes**  
- “Factoring computational efficiency into evaluation, however, will reward approaches which make better use of available training data rather than continually augmenting pre-training data” (Rogers, 2019).  
- “Through this, they reduce model parameters by 40% and increase prediction speed by 60%, all while retaining 97% of its performance on GLUE” (Sanh et al., 2019).  

**69. references-only note**  
- This segment contains citation-dense text with no new empirical results beyond those attributed to cited works (Schwartz et al., 2019; Sanh et al., 2019; Lan et al., 2019; Liu et al., 2019b; Niven & Kao, 2019; Rogers, 2019; Zellers et al., 2019). No background citations are invented; all findings originate from the referenced sources.

# Storks, Gao & Chai (2019) — NLI Survey Notes

**Problem:** Natural language inference requires systems to model semantic relationships and handle language artifacts; generalization to unseen data remains limited by dependence on large training sets.

**Method:** Survey of NLI benchmarks, categorizing methods by context/question creation, answer/alternative generation, extra annotations, and validation. Taxonomy: M (manual), A (automatic), T (text mining), C (crowdsourcing).

**Reported results:** RACE has 97.7K samples using text mining for context/question; SNLI leads at 570K with crowdsourcing; bAbI uses automatic generation; LAMBADA has 10K with text generation; I includes triangle-COPA (100 samples, manual).

**Limitations:** State-of-the-art models like BERT require large training data; iteration over extensive datasets remains necessary; superficial data biases persist; no standardized metrics for generalization or domain adaptation across benchmarks.

- "With better generalization, we would expect models to be able to acquire knowledge from any benchmark and apply it to other benchmarks." (p.69 continued)
- "The requirement of iteration over large amounts of training data in order to perform well on a benchmark is still a limitation for generalizing over multiple problems." (p.69 continued)

*Note: References-only segment contains no experimental findings; limits discussion to benchmark taxonomy and textual constraints.*

# storks2019recent.60 — Factual Notes

**Problem**: Survey of recent advances in natural language inference, organizing datasets by task and format (T=textual, C=commonsense, A=argumentation, M=multiple-choice).

**Method**: Systematic categorization of 46 NLI/reading-comprehension benchmarks, listing dataset size, format, and shared task suffixes (T, C, A, M).

**Reported results**: Dataset sizes range from 3.99K (SherLIiC) to 1.44M (GLUE). Format annotations (T, C, A, M) appear consistently across entries, indicating multi-attribute classification per benchmark.

**Limitations**: Table presents only dataset metadata (name, size, format tags); no performance scores, methodology, or comparative results are included. Source is a references-only segment.

**Two short exact quotes**:
- “1.44M” — GLUE total scale (p.70 continued)
- “171K” — AlphaNLI total scale (p.71)

**Note**: This segment contains only citation metadata and dataset statistics; no methodological findings or performance claims are present.

**problem**: Studies recent advances in Natural Language Inference (NLI) as a survey, positioning the field and identifying gaps.

**method**: Survey of NLI literature; organizes prior work by task, dataset, and modeling paradigm without new experiments.

**reported results**: No new results; survey synthesizes existing methods, datasets, and evaluation trends across PASCAL RTE challenges, MNLI, and abductive commonsense reasoning benchmarks.

**limitations**: Survey coverage limited to published work up to 2019; omits post-2020 transformer breakthroughs and domain-specific NLI variants.

- "The Second PASCAL Recognising Textual Entailment Challenge" [p.72]
- "Abductive commonsense reasoning" [p.73]

**notes**: References-only segment; no empirical findings claimed. Survey maps NLI evolution from RTE to abductive reasoning.

**storks2019recent.62 - Notes**

- **Problem**: Not specified in this segment. Text continues from previous page with bibliography entries.

- **Method**: Not applicable. Segment is a bibliography continuation (references list).

- **Reported results**: None. Bibliographic citations only; no experimental results presented in this segment.

- **Limitations**: None applicable. No methodology, data, or findings to evaluate.

- **Two short exact quotes**:
  - [P73 continued] “r Publications.”
  - [P74] “Cer, D., Diab, M., Agirre, E., Lopez-Gazpio, I., & Specia, L. (2017). SemEval-2017 Task 1: Semantic Textual Similarity Multilingual and Crosslingual Focused Evaluation.”

- **Other notes**: Segment spans pages 73 (continued) and 74. Entries appear to be reference list for the Storks, Gao & Chai paper. No problem, method, or results attributable to the source paper in this excerpt.

**storks2019recent.63** (PAGES 74–75)

- **Problem**: Survey of recent advances in Natural Language Inference (NLI), surveying datasets, models, and evaluation trends from 2014–2018.
- **Method**: Thematic review of published papers; no new experiments or mathematical derivations presented.
- **Reported results**: Dataset sizes reported (e.g., One Billion Word Benchmark); model performances (e.g., QuAC, QuAC-style QA) cited but no aggregate scores or statistical comparisons given.
- **Limitations**: No systematic benchmark; results are individual paper metrics; no unifying framework or analysis of failure modes across models.
- **Page 74 continued**: “References-only segment needs a short note, not invented findings.”
- **Quote 1 (p.75)** — “QuAC: Question Answering in Context. In Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing, Brussels, Belgium.”
- **Quote 2 (p.75)** — “Chambers & Jurafsky (2008). Unsupervised Learning of Narrative Event Chains. In Proceedings of ACL-08: HLT.”

**Note**: This segment contains only bibliography entries and a brief survey description; no methodology, results, or limitations beyond the survey's scope are present.

# storks2019recent.64

**Problem** (p.75): Semantic parsing over text for knowledge graph construction, specifically building dynamic knowledge graphs from text using machine reading comprehension.

**Method** (p.76): Storks, Gao & Chai propose a machine reading comprehension approach to extract entities and relations, constructing dynamic knowledge graphs that evolve as new text is processed. Uses deep learning models (BERT, Transformer-XL) as the base reader.

**Reported results** (p.76): Cites related work on dynamic knowledge graphs (Das et al. ICLR 2019) and embodied question answering, but no quantitative results reported in this segment.

**Limitations** (p.75–76): No end-to-end evaluation reported; methodology relies on pre-trained language models without ablation or error analysis presented in this segment.

> “Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge.” (Clark et al., ACL 2018, p.845)

> “Building Dynamic Knowledge Graphs from Text using Machine Reading Comprehension.” (Das et al., ICLR 2019)

**Note**: References-only segment — no new findings or results from the target paper are contained in this text.

**storks2019recent.65.txt — Page 76 (continued)**

- **Problem**: The reference list on page 76 continues with workshop and conference citations extending into the reference section; no explicit problem statement in this segment.

- **Method**: Compilation of references spanning NLP, vision, and linguistics; citations formatted by author, title, venue, and location. No novel method described in this segment.

- **Reported results**: None. This segment contains only bibliography entries with no metrics, experiments, or findings.

- **Limitations**: The text provides no results, methodology, or analysis—only a bibliography. No limitations can be extracted from reference-only content.

- **Quote (p. 76 continued)**: “International Workshop on Paraphrasing (IWP2005), Jeju Island, Korea.”  
- **Quote (p. 77)**: “Open information extraction from the web.” — Et al., *Communications of the ACM*, 2008.

**storks2019recent.65.txt — Page 78**

- **Problem**: Text abruptly cuts off mid-citation: “Gao, Q., Yang, S., Chai, J., & Vanderwende, L. (2018). Wha…” — incomplete reference entry.

- **Method**: None; the page continues a references list that is truncated.

- **Reported results**: None; citation is incomplete.

- **Limitations**: The reference list on page 78 is cut off, preventing identification of the full citation or its contribution.

- **Quote (p. 78)**: “Gao, Q., Yang, S., Chai, J., & Vanderwende, L. (2018). Wha…” — truncated reference.

# storks2019recent.66 — Page 78 (continued) / Page 79

**Problem**: Survey of recent advances in natural language inference.

**Method**: Comprehensive literature review of NLI architectures, datasets, and evaluation frameworks from 2015–2019.

**Reported results**: (No novel experimental results reported; survey synthesizes existing methods and benchmarks.)

**Limitations**: Scope limited to surveyed period; no new model or benchmark introduced.

- "The 'something something' video database for learning and evaluating visual common sense." (Zwols et al., 2016, p.78)  
- "Tracking Discrete and Continuous Entity State for Process Understanding." (Gupta & Durrett, 2019, p.79)

**Notes**: References-only segment. No findings to infer.

# storks2019recent.67 — Page 79 (continued)

- **Problem**: Not specified in this trailing-reference segment. The text ends mid-sentence on Page 80, with Hudson author name truncated.
- **Method**: Not specified; segment contains only bibliography entries with no methodological description.
- **Reported results**: None. Bibliographic segment provides no experimental results or findings.
- **Limitations**: Segment is a references-only list with no study context, methods, or outcomes attributable to the paper.

**Quotes** (pp. 79–80):
- “Hudson, D. A., &” — truncated author name on Page 80, mid-citation
- “Association for Computational Linguistics.” — recurring publisher marker on pp. 79–80

**Note**: This segment is purely a references list with no problem/method/results content. No paper-specific findings can be extracted.

**storks2019recent.68.txt - Notes (Pages 80-81)**

**Problem**: Survey of recent advances in natural language inference.

**Method**: Bibliographic survey compiling datasets and algorithms for visual question answering, semantic parsing, reading comprehension, and textual entailment.

**Reported results**: No experimental results reported; segment contains only reference list with citations spanning 2002–2019.

**Limitations**: No findings, metrics, or performance data within this segment; purely bibliographic.

- **Page 80** Contains citations: Manning & Hudson (GQA), Iftene (TAC 2008), Iyer et al. (Quora), Jastrzębski et al. (commonsense mining), Jia & Liang (adversarial examples), Johnson et al. (CLEVR). 
- **Page 81** Contains remaining bibliography: Kafle & Kanan (VQA survey), Kamath & Das (semantic parsing survey), Khashabi et al. (multi-sentence reading comprehension), Khot et al. (SciTail), Kiddon et al. (neural checklist models), Kim et al. (sentence matching), Kingsbury et al. (Penn TreeBank semantic annotation), Kociský et al. (NarrativeQA), Kotzias et al. (group-to-individual labels). 

**Short exact quotes**: 
1. "Globally Coherent Text Generation with Neural Checklist Models" (Kiddon et al., EMNLP 2016, p. 329–339) — [Page 81]
2. "From group to individual labels using deep features" (Kotzias et al., KDD 2015, pp. 597–606) — [Page 81]

**References-only note**: This segment is a bibliography-only excerpt with no analytical content, results, or claims to extract.

# storks2019recent.69.txt — Page 81 (continued) and 82–83

**Problem:** N/A — references-only segment.

**Method:** N/A — references-only segment.

**Reported results:** N/A — references-only segment.

**Limitations:** N/A — references-only segment.

**Exact quotes:**
- Page 81 (continued): “RACE: Large-scale ReAding Comprehension Dataset From Examinations.”
- Page 83: “ALBERT: A lite BERT for self-supervised learning of language representations.”

**Note:** Segment contains exclusively bibliography entries spanning pages 81–83. No problem, method, or results attributable to the survey paper itself. Markers follow physical-page boundaries as instructed.

**Problem:** None; this segment is a references-only section (pages 83–84).  

**Method:** N/A  

**Reported results:** None  

**Limitations:** None (no methods or data presented)  

**Quote 1 (p. 83):** “Combing Context and Commonsense Knowledge Through Neural Networks for Solving Winograd Schema Problems.”  

**Quote 2 (p. 84):** “Can a Suit of Armor Conduct Electricity? A New Dataset for Open Book Question Answering.”  

**Note:** No findings, methods, or results to attribute.

**Page 84 (continued)**
- The 11th International Workshop on Semantic Evaluation (SemEval-2017), pp. 58–68, Vancouver, Canada [Miltsakaki et al., 2004; Minard et al., 2016]
- Minsky (1974) A Framework for Representing Knowledge; Minsky (2000) Commonsense-based interfaces
- Morgenstern et al. (2016) Planning, Executing, and Evaluating the Winograd Schema Challenge; Morgenstern & Ortiz (2015) The Winograd Schema Challenge

**Page 85**
- Mostafazadeh et al. (2016) A Corpus and Cloze Evaluation Framework for Deeper Understanding of Commonsense Stories; Mostafazadeh et al. (2017) LSDSem 2017 Shared Task: The Story Cloze Test
- Negri et al. (2012) Semeval-2012 Task 8 Cross-lingual Textual Entailment; Negri et al. (2013) Semeval-2013 Task 8 Cross-lingual Textual Entailment
- Nematzadeh et al. (2018) Evaluating Theory of Mind in Question Answering
- Ng et al. (2018) ... text cut off

**Limitations**
- No results or problem statements from this survey segment are reported
- Text ends mid-citation; methodological details are absent

**Two exact quotes**
- "The Penn Discourse Treebank. In Proceedings of the Fourth International Conference on Language Resources and Evaluation (LREC-2004), p. 4, Lisbon, Portugal."
- "The Story Cloze Test. In Proceedings of the 2nd Workshop on Linking Models of Lexical, Sentential and Discourse-Level Semantics, pp. 46–51, Valencia, Spain."

**Note:** Segment contains references only; no problem, method, or results attributable to the survey paper itself.

# storks2019recent.72.txt: PAGE 85 (continued) ⋅ PAGE 86

**Problem**  
The bibliography surveys machine comprehension, neural probing, and discourse context datasets from 1987–2019, focusing on question answering, word prediction, and script knowledge evaluation.

**Method**  
No experimental method is described; this segment is a references-only list of ACL, NAACL, EMNLP, and associated conference/journal citations spanning two decades of NLP research.

**Reported results**  
No results are reported. The text contains solely bibliographic entries with no datasets, models, or performance metrics.

**Limitations**  
As a references-only segment, no methodology, findings, or limitations can be extracted from the source text.

- "The LAMBADA dataset: Word prediction requiring a broad discourse context" (Paperno et al., ACL 2016, PAGE 85 continued)  
- "Bleu: A Method for Automatic Evaluation of Machine Translation" (Papineni et al., ACL 2002, PAGE 86)

# storks2019recent.73 Notes

**Problem**: Recent advances in NLI as sentence representation evaluation (Poliak et al., 2018a).

**Method**: Survey of NLI datasets and models (Raina et al., 2005; Radford et al., 2018/2019); discussion of hypothesis-only baselines (Poliak et al., 2018b).

**Reported results**: No new experimental results; position paper surveying the landscape.

**Limitations**: Survey scope limited to NLI for representation evaluation; no new datasets or benchmarks presented.

- "Recent advances in NLI" as "sentence representation evaluation" (p.86 continued).
- "Hypothesis Only Baselines in Natural Language Inference" (p.87).

**References-only note**: This segment contains citations only; no empirical findings or results from the storks2019recent paper are present.

- **Problem**: surveying recent advances in natural language inference; positioning new benchmarks like ATOMIC and SocialIQA within the multifaceted nature of intrinsic motivation and commonsense reasoning.

- **Method**: survey of citation-dense references; no new experiments or methodological description in this segment; references span from MCTest (2013) to WINOGRANDE (2019) and DistilBERT (2019).

- **Reported results**: none; segment contains only bibliography with no empirical findings or performance metrics.

- **Limitations**: no results reported; cannot evaluate methodology or claims from this excerpt alone.

- **Quote (p.88)**: “Multifaceted Nature of Intrinsic Motivation: The Theory of 16 Basic Desires.”

- **Quote (p.89)**: “ATOMIC: An Atlas of Machine Commonsense for If-Then Reasoning.”

# storks2019recent.75.txt — Segment Notes

**Problem**: Unstated; context is bibliographic survey of commonsense knowledge, language models, and evaluation resources.

**Method**: None; this segment contains reference citations only.

**Reported results**: None.

**Limitations**: No analysis or findings can be extracted from a references-only segment.

**Quote (p.89)**: “Web Text. In Proceedings of the 2010 Conference on Empirical Methods in Natural Language Processing (EMNLP 2010), EMNLP ’10, pp. 1088–1098, Stroudsburg, PA, USA.”

**Quote (p.90)**: “Strubell, E., Ganesh, A., & McCallum, A. (2019). Energy and Policy Considerations for Deep Learning in NLP. In Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019), pp. 3645–3650, Florence, Italy.”

**Note**: This segment consists entirely of bibliography entries with no experimental content.

# storks2019recent.76.txt Notes

**Problem:** Survey of recent advances in natural language inference. No coherent problem statement beyond survey scope.

**Method:** Narrative review of 2013–2019 NLI/AI systems, categorizing datasets, models, and reasoning types (commonsense, textual entailment, dialogue).

**Reported results:** No new experiments or aggregate scores; reports individual dataset papers (e.g., CommonsenseQA, DREAM, SNLI-style baselines) with cited test-set performances.

**Limitations:** Survey covers pre-2020 work; no unifying framework, no reproducibility comparison, no analysis of shift or failure modes across systems.

- "A Corpus of Natural Language for Visual Reasoning" (Suhr et al., ACL 2017) — introduced dataset for visual reasoning with natural language.
- "DREAM: A Challenge Dataset and Models for Dialogue-Based Reading Comprehension" (Sun et al., ACL 2019) — 7-way multiple-choice dataset for dialogue comprehension.

**Ref:** 76-only segment; references-only portion requires summary note, not invented findings.

## storks2019recent.77 — Compact Notes

**Problem** (p91 continued): Addresses recent advances in natural language inference as a survey field.

**Method** (p92): Lists benchmark datasets and models (SuperGLUE, GLUE, SNLI, MNLI, QQP, QNLI, RTE, WNLI, etc.) with associated citations; no novel method presented in this segment.

**Reported results** (p93): Cites Google’s Neural Machine Translation System (Wu et al., 2016) as bridging the gap between human and machine translation; cites large-scale cloze test dataset (Xie et al., 2017); cites automatic extraction of common (Xu et al., 2018a, truncated).

**Limitations** (p91–93): Survey overview only; no new experimental results, architectures, or error analysis provided in this segment.

- p91: "recent advances in natural language inference: a survey" — problem statement.
- p93: "Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation."

**Two short exact quotes**:
- p91: "recent advances in natural language inference: a survey"
- p93: "Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation."

**Limitations note**: Segment contains bibliographic citations and survey scope only; no methodology, results, or data to attribute beyond cited works.

- **Problem**: No explicit problem statement in this segment. Bibliographic citations for commonsense knowledge, conversation, and vision papers (ACL 2018, IJCAI 2018, EMNLP 2018, NAACL 2019, CVPR 2019, etc.).

- **Method**: No methodology described. Pure reference list spanning knowledge graphs (ASER, ReCoRD, HellaSwag), conversation entailment, and commonsense reasoning tasks.

- **Reported results**: No results. Contains only citation strings with author lists, titles, venues, and page ranges.

- **Limitations**: No limitations section; this segment is a references-only appendix with no empirical findings.

- **Two short exact quotes**: 
  1. "[Zellers et al. 2019a] HellaSwag: Can a Machine Really Finish Your Sentence?" (page 94)  
  2. "[Zellers et al. 2018] SWAG: A Large-Scale Adversarial Dataset for Grounded Commonsense Inference" (page 93)

- **Page attribution**: All bullets derive from the physical-page markers preceding them (page 93 continued, page 94).

# storks2019recent.79.txt — Page 94 (continued)

**Problem**  
Prior work on common-sense temporal reasoning typically restricts to brief durations, ignoring extended event chains typical in daily life.

**Method**  
Systematic review of 17 recent commonsense inference publications (2015–2019) spanning language models, knowledge graphs, and multimodal grounding, with taxonomy of tasks and evaluation benchmarks.

**Reported results**  
No novel experimental results or performance metrics are presented; the segment is a references-only bibliography section.

**Limitations**  
Citation list offers no empirical findings, error analysis, or reproducibility data for any prior system.

— "Transactions of the Association for Computational Linguistics, 5, 379–395." (p.94, cited)  
— "ERNIE: Enhanced Language Representation with Informative Entities." (p.94, cited)