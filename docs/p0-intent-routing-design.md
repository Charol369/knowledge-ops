# P0 Intent-Aware QA Core Design

Date: 2026-06-22

Status: Design ready for implementation

## 1. Goal

This document defines the P0 technical design for upgrading KnowledgeOps from a single-path RAG query flow to an intent-aware enterprise knowledge-base QA core.

P0 target:

```text
question
-> classify intent
-> choose retrieval/tool strategy
-> execute deterministic retrieval/tool
-> synthesize answer when needed
-> verify citations
-> return answer + citations + diagnostics
```

The next implementation round must make the system answer common enterprise knowledge-base questions more reliably without expanding into P1/P2 infrastructure work.

## 2. Requirements Covered

| Requirement | Covered in this design | Notes |
|---|---:|---|
| P0-R1 Query Intent Router | yes | Classify core intents with deterministic rules first; optional LLM router remains future work. |
| P0-R2 Intent-aware graph routing | yes | Graph state carries intent/strategy/tool diagnostics and routes to retrieval/tool paths. |
| P0-R3 Reference count tool | yes | Deterministic reference counting for paper/reference-list questions. |
| P0-R4 Section lookup tool | yes | Deterministic section lookup before synthesis for section questions. |
| P0-R5 Automatic session/trace | already done | Existing implementation remains unchanged. |
| P0-R6 API diagnostics | yes | Response returns intent, strategy, tool status and fallback reason. |
| P0-R7 LLM synthesis stability | reused | Existing structured LLM synthesis and deterministic fallback remain the generation layer. |
| P0-R8 Regression tests | yes | Unit, integration and API smoke matrix defined below. |

## 3. Non-goals

These are explicitly out of scope for this P0 slice:

| Non-goal | Reason |
|---|---|
| Postgres metadata store | Data model exists, but local artifacts are sufficient for P0 routing validation. |
| Enterprise ACL | Must be designed before multi-user deployment, but does not block local intent/tool routing. |
| Real bge-m3 Docker runtime | Retrieval correctness should be validated first with current hash/local path. |
| Real RAGAS answer-quality run | P0 needs deterministic regression first; RAGAS belongs after stable intent outputs. |
| Locust 100 QPS | Throughput is not the bottleneck until correctness is stable. |
| Cloud deployment | Deployment follows stable workflow and Docker reproducibility. |
| Next.js rewrite | Current Streamlit UI is enough for local product validation. |
| General table parser | P0 can classify `table_query` and return a precise blocked reason if table parsing is unavailable. |

## 4. Current Baseline

Current implemented query path:

```text
question
-> planner
-> retrieval_orchestrator
-> dense + BM25 + RRF
-> context_builder
-> LLM synthesis if enabled
-> reporter
-> citation verifier
-> QueryResponse
```

Current gaps:

| Gap | Impact |
|---|---|
| `QueryResponse` does not return `intent` / `strategy` / `tool_*` diagnostics | The caller cannot tell why a path was chosen or why fallback happened. |
| `AgentState.intent` exists but is not populated by an explicit router | Graph cannot route by question type. |
| All questions use the same retrieval path | Count/section/table questions may retrieve plausible but insufficient chunks. |
| No deterministic reference count tool | The system must not ask the LLM to guess counts. |
| No section lookup tool | Section questions can be answered from unrelated top-k chunks. |
| No product intent regression set | Future edits can silently break core workflows. |

## 5. Core Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Router implementation | Rule-first deterministic router | P0 needs predictable tests and no extra external LLM dependency. |
| LLM router | Not required for P0 | Can be added later for ambiguous enterprise questions. |
| Count handling | Deterministic tool first | Counts must not be inferred by LLM synthesis. |
| Section handling | Deterministic lookup first | Section lookup should narrow evidence before generation. |
| Table handling | Classify and block when unsupported | Better to return a clear blocked reason than hallucinate table contents. |
| Graph integration | Add an intent router node before retrieval/tool execution | Keeps routing observable and keeps retrieval/tools deterministic. |
| API compatibility | Extend response fields without breaking existing request fields | Existing clients using `thread_id`, `docs_dir`, `index_dir` continue to work. |
| Evidence model | Use current `source`, `page`, `snippet/content` fields for P0 | Stable document/block IDs can be added later. |

## 6. Intent Taxonomy

P0 router must return one of:

```text
definition
section_summary
count
list
compare
table_query
no_answer
unknown
```

### 6.1 Intent Routing Table

| Intent | Example | Primary signal | Strategy | Tool | LLM synthesis |
|---|---|---|---|---|---|
| `definition` | `What is multi-head attention?` | `what is`, `define`, concept question | `hybrid_retrieval` | none | yes |
| `section_summary` | `Summarize section 3.2.` | `section`, numeric section pattern, `summarize` | `section_lookup` | `section_lookup_tool` | yes if evidence found |
| `count` | `How many references are in the paper?` | `how many`, `number of`, `count`, target=`references/citations` | `reference_count` | `reference_count_tool` | optional explanation only |
| `list` | `List the datasets used in experiments.` | `list`, `what datasets`, `which methods` | `targeted_retrieval` | none in P0 | yes |
| `compare` | `Compare encoder and decoder attention.` | `compare`, `difference between`, `versus` | `hybrid_retrieval` | none in P0 | yes |
| `table_query` | `What does Table 2 show?` | `table`, `Table 1/2/...` | `table_lookup` | blocked in P0 if parser unavailable | no if blocked |
| `no_answer` | `What was the author's private salary?` | private/unsupported domain or retrieval evidence insufficient | `blocked` or `minimal_retrieval` | none | no unsupported answer |
| `unknown` | Ambiguous question | no strong signal | `hybrid_retrieval` | none | yes if evidence exists |

### 6.2 Router Output Schema

Internal model:

```python
class QueryIntentResult(BaseModel):
    intent: str
    strategy: str
    confidence: float
    normalized_question: str
    tool_name: str | None = None
    route_reason: str | None = None
    target: str | None = None
```

Allowed `strategy` values:

```text
hybrid_retrieval
targeted_retrieval
section_lookup
reference_count
table_lookup
blocked
```

## 7. LangGraph Workflow Design

### 7.1 Target Graph

P0 graph should become:

```text
START
-> intent_router
-> planner
-> route_by_intent
   -> retrieval_orchestrator
   -> reference_count_tool
   -> section_lookup_tool
   -> blocked_answer
-> synthesizer
-> reporter
-> verifier
-> END
```

P0 may keep the existing `planner` before retrieval if the implementation risk is lower, but the intent router must run before routing decisions.

Recommended implementation order:

```text
START -> intent_router -> planner -> query_executor -> synthesizer -> reporter -> verifier -> END
```

Where `query_executor` is a deterministic dispatch node that calls:

```text
hybrid retrieval
reference_count_tool
section_lookup_tool
table blocked path
```

This avoids complex conditional edges in the first implementation and keeps tests simpler.

### 7.2 AgentState Additions

Add fields to `AgentState`:

```python
intent: str | None
strategy: str | None
intent_confidence: float | None
route_reason: str | None
tool_name: str | None
tool_status: str | None
tool_result: dict[str, Any] | None
fallback_reason: str | None
diagnostics: dict[str, Any] | None
```

Field ownership:

| Field | Written by | Read by |
|---|---|---|
| `intent` | `intent_router_node` | planner, executor, API, UI |
| `strategy` | `intent_router_node` | executor, API, UI |
| `intent_confidence` | `intent_router_node` | API diagnostics |
| `tool_name` | router or executor | API diagnostics |
| `tool_status` | tool executor | API diagnostics |
| `tool_result` | tool executor | synthesizer/reporter/API |
| `fallback_reason` | executor/synthesizer/verifier | API/UI |
| `diagnostics` | final response mapping | API/UI |

### 7.3 Dispatch Behavior

| Strategy | Executor behavior |
|---|---|
| `hybrid_retrieval` | Use current `RetrievalOrchestrator.gather_evidence()`. |
| `targeted_retrieval` | Use current retrieval path with optional future query rewrite. P0 can reuse hybrid retrieval and set strategy. |
| `reference_count` | Call `reference_count_tool`; skip normal top-k retrieval unless the tool needs document text. |
| `section_lookup` | Call `section_lookup_tool`; use returned section evidence as graph evidence. |
| `table_lookup` | Return blocked status if no table parser/index exists. |
| `blocked` | Return no-answer response with diagnostics and `needs_human_review` where appropriate. |

## 8. Tool Design

### 8.1 `reference_count_tool`

Purpose:

```text
Count references/citations deterministically from local document text, or return a precise blocked reason.
```

P0 target:

```python
class ReferenceCountResult(BaseModel):
    status: Literal["ok", "blocked"]
    count: int | None
    source: str | None
    page_start: int | None
    page_end: int | None
    evidence: list[dict]
    blocked_reason: str | None
```

Algorithm for local P0:

1. Load documents from `docs_dir` with existing loaders.
2. Find likely references section using heading patterns:
   ```text
   references
   bibliography
   works cited
   ```
3. Count reference entries with deterministic patterns:
   ```text
   [1] ...
   1. ...
   newline + author/year style fallback only if numbered patterns are unavailable
   ```
4. Return `status=ok` only when a reference section and countable entries are found.
5. Return `status=blocked` with a precise reason when section or entries cannot be located.

P0 limitation:

```text
Only reference-list count is required. General "count all tables/figures/entities" is P1.
```

### 8.2 `section_lookup_tool`

Purpose:

```text
Locate a requested section by heading/number and return section-scoped evidence before synthesis.
```

P0 target:

```python
class SectionLookupResult(BaseModel):
    status: Literal["ok", "blocked"]
    section_id: str | None
    section_title: str | None
    page_start: int | None
    page_end: int | None
    evidence: list[dict]
    blocked_reason: str | None
```

Algorithm for local P0:

1. Parse section target from question:
   ```text
   section 3.2
   Section 3.2.1
   summarize 3.2
   ```
2. Load local documents with existing loaders.
3. Detect heading candidates using line patterns:
   ```text
   3.2 Attention
   3.2.1 Scaled Dot-Product Attention
   ```
4. Collect text from heading start until next same-or-higher-level heading.
5. Return evidence chunks with source/page/snippet.
6. If section cannot be located, return `blocked_reason` and do not answer from unrelated top-k chunks.

P0 limitation:

```text
Section detection can be text-pattern based. Full layout-aware PDF parsing is P1/P2.
```

### 8.3 `table_lookup_tool`

P0 behavior:

```text
Classify table questions, but return a clear blocked diagnostic unless table parsing/indexing is available.
```

Reason:

```text
It is safer to say "table structure is not available in the current index" than to retrieve arbitrary nearby text and hallucinate table contents.
```

## 9. API Contract Changes

Extend `QueryResponse` with:

```python
intent: str | None = None
strategy: str | None = None
intent_confidence: float | None = None
tool_name: str | None = None
tool_status: str | None = None
tool_result: dict[str, Any] | None = None
fallback_reason: str | None = None
diagnostics: dict[str, Any] | None = None
```

Compatibility:

| Existing field | Keep |
|---|---:|
| `answer` | yes |
| `confidence` | yes |
| `plan` | yes |
| `citations` | yes |
| `synthesis_*` | yes |
| `session_id` | yes |
| `trace_id` | yes |
| `artifact_session_id` | yes |
| `needs_human_review` | yes |

SSE P0 event behavior:

```text
Keep existing started -> graph_completed -> completion sequence.
Add intent/strategy/tool fields to graph_completed when available.
Do not implement token-level streaming in this slice.
```

## 10. Answer Behavior

### 10.1 Supported Answer

For `definition`, `list`, `compare`, and successful `section_summary`:

```text
Use existing LLM synthesis when enabled.
Use deterministic fallback when LLM is unavailable.
Always cite retrieved evidence.
```

### 10.2 Deterministic Tool Answer

For successful `count`:

```text
The final answer must include the deterministic count from `tool_result`.
The LLM may explain the result but must not change the count.
If LLM synthesis fails, deterministic fallback must still answer with the count.
```

### 10.3 Blocked Answer

For unsupported table parsing, missing references, missing section, or insufficient evidence:

```text
Return an evidence-insufficient answer.
Set `tool_status=blocked` or `strategy=blocked`.
Set `fallback_reason` or `blocked_reason`.
Set `needs_human_review=true` when the user asked a valid question but the system lacks required structure.
```

## 11. Evaluation And Test Matrix

### 11.1 Unit Tests

| Test file | Coverage |
|---|---|
| `tests/unit/test_intent_router.py` | deterministic classification for all P0 intents |
| `tests/unit/test_reference_count_tool.py` | count success, missing references section, uncountable references |
| `tests/unit/test_section_lookup_tool.py` | section success, section missing, next-heading boundary |
| `tests/unit/test_agents.py` | graph state carries intent/strategy/tool fields |

### 11.2 Integration Tests

| Test file | Coverage |
|---|---|
| `tests/integration/test_query_api.py` | `/api/v1/query` returns intent/strategy/tool diagnostics |
| `tests/integration/test_streaming.py` | SSE completion includes diagnostics |
| `tests/integration/test_frontend_demo.py` | UI helper remains importable; no manual trace dependency |

### 11.3 Regression Questions

Minimum P0 regression set:

| Intent | Question | Expected |
|---|---|---|
| `definition` | `What is multi-head attention in Attention Is All You Need?` | `strategy=hybrid_retrieval`, citations present |
| `count` | `How many references are in Attention Is All You Need?` | `strategy=reference_count`, deterministic count or precise blocked reason |
| `section_summary` | `Summarize section 3.2 in Attention Is All You Need.` | `strategy=section_lookup`, section evidence or precise blocked reason |
| `table_query` | `What does Table 2 show?` | `strategy=table_lookup`, blocked if table parser unavailable |
| `no_answer` | `What was the author's private salary?` | insufficient evidence, no invented answer |

## 12. Implementation Boundaries

P0 implementation should touch only:

```text
src/api/schemas.py
src/api/routes.py
src/agents/graph.py
src/agents/planner.py
src/agents/orchestrator.py
src/agents/synthesizer.py
src/agents/reporter.py
src/agents/verifier.py
src/agents/intent_router.py
src/agents/tools.py or src/tools/*.py
src/retrieval/context_builder.py
frontend/app.py
tests/unit/*
tests/integration/*
docs/*
```

Avoid touching:

```text
Docker Compose stack
CI workflow
cloud deployment
Postgres migrations
ACL schema implementation
new frontend framework
large model download path
```

## 13. Acceptance Criteria

P0 Intent-Aware QA Core is complete when all are true:

- `/api/v1/query` returns `intent`, `strategy`, `tool_name`, `tool_status`, `tool_result`, `fallback_reason` or `diagnostics`.
- `/api/v1/query/stream` completion returns the same expanded fields.
- Definition questions still use the current hybrid retrieval + LLM/fallback synthesis path.
- Reference count questions do not use LLM guessing for the count.
- Section questions do not answer from unrelated top-k chunks when the section cannot be located.
- Table questions return a precise blocked reason until table parsing is implemented.
- No-answer questions avoid unsupported claims.
- Unit and integration tests cover success and blocked paths.
- Status docs are updated with evidence-backed claims only.

