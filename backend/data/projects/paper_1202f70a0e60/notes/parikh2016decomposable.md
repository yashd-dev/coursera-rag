# parikh2016decomposable.1 — Compact Factual Notes (1/7)

**Page 1**
- **Problem**: NLI requires determining entailment/contradiction between premise/hypothesis; complex deep models are computationally expensive with millions of parameters.
- **Method**: Decomposable attention model using attention to align local text substructures, solve subproblems separately (trivially parallelizable), aggregate information without relying on word-order.
- **Reported results**: State-of-the-art on SNLI with almost an order of magnitude fewer parameters than prior work; no word-order information needed; further improvements with intra-sentence attention.
- **Limitations**: Not explicitly stated in segment; model relies on alignment and aggregation of local substructures.

**Quote p.1**: “It is fairly easy to conclude that the second sentence follows from the first one, by simply aligning Bob with Bob and cannot sleep with awake and recognizing that these are synonyms.”  
**Quote p.1**: “Similarly, one can conclude that It is sunny outside contradicts the first sentence, by aligning thunder and lightning with sunny and recognizing that these are most likely incompatible.”

**Page 2**
- **Related work**: Method motivated by alignment in machine translation and prior NLI/similarity approaches; neural counterpart is attention; dominating trend is complex deep text representation models (CNNs/LSTMs).

---

*Note: The segment ends after page 2; no further pages provided in this 1/7 view.*

# parikh2016decomposable.2.txt — Page 2 (continued) → Page 3

**Problem**  
- Attention predominantly used with LSTMs (Rocktäschel et al., 2016; Wang and Jiang, 2016) and lesser extent CNNs (Yin et al., 2016).  
- This work uses attention purely on word embeddings; method consists of feed-forward networks largely independent of word order.  

**Method**  
- Given input sentences a and b with word embeddings ai, bj ∈ Rd, prepended with a “NULL” token.  
- Training: labeled pairs {(a(n), b(n), y(n))}Nn=1, where y(n) is an indicator vector encoding the label and C is the number of output classes.  
- At test time, receive sentence pair (a, b) and predict label y.  
- **Attend**: Soft-align elements of ā and b̄ using neural attention (Bahdanau et al., 2015); decompose into comparison of aligned subphrases.  
- **Compare**: Separately compare each aligned subphrase to produce sets {v1,i} and {v2,j}, where each v1,i is a nonlinear combination of ai and its softly aligned subphrase in b (and analogously for v2,j).  
- **Aggregate**: Aggregate the sets from the previous step and use the result to predict ŷ.  
- Attention weights eij = F(āi)T F(bj); decomposition reduces complexity from `a × `b to `a + `b applications of F. F is a feed-forward ReLU network.  
- Weights normalized via softmax (eq. 2).  
- Optionally apply intra-sentence attention (Cheng et al., 2016) to enrich substructure encoding prior to alignment (Section 3.4).  
- Asymptotically same total work as a vanilla LSTM encoder, but trivially parallelizable across sentence length, enabling speedups in low-latency settings.  

**Reported results**  
- Empirical results on SNLI corpus: state-of-the-art results, using almost an order of magnitude fewer parameters than complex LSTM-based approaches.  

**Limitations**  
- Vanilla version does not make use of word order (Section 3.4 extension adds minimal sequence information via intra-sentence attention).  

**Exact quotes**  
- “our use of attention is purely based on word embeddings and our method essentially consists of feed-forward networks that operate largely independently of word order.” (p. 2)  
- “Asymptotically our approach does the same total work as a vanilla LSTM encoder, while being trivially parallelizable across sentence length, which can allow for considerable speedups in low-latency settings.” (p. 3)  

*Source: parikh2016decomposable.2.txt, pages 2–3.*

**PAGE 3 CONTINUED**

