# PaperForge - corrective build 0.3 (checkpointed end-to-end tested)

A dark chat interface based on assistant-ui's actual landing-chat components, with a FastAPI backend and PostgreSQL + pgvector. This source replaces the earlier upload-first prototype; it does not preserve all of that prototype's features.

## Current status (28 October 2026)

- An explicitly scoped latest-GraphRAG UI test automatically discovered/downloaded two2026papers, parsed28pages, stored196Voyage4/1024vectors in PostgreSQL/pgvector, read41native source segments, generated a compiling IEEE draft, and completed source review plus PDF/Word/source exports. This two-source fixture does not establish broad latest/foundational coverage.
- A subsequent explicit link added a26page GraphRAG paper (115vectors,23read segments) and one cited sentence only inside Conclusion. Every character outside that section was preserved. Final collection:3documents/311vectors. All exports returned HTTP200. IEEE1page and semantic Word3page renders were inspected; Word is not template pagination.
- Earlier independent live tests exercised Springer LNCS exports, history reload and other edits. The preserved scoped fixture still contains a planner title typo and ambiguous introductory attribution. Later guards were tested separately, not retroactively counted as original-run success.
-115isolated tests and the web production build pass. These are separate from the live tests.
- Budget-only source-reading and span-review limits now continue automatically within the same live backend job, with finite safety limits and verified checkpoint progress. Genuine model, integrity and semantic failures stop rather than entering a retry loop. Backend restarts still require explicit resume.
- Local controlled acceptance exercised both creation and new-link section editing across multiple reading/review slices: one ingestion/index, one draft or section patch, exact outside-section preservation, blocked exports on errors, and saved-patch resume without applying the change twice. This is orchestration evidence using stage substitutes, not another successful hosted model run.
- Reloaded chat status distinguishes a live job from a paused checkpoint and disables input while busy. It does not reattach the old live output stream; refresh after disconnected completion to load the saved response.
- Long model work can pause on timeouts or invalid output. `/resume` continues checkpoints without repeated source ingestion. The live creation needed multiple resumes and development corrections, so uninterrupted one-shot reliability is NOT established. Do not depend on this for an unattended deadline.
- Evidence review binds exact draft spans to physical-page quotations and rejects uncovered prose. Model entailment judgments can still be wrong. Review exports before submission. This is a literature-review tool, not a source of original experimental results.
- Single-user localhost development app only: no authentication, multi-user isolation, deployment hardening, manual upload UI, or cancellation. Keep it bound to 127.0.0.1. Never expose it directly to the internet. Closing a stream does not cancel backend work.
- Credentials and paper data are not included in this source package. Paid calls remain off by default; keys do not authorize spending.

## Prerequisites

Linux or a compatible development environment, Python 3.10+, Node/npm compatible with Vite 8, Docker (or an existing PostgreSQL 16 server with pgvector), OpenCode CLI, Pandoc 2.11+ (3.6.4 tested), and these commands on PATH:

```
pdflatex bibtex pdftotext pdftoppm pdfinfo pandoc soffice
```

Install the command-line packages through your OS package manager. The IEEEtran/LNCS class and bibliography files are bundled; base LaTeX packages are still required.

## Run locally

From the project root:

```
cp .env.example .env
# Fill DATABASE_URL and your own credentials/settings locally. Never commit .env.
docker compose up -d db
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
npm install -g opencode-ai
opencode models
```

Choose an explicit `PAPERFORGE_MODEL=provider/model` in `.env`. The owner-selected default is nvidia/nvidia/nemotron-3.5-lightning-30b-a3b using NVIDIA_API_KEY, not OpenCode Zen or DeepSeek. Direct Q&A uses the same key at NVIDIA with API model nvidia/nemotron-3.5-lightning-30b-a3b. Free endpoints have provider-specific privacy policies, trial limits and availability; free does not mean confidential or guaranteed. Configure provider authentication in OpenCode as its documentation describes.

Voyage is the default embedding provider (`voyage-4`, 1024 dimensions). Set `VOYAGE_API_KEY`. For scanned PDFs set `UNSTRUCTURED_API_KEY` and the endpoint shown in your Unstructured account. These are separate services and keys.

Hosted embedding/OCR requests remain disabled until `PAPERFORGE_HOSTED_CALLS=enabled`. Enabling them can incur provider charges. Check account limits and billing first. App-side usage counters are not provider account spending caps, and concurrent use elsewhere is not counted.

```
set -a; . ./.env; set +a
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, from the project root:

```
cd web
npm ci
npm run dev
```

Open http://127.0.0.1:5173. Choose IEEE/Springer, then enter a topic. It is a template selector, not an LLM selector. The API does not create tables during a read unless explicit initialization is enabled. First have the database owner enable pgvector (`CREATE EXTENSION vector`) and authorize a dedicated `paperforge` schema. For initial setup only, set PAPERFORGE_DB_INITIALIZE=enabled; after setup set it back to disabled. All app table queries are qualified into PAPERFORGE_DB_SCHEMA; public/system schemas are rejected. Existing public tables are not reused. A database initialized with another embedding model must not be reused without re-embedding or a fresh database.

## Orchestrator (LangGraph, default) and claim checker (Laya, default)

Each chat turn goes through a LangGraph `StateGraph` (`backend/app/orchestrator/`). Claims are checked by Laya (`laya==0.4.17`, in `requirements.txt`), run on CPU in short-lived worker processes; the first check downloads about 843 MB of weights, and on machines under 6 GB RAM a low-memory loader is used automatically. The final message says the claims are model-assessed, not verified. No setup flags are needed. To roll back, set `PAPERFORGE_ORCHESTRATOR=legacy` and `PAPERFORGE_CLAIM_CHECKER=legacy` (the previous router and LLM claim review).

```
fast_route -> scope | resume | edit | ask          slash commands, resume and questions: no model call
fast_route -> classify (forced Intent tool call)
classify -> find_agent <-> find_tools -> find_report   search only; nothing is downloaded, indexed or written
classify -> ask_consent -> consent (interrupt) -> write_paper
classify -> clarify
```

- `find papers ...` only searches arXiv/OpenAlex through LangChain tools that the graph executes (max 2 rounds) and lists candidates.
- A paper is written only on an explicit write request ("write a literature review on ...") or after a yes to the consent question. Unclear input gets a clarifying question, never a run.
- The consent question is a LangGraph `interrupt`; the checkpoint lives in Postgres schema `paperforge_lg` and survives a restart. `threads.phase` stays the source of truth, and `write_paper` refuses to start unless the phase is `new` or `failed_early`.
- Model: the owner's NVIDIA model through `langchain-nvidia-ai-endpoints`. That endpoint rejects `with_structured_output` and `max_retries`, so intent uses a forced tool call. Hosted calls still need `PAPERFORGE_ANSWER_CALLS=enabled`; without them, rules decide and the graph only searches or asks.
- OpenCode is unchanged: it still does the file editing and drafting. The claim review is unchanged; LangGraph does not verify claims. An unresolved span is never marked verified and the draft downloads stay labelled "not verified".

What the graph owns today, and what is still the previous code:

| Stage | Owner |
| --- | --- |
| Turn routing, intent classification, find_papers search loop, write consent and its checkpoint | LangGraph |
| Fresh paper run: discover/index, read, draft, build+claim review, export | One LangGraph node per stage (`discover`, `read`, `draft`, `build_review`, `export`), conditional edges stop at the first failed stage |
| The code inside each stage (plan, OpenCode file work, drafting, claim review, build, export) | Existing `pipeline.py` / `drafting.py` / `review.py`, unchanged; `run_create` (legacy) calls the same stage functions |
| Scope clarification, ask (retrieval + answer + citation check), edit, resume of a paused run | Existing functions, called as one graph node each |

Stage context (project root, plan, session) is held in process memory during a run. After a restart the run is picked up through `threads.phase` and `/resume`, exactly as before. Only the consent question is checkpointed in Postgres. Stages are not yet re-entrant graph nodes, and `ask`, `edit` and `resume` are not decomposed.

## Workflow and provenance

arXiv API and OpenAlex open-access works search provide candidates. A PDF link is not evidence that the paper was downloaded. Downloads are checked for a PDF header, extracted per page with pdftotext, optionally sent to hosted Unstructured for OCR, chunked with page/source IDs, embedded, and stored under the thread's collection. Every retrieval SQL query filters `thread_id`.

OpenCode processes full source-text segments into notes, then returns source-specific draft prose. The app assembles escaped LaTeX syntax, citations and tables. The code writes refs.bib from indexed-source metadata. Full available author lists are preserved. Undefined citations trigger the build-fix loop. The review stage uses retrieval for claim checks, but is not a deterministic proof of factual correctness. Search metadata and DOI values can be wrong; there is no independent DOI registry/liveness validation. Firecrawl optionally provides separately labeled public-web context alongside OpenAlex/arXiv. It is not processed-paper evidence or a citation source.

Artifacts, once successfully generated, are linked in the chat: PDF, Word, LaTeX ZIP. Data/checkpoints live in `backend/data` by default. `/resume` continues paused reading, drafting, build, review and export checkpoints without repeating source discovery or embeddings. No partial notes silently satisfy full reading. Per-stage budgets bound each slice. A finite in-process loop now continues budget-only slices with verified increasing progress, without another user message. It does not automatically retry provider/model errors, semantic or purpose failures, integrity failures, or no-progress states. A256slice ceiling stops extreme jobs. `/resume` remains explicit recovery for those pauses or a restarted process.

Q&A uses a direct hosted OpenAI-compatible API, separate from OpenCode. The owner-selected default for both routes is NVIDIA Nemotron 3.5 Lightning 30B A3B, authenticated by NVIDIA_API_KEY, with thinking disabled. Q&A uses the NVIDIA direct API and create/edit use native OpenCode. Explicitly enable PAPERFORGE_ANSWER_CALLS only after checking free allowance/billing controls. No fallback provider is used.

## Tests

```
cd backend
python -m unittest discover -s tests -v
cd ../web
npm run build
```

Tests use synthetic data/mocks and a local fake sleeping process for the watchdog. They make no model, embedding or OCR API calls. A separate development check used real PostgreSQL 16 + pgvector 0.6.2, two synthetic source collections with identical vectors, and verified each retrieval returned only its own chat. Embeddings in that test were synthetic, not Voyage outputs. The route tests verify Q&A uses the direct adapter without OpenCode/project writes, while edit invokes OpenCode (mocked). They do not establish end-to-end correctness.

## Optional: separate reviewer model

Drafting and answer generation use the default model. Claim review and per-sentence Q&A verification can run on a different model: set `PAPERFORGE_REVIEW_MODEL=provider/model` (and, for a rate-limited free account, `tools/bounded-review-proxy.py`, which caps requests and stops on the first upstream error; it does not log auth headers). This was tested once with Groq `openai/gpt-oss-120b`; it is not required.

## Ownership by person (proposed, going forward)

This is how the work is divided from now on. It says nothing about who wrote what so far; for that, use the git history. Names are placeholders until filled in. Shared code is split by feature, not dumped on one person: whoever's feature needs a change in a shared file makes it.

| Owner | Area | Files |
| --- | --- | --- |
| Yash | Complete frontend, final PDF/Word build, deployment files | `web/`; `backend/app/latexbuild.py`, `backend/app/templates/`; `Dockerfile`, `RAILWAY.md`, `.env.example`, `tools/docker-entrypoint.sh`; tests `check_exports.py` |
| Person 2 | Sources, retrieval and long-running jobs: discovery, URL/PDF ingestion, chunking, embeddings, pgvector, retrieval, job resume | `backend/app/research.py`, `source_links.py`, `firecrawl.py`, `transform.py`, `db.py`, `rag.py`, `voyage_guard.py`, `evidence.py`, `scope.py`, `jobs.py`, `continuation.py`; the source and job endpoints in `main.py`; the discovery and reading stages in `pipeline.py` (`plan`, discovery, ingestion); tests `test_discovery_guard.py`, `test_candidate_classifier.py`, `test_firecrawl.py`, `test_source_links.py`, `test_transform.py`, `test_embedding_validation.py`, `test_voyage_guard.py`, `test_scope.py`, `test_evidence.py`, `test_continuation.py`, `test_budget_integration.py`, `check_postgres.py`, `check_schema.py` |
| Person 3 | Drafting and verification: drafting, model runner, claim review, Q&A | `backend/app/drafting.py`, `sections.py`, `section_purpose.py`, `limitations.py`, `structured.py`, `opencode.py`, `span_review.py`, `answering.py`; the chat, edit and ask endpoints in `main.py`; message routing and the drafting, review and export-orchestration stages in `pipeline.py`; tests `test_drafting.py`, `test_limitations.py`, `test_section_purpose.py`, `test_structured.py`, `test_span_review.py`, `test_review_model.py`, `test_routes.py`, `test_resume_and_fallback.py`, `test_contract_wording.py`, `test_operational_outcomes.py` |
| Shared | Touch only with the feature owner's review | `config.py`, `test_core.py`, `README.md`, `requirements.txt`, `docker-compose.yml` |

What each person can demo on their own machine:
- Yash: the chat UI end to end, ending in the compiled PDF/Word (LaTeX runs on his laptop only).
- Person 2: add papers by search or URL, show the indexed chunks with page numbers, run retrieval for a question, and resume a paused job. No LaTeX needed.
- Person 3: draft a section, show claims marked supported or unresolved with evidence, and ask a question answered with page citations. No LaTeX needed.

## Credits

Web chat components copied from assistant-ui commit 42ec2ba61de4361a31a1cefb4b2daf131fe8f63e (MIT license in licenses/assistant-ui-MIT.txt), then adapted for PaperForge. Source: https://github.com/assistant-ui/assistant-ui. Template notices are in backend/licenses.

### Tested workflow and limits

The live test used these sources returned by automatic discovery:
- https://arxiv.org/pdf/2305.16243v3
- https://arxiv.org/pdf/2504.05324v1

Read-only Q&A used direct NVIDIA and did not change the TeX hash. Creation/edit/review used native OpenCode with the owner's NVIDIA key. Source reading, drafting and evidence judgments are bounded inline stages with tools disabled. Edits use exact model-produced replacement patches, validated before application. Source metadata writes BibTeX deterministically. Generated TeX is compiled with shell escape disabled and restrictive local file I/O; suspicious direct file-reading/writing primitives are rejected. These are defenses, not a complete hostile-document sandbox.

Discovery checkpoints preserve successful results and indexed sources. arXiv 429 responses stop subsequent uncached arXiv requests and save a one-hour backoff; OpenAlex can continue within verified free allowance. Firecrawl results remain web context, never processed-paper evidence.

Voyage pacing uses the official model-specific tokenizer, a conservative 8,000-token sliding window, 22-second spacing and a shared PostgreSQL reservation queue. The account test showed 3 RPM/10,000 TPM. A persisted model/dimension/input-type/content cache preserves successful batches. App counters do not cap provider account charges or other applications. Verify current account billing before enabling any hosted service.

Known limitations: review text can be conservative or repetitive; model outputs can fail valid JSON or exact-span edits; full new-topic reliability beyond the tested sources is unproven; reload shows the actual server running/paused state, but does not reattach live output; refresh after completion loads saved history; no manual upload; no publication-quality fact guarantee. Source-internal numeric disagreements should be preserved, not silently reconciled.

### Process restart behavior

Run the backend as a normal long-lived local process. It has one in-process background job per active chat, not an external job service. Checkpoints are persisted to PostgreSQL and the local data directory; keep both. A killed backend does not automatically restart its job. Restart it and send `/resume` in the same chat. Completed source reads/draft spans are reused. An edit interrupted before a validated patch is saved repeats that edit from its pending request; after a patch is saved, resume builds/reviews the saved draft. Model stages are not transactional with the database, so process-crash timing can repeat a bounded model call. Charges, if enabled by the operator, are not exactly-once.

Checkpointed live tests, compiler/export checks and isolated recovery tests passed. Uninterrupted fresh-topic reliability remains unverified. A resumed test is not evidence of unattended success.

### New link into a named section (build36)

An explicit edit such as `/edit Add https://arxiv.org/abs/... to section 7A` resolves the actual existing section first. A missing/ambiguous section asks for correction before downloading. Numeric references, 7A/7.1 subsections, and exact section titles are supported. The link must be a public HTTPS academic PDF or a landing page with citation PDF metadata. Private-network URLs, paid/paywalled access, oversized files and unknown citation titles fail closed.

The app downloads/parses the PDF, embeds page chunks in the current chat's pgvector collection, reads source segments with the same native model, and supplies notes plus source-scoped vector evidence to the edit. Per-URL checkpoints and content hashes reuse completed ingestion. New sources must be cited inside the requested section. Exact patch bounds protect every character outside that section, including against later build/review changes. Bibliography entries and the rendered reference list can grow as expected. `/resume` continues interrupted ingestion/editing.

This path has 108 isolated tests total, including a synthetic PDF parse/index checkpoint test and an integrated mocked new-link→evidence→section patch test. Public live arXiv landing metadata/PDF resolution passed for https://arxiv.org/abs/2504.05324 (19 physical pages). The subsequent build37 validation below exercises the full new-link path; resolver success alone does not establish that larger claim.

### Core link/section live validation (build37)

Actual UI test added https://arxiv.org/abs/2404.16130 to the existing Conclusion:26physical pages,23/23source segments read, pgvector ingestion, one model-written paragraph,19/19review spans, and all PDF/Word/source downloads returned200. Original TeX prefix/suffix outside Conclusion were byte-identical. Reference list/citation numbering grew as expected. This required bounded resumes and development corrections, not an uninterrupted new-topic proof. Native model additions now return bounded plain prose; the app supplies exact LaTeX citations and preserves existing section text for add requests.

New-source direct Q&A now returns structured sentences linked to retrieved evidence IDs; the app supplies their actual source/page labels. A real UI answer on GraphRAG community summaries cited physical page6, was checked against that source page, and left TeX unchanged. This reduces page-label invention; it is still not a deterministic semantic-entailment guarantee. Surname-first citation metadata is normalized before BibTeX generation.

Existing reviewed spans survive addition of a new source only when their exact text, prior complete source-text subset hash, and current physical-page quotations match. This prevents unrelated review drift without treating stale/changed sources as validated.

### Latest-topic discovery preparation (build38)

The planner now returns bounded inline JSON with tools disabled instead of depending on model file writes. Invalid plans use an explicitly labeled prompt-derived fallback. For latest/recent/advancements requests, discovery requests date-sorted results from arXiv/OpenAlex for focused queries while retaining a foundational relevance query; ranking adds a bounded recent-year preference. This avoids silently treating "latest" as ordinary citation-count ranking. Date ordering is not proof that every recent important paper was found. Broad new-topic latest GraphRAG live discovery-to-export remains unverified on this revision.

Build39: a wholly fresh actualUI latest-GraphRAG test produced a valid inline plan, real arXiv/OpenAlex discovery, and Firecrawl context (3results/2pages). It selected and extracted a41page survey; embedding/indexing remains incomplete, so this is not a new draft/export pass. Discovery now reuses pending source rows/downloads on resume and rejects future-year metadata before ranking. Date-sorted candidates do not ensure that the selected set covers recent advances. Existing broad-topic retrieval coverage and source-selection quality still need validation.

### Scope clarification (build40)

Unqualified graph-based RAG creation now asks which family is intended before discovery: LLM/document question answering with knowledge graphs, or retrieval for graph foundation/graph prediction models. The explicit reply is kept alongside the original request. An explicit LLM/document scope filters clear graph-prediction-only candidates. Actual UI clarification was exercised without provider calls. This is a narrow research-family guard, not a general semantic relevance classifier. The older broad GraphRAG test is preserved as ambiguous, not counted as a successful LLM-GraphRAG run; its indexed survey is not discarded. A fresh explicitly scoped latest-LLM-GraphRAG creation remains unverified.

Build41: actualUI scope reply explicitly chose LLM/document QA and global summarization. The app retained the original request plus reply and started new scoped discovery. It downloaded/extracted a2026core-hierarchy GraphRAG paper matching that scope; indexing/drafting is unfinished. Found planner output drift (RLL typo and old2023/2024query years) despite otherwise valid JSON. Planner now receives the current date and explicit exact-term/no-unrequested-year constraints; that final correction is isolated-tested, not yet live-retested. Clarification threads now persist a usable sidebar title. This is not a latest-coverage or final-paper success claim.

Build42: the explicitly scoped test read all41source segments from two2026papers, generated a compiling draft, and retained checkpoints through evidence review. Review detected an overbroad comparison-table result. Table repairs now accept typed plain-text cells while preserving the original source citation and table structure;108isolated tests pass. The app subsequently passed14/14review spans and exported files. Visual inspection found a readable one-page IEEE layout but retained the RLL typo, source-attribution defects and a comparison claim that had been rejected on one review attempt and accepted on a later one. This is not publication readiness or stable semantic validation. The planner typo and weak introductory attribution in this preserved test remain defects, not corrected output.

Build43: semantic span rejections are persisted by exact draft span and complete source-content hash. An unchanged rejected span goes back to repair rather than receiving a fresh favorable judgment on retry, even if another cache entry exists. Valid changed text is reviewed again; reverting restores the block. Invalid/time-out review responses remain retryable. New source-specific introductions/conclusions with ambiguous self-attribution are blocked before assembly. These guards are isolated-tested, not a promise of complete semantic correctness.

The scoped test produced downloadable PDF/Word/source exports (all returned HTTP200). Visual inspection found readable one-page IEEE and two-page semantic Word output, with the known title and attribution defects retained. A direct Q&A attempt failed the evidence-linked response check without changing the TeX; a second actual UI attempt returned source/physical-page citations that matched pages4and13, again without changing TeX. This exposes remaining model-format variability, not an unbroken success claim.

Build44: planner output that changes requested RAG to RLL or adds unrequested year filters to a latest/recent search is rejected into the visible prompt-derived fallback, rather than silently repaired. Source framing explicitly includes authors; ambiguous self-attribution triggers one bounded native-model retry and then blocks assembly if still present. This covers summary, abstract, introduction and conclusion. A separate guarded draft using the existing two-source notes succeeded without those ambiguous self-attribution phrases; the preserved original test/output was not rewritten.108isolated tests pass. That separate draft has not been claim-reviewed or exported, and does not prove uninterrupted discovery-to-export reliability.

Build45: tool-free native stages now use an inline evidence-worker instruction rather than inheriting contradictory file-writing instructions. A live source-reading retry advanced from2to6segments after a prior response returned only an output filename; this is bounded evidence of the fix, not a reliability guarantee. The scoped thread has downloaded/parsed/indexed the additional26page GraphRAG source (using the existing account content cache where applicable), with9/23native source segments read so far. The existing TeX remained unchanged while source reading was incomplete.108isolated tests pass.

Build46: scoped new-link Conclusion edit completed23/23source reads,15/15review spans and all exports returned HTTP200. Existing text outside Conclusion was byte-identical. Collection:3documents,311vectors, voyage-4/1024. Final one-page IEEE and three-page semantic Word renders were inspected; Word places the third reference on its own page. The preserved title/intro defects remain. New-source Q&A retrieval succeeded but the direct provider returned an HTTP error; TeX was unchanged. Provider errors now distinguish rate limit, refused access and temporary server failure without exposing response bodies.108isolated tests pass. This does not establish uninterrupted core-flow reliability.

Build47: named-paper Q&A can restrict vector retrieval to a uniquely identified indexed source key, exact title, full author name, or explicit author/source reference. Ambiguous surnames and generic domain terms keep whole-chat scope. The actual UI Edge-source question returned only Edge physical-page citations after this change; TeX remained unchanged. Source pages2and6support the main map/reduce explanation. The response still repeats part of the explanation, so concise answer quality remains imperfect. Earlier format and provider failures remain recorded, and a later successful retry is not an uninterrupted reliability pass.108isolated tests pass.

Build48: a separate native planner check returned a valid RAG title and focused queries without old-year filters. The separately regenerated guarded two-source draft completed12/12review spans and PDF/Word/source export after bounded retries, without changing the preserved original fixture. A semantic rejection persisted until a changed typed-cell table repair was accepted, exercising the rejection latch live. Table review now explicitly distinguishes evaluated tasks from reported outcomes; table repairs request only method/evaluation fields. Review reasons are requested under30words to reduce malformed verbose responses.108isolated tests pass.

The separate output was visually inspected: no clipping, but the narrow comparison-table cells are tall and Word breaks a long word awkwardly. It also contains an author-name spelling error in one introduction sentence and excessive IEEE vertical spacing. These are quality defects, not a final-ready artifact. The successful review is not proof against attribution typos or layout flaws. This separate fixture did not repeat source discovery or test the final revision as one uninterrupted creation.

Build49: draft comparison cells and repaired table cells are bounded to8words/100characters. Oversized draft cells receive one native compacting attempt; invalid output blocks assembly. A conservative source-name spelling guard detects near-spelled author tokens and altered surnames after exact given-name prefixes, asks one native repair, then blocks rather than silently correcting names. This is not a general identity/name validator. IEEE drafting uses ragged-bottom layout to avoid stretched vertical gaps.108isolated tests pass.

A new separate layout fixture exercised the spelling repair live and produced compact comparison cells. Its one-page IEEE and two-page semantic Word preview were inspected: no observed clipping or awkward table word-breaking, and excessive vertical stretch was removed. This latest layout fixture is not claim-reviewed yet; it must not be presented as final reviewed output. The earlier reviewed fixture and original flawed UI fixture remain preserved independently.

Build50 validation: the latest separate layout/name-guarded fixture completed13/13review spans and PDF/Word/source export after further bounded retries and model-written table/limitations repairs. Updated IEEE1page and Word2page renders were inspected again: compact table and readable layout, no observed clipping. The evidence-limitations section still contains a method description after repair rather than a useful limitation, illustrating a remaining section-purpose/prose-quality defect. This is not a fresh discovery-to-export test, an uninterrupted success, or a scientific quality guarantee. No original fixture was silently replaced.

Build51 focused acceptance: Evidence limitations now has a separate purpose gate after claim evidence review. A method description or solved background issue alone cannot satisfy that section merely because its facts are supported. A native purpose verdict rejected the preserved wrong-purpose fixture. One bounded source-grounded repair replaced only that section using Hossain physicalp9future work and FuseRAG physicalp11memory-granularity trade-off. Outside-section text was byte-identical. The revised fixture passed the independent purpose verdict,13/13claim spans and export checks; updated IEEE/Word pixels were inspected. This is a narrow model-judged gate, not general section-quality proof. A failed purpose gate stops publication; automatic purpose repair is not implemented. Invalid verdicts remain blocked but retryable.108isolated tests pass. No discovery/embedding was repeated, and this focused test does not establish uninterrupted fresh-topic reliability.

Build52 budget-only orchestration: source reading and claim review expose typed budget-progress checkpoints. An ordinary persistent local process automatically advances these slices while saved progress increases. Each stage/call remains bounded, and a256slice ceiling prevents an unbounded loop. Model/provider errors, semantic/purpose rejections, integrity errors, no progress and process death are not auto-retried by this mechanism. A single mocked creation invocation crossed three one-segment slices and reached exports without additional user requests; isolated tests also exercise provider-error/no-progress/integrity stops and review-budget continuation.108isolated tests pass. No hosted discovery/embedding/model calls were used in this phase.

The UI polls the local server's current execution state every2seconds. After reload it reports running vs paused/process-ended and prevents typing into the composer while work is running. It does not claim automatic process-restart recovery or live-output reattachment. Output completed while disconnected still needs a refresh. Browser checks with a mocked local API exercised running-to-paused state and screenshots were inspected. This phase closes routine budget-only manual orchestration, not provider reliability or uninterrupted fresh-topic acceptance.

### Corrected drafting contract and status refresh (build54)

The frozen build53 fresh-topic live acceptance discovered/downloaded two speculative-decoding sources, indexed98vectors across24pages and completed20native source reads, but FAILED drafting: ambiguous self-attribution remained after the built-in repair. It did not reach final exports. Build54 removes the contradictory request for an introduction about "this paper" while retaining the attribution rejection guard. The UI requests current status immediately when its stream ends and ignores older overlapping status responses. These changes require a new frozen live acceptance; the failed run is not relabeled successful.

### Source-page limitations stage (build55)

Build54 failed the independent purpose gate after claim review accepted processing commentary as a limitation. Build55 requires a separate source-page limitation/scope selection with exact physical-page quotation before draft assembly. Processing/unsupported absence boilerplate is rejected; absent valid evidence blocks drafting, without a fabricated fallback. Claim and purpose checks remain required. This correction is not yet live-accepted.

### Evidence-ID source limitation contract (build56)

Build55 correctly stopped on an invented quote and invalid model schema. Build56 binds selected evidence IDs to original page excerpts in application code and independently checks every clause and limitation purpose before caching a sentence. Unknown IDs, invalid schemas, unsupported clauses and missing evidence still stop drafting. No schema synonym relaxation or guard removal. Live acceptance remains pending.

### Reviewed-method candidate coverage (build57)

Build56 stopped after proposing a background method limitation and then unavailable. Source inspection found an explicit reviewed-method limitation on arithmetic/compute resources in the PDF discussion. Build57 ranks explicit limitations/assumptions ahead of generic overlap, includes12page windows, and independently checks reviewed-method attribution. Optional limitation omission requires a separate successful complete-source absence assessment; provider/schema/retrieval failures do not omit content. Failed prior acceptances remain failed.

### Native schema-bound limitation stages (build58)

Installed OpenCode1.19.4 supports JSON-schema structured output through its loopback session API, not CLI event --format json. Build58 uses a bounded native helper for limitation selection/support/absence stages, allowing only StructuredOutput while denying filesystem/network tools. Same NVIDIA model/key; no direct-provider fallback. Local strict-schema tests and a synthetic native live check passed; real corrected-corpus acceptance is pending. Schema compliance is not semantic evidence, and independent support/purpose guards remain.

### Marked extractive limitation selection (build59)

Source inspection showed tradeoff/plateau passages underweighted by the prior candidate scorer. Build59 adds those signals and enumerates short source passages for ID selection, preserving original words in an explicitly marked attributed quotation rather than unmarked copied synthesis. Independent support/limitation-purpose checks remain mandatory. This corrects candidate coverage and removes free paraphrase as a source of extra claims; live acceptance remains pending.

### Selection input/provenance audit (build60, local verification only)

Actual failed59 model input omitted explicit SOURCE TITLE and ranked auto-regressive text as regression, passing80noisy passages. Build60 fixes explicit identity, word-boundary regression ranking and sentence-local top16selection. Unique per-attempt prompt/candidate/events storage prevents stale support files being mistaken for current results.123tests pass, including rendered identity/provenance and auto-regressive negative ranking. Real source acceptance is pending; build59failure remains failed.

### Bounded independent candidate classification (build61)

Replaces unreliable global limitation selection with at most4independent native schema classifications of deterministic explicit-signal source passages. Figure/table narration is excluded; positive/background/research-purpose checks stay required. Quotes remain marked and cited. Public-source component checks reached real Chen speedup-plateau and Leviathan arithmetic-cost tradeoffs; this is component evidence, not full-loop readiness.126local tests pass. Whole corrected-corpus acceptance remains pending.

### Saved-draft build checkpoint (build62)

Build61real corrected-corpus generation succeeded but a process restart during build regenerated the saved draft because phase remained draft_paused. Build62 checkpoints editing immediately after draft save so normal resume preserves build repairs and goes to build/review. Existing automatic draft is retained; this is recovery correction, not a fresh-run success claim.