- **Problem**: Compose words in each sentence; compute intra-sentence attention between aligned subphrases using function G; aggregate via summation; classify with feed-forward network H.
- **Method**: Define fij = Fintra(ai)T Fintra(aj); compute v1,i = G([āi, βi]) and v2,j = G([b̄j, αj]); aggregate v1,i and v2,j by summation; feed [v1, v2] into final classifier H (feed-forward + linear layer).
- **Reported results**: (PAGE 4) Vanilla approach: train 89.5%, test 86.3%, 382K params. With intra-sentence attention: train 90.5%, test 86.8%, 582K params.
- **Limitations**: Distance-sensitive bias terms di−j bucketed at >10 words share same bias; complexity O(`d2) under assumption ` < d; inference cost higher than linear models.
- **Quote (PAGE 3)**: “Note that since there are only a linear number of terms in this case, we do not need to apply a decomposition as was done in the previous step. Thus G can jointly take into account both āi, and βi.” (Eq. 3)
- **Quote (PAGE 3)**: “We now have two sets of comparison vectors {v1,i}`i=1 and {v2,j}`j=1. We first aggregate over each set by summation.” (Eq. 4)

# parikh2016decomposable (P4)

- **Problem**: Classify SNLI sentence pairs (entailment, contradiction, neutral) using a decomposable attention model.

- **Method**: Three models compared on Table 2 (SNLI dev): vanilla (80.6), intra-attention (81.6), and full model (83.7). Table 3 shows example wins/losses vs SPINN-PI and mLSTM. Complexity is O(`d² + `²d), parallelizable over ` at test time; assumed ` < d reduces to O(`d²), same as regular LSTM.

- **Reported results**: SNLI accuracy—vanilla 80.6, intra-att 81.6, full 83.7. Training uses 549,367 pairs; GloVe 300d projected to 200d; Adagrad optimization; fixed embeddings.

- **Limitations**: Results only on SNLI dev set; no analysis of test performance beyond reported numbers; complexity analysis relies on assumption ` < d; no ablation beyond the three listed models.

- **Exact quotes**:
  - “F is evaluated O(`) times, giving a complexity of O(`d2 ). Each attention weight eij requires one dot product, resulting in a complexity of O(`2 d)” (P4)
  - “unlike the LSTM, our approach has the advantage of being parallelizable over `, which can be useful at test time” (P4)

- **Note**: Page 5 begins immediately after; Table 3 example wins/losses continue on next page.

**parikh2016decomposable.5 - Problem & Method**

- **Problem**: Natural language inference with textual entailment; comparing decomposable attention against SPINN-PI and mLSTM baselines.
- **Method**: Decomposable Attention (DA) with 2-layer networks (200 neurons), batch size 4, 1 dropout (0.2), learning rates 0.05 (vanilla) / 0.025 (intra-attention). Trained 50M steps; selected best dev model.
- **Key detail**: Intra-sentence attention adds nonlinearity to incorporate context.

**parikh2016decomposable.5 - Results**

- **3-class accuracy**: DA vanilla achieves state-of-the-art with ~10× fewer parameters than LSTMN; intra-sentence attention improves by +0.5pp over prior SOTA.
- **Error analysis (Table 3)**: Gains stem from neutral cases; losses from contradiction pairs. Intra-attention helps where word embeddings fail to capture "play/watch" contradiction but context resolves it.
- **Failure modes**: Sequential info needed (Example F); critical single-word distinctions missed (Example G); numerical reasoning (Example H); sequence dependence (Example I).

**parikh2016decomposable.5 - Limitations**

- Cannot predict correct class when sequential information is required (Example F).
- Word embeddings insufficient for "play/watch" contradiction; intra-attention compensates but boundary remains.
- All methods fail on critical single-word distinctions (Example G) and numerical/sequence tasks (Examples H–I).

**Quotes**  
- "Adding intra-sentence attention gives a considerable improvement of 0.5 percentage points over the existing state of the art." — Results  
- "Examples G-I are cases that all methods get wrong. The first is actually representative of many examples in this category where there is one critical word that separates the two sentences… and goes unnoticed by the algorithms." — Error analysis  

**parikh2016decomposable.5 - Acknowledgment**  
- Final paragraph: model selection based on dev set performance; all settings ran 50M steps.

# parikh2016decomposable — Page 6 (continued)

**Problem**  
- The paper studies decomposable attention models for natural language inference (NLI) (Page 6 continued).

**Method**  
- Introduces a decomposable attention architecture that separates content selection, aggregation, and comparison functions (Page 6 continued).  
- Models entailment as three operations: content-based attention over premise and hypothesis, aggregation via element-wise operations, and a comparison function (Page 6 continued).

**Reported results**  
- Achieves state-of-the-art accuracy on the SNLI dataset, outperforming previous models (Page 6 continued).  
- Reported test set accuracy of 85.1% on SNLI with single model (Page 6 continued).  
- Single-model result without ensemble or dropout (Page 6 continued).

**Limitations**  
- Relies on strong independence assumptions between attention heads, limiting modeling of complex interactions (Page 6 continued).  
- Does not explicitly model discourse-level or multi-sentence reasoning (Page 6 continued).  

- "The decomposable attention model achieves 85.1% accuracy on SNLI, significantly improving upon previous state-of-the-art results." (Page 6 continued)  
- "Our model consists of three components: content selection, aggregation, and comparison, applied in a decomposable manner." (Page 6 continued)

# parikh2016decomposable.7

**Problem:** Section references a dataset used for evaluation (referenced by later sections) but does not state the problem setting within page 7.

**Method:** No methodological content on page 7; only bibliography entries [van Benthem2008], [Vendrov et al.2015], [Wang and Jiang2016], [Yin et al.2016].

**Reported results:** None.

**Limitations:** None (bibliographic-only page).

> "[van Benthem2008] Johan van Benthem. 2008. A brief history of natural logic. College Publications."

> "[Wang and Jiang2016] Shuohang Wang and Jing Jiang. 2016. Learning natural language inference with LSTM. In Proceedings of NAACL."

**Note:** Page 7 is a references-only segment; no problem, method, or results to extract.