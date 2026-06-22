# KnowledgeOps Product Workflows

Date: 2026-06-22

Status: Draft for review

## 1. Workflow Goals

This document defines the target workflows for a real enterprise knowledge-base question-answering system.

The system must support two independent but connected flows:

```text
Offline / async ingestion flow:
source documents -> parsed documents -> chunks -> indexes -> eval artifacts

Online query flow:
user question -> intent/strategy -> retrieval/tool -> LLM synthesis -> verification -> trace/feedback
```

The current project already supports a single online path. The target workflow must become intent-aware and tool-augmented.

## 2. Principles

1. Deterministic work stays deterministic.
2. LLMs synthesize and classify; they must not be trusted for ACL, counts, sums, or source existence.
3. Permissions must be applied before context reaches any LLM.
4. Answers without supporting evidence must say evidence is insufficient.
5. Every response must be traceable to request, evidence, model, fallback and citations.

## 3. Offline Ingestion Workflow

### 3.1 Target Flow

```text
1. receive source configuration
2. sync or upload source files
3. compute document_id and version_hash
4. skip unchanged documents
5. persist raw document
6. parse into canonical document blocks
7. normalize text and metadata
8. detect sections, tables, figures and references
9. split into chunks
10. attach source/page/section/block/ACL metadata
11. extract optional LLM metadata
12. build dense embeddings
13. build sparse index
14. build metadata/section/reference indexes
15. run ingestion quality checks
16. publish index version
17. record ingestion artifact and trace
```

### 3.2 Current Project Mapping

| Step | Current status | Gap |
|---|---|---|
| Load local PDF/Word/HTML | implemented | no real connector or upload workflow |
| Parse page text | implemented for PDF basics | no layout/table/reference parsing |
| Chunk text | implemented | no stable document/chunk schema |
| Embedding | implemented path | default smoke still uses hash backend |
| Sparse search | local BM25 | not service-scale |
| Vector index | FAISS/Milvus path | production Milvus path not fully used by query |
| Metadata/ACL | weak | no ACL or metadata filters |
| Ingestion jobs | missing | no async job model |

### 3.3 Ingestion States

```text
created
syncing
parsed
chunked
indexed
ready
blocked
failed
deleted
```

### 3.4 Ingestion Failure Handling

| Failure | Expected behavior |
|---|---|
| Unsupported file type | mark document blocked, keep reason |
| Parser failure | mark failed with parser error |
| Empty text | mark blocked, no index write |
| Embedding failure | retry if transient, otherwise failed |
| Index write failure | retry and keep prior index version active |
| Deletion | tombstone document and remove chunks from indexes |

## 4. Online Query Workflow

### 4.1 Target Flow

```text
1. receive query
2. create request_id / trace_id / session_id
3. authenticate user
4. load tenant/user/group permission context
5. normalize question
6. run pre-LLM guardrails
7. classify query intent
8. choose retrieval/tool strategy
9. rewrite/decompose query if needed
10. execute retrieval or deterministic tool
11. apply ACL and metadata filters
12. rerank and deduplicate evidence
13. build citation-aware context
14. run LLM synthesis if needed
15. verify citations and schema
16. run post-answer safety checks
17. persist trace/artifacts/usage
18. return answer, citations and diagnostics
19. collect feedback
```

### 4.2 Current Query Flow

Current implemented flow:

```text
question
-> intent_router
-> planner
-> retrieval_orchestrator / tool dispatch
-> dense + BM25 + RRF OR reference_count_tool OR section_lookup_tool OR blocked table path
-> context_builder
-> LLM synthesis if enabled
-> reporter
-> citation verifier
-> response
```

Current gap:

```text
No ACL filtering.
No production embedding/rerank verification.
No persisted query trace store beyond artifacts/local metrics.
Streamlit diagnostics panel exists for intent/tool/fallback fields, but no persistent query trace table exists yet.
P0 intent eval artifact exists for 5 deterministic workflow cases; larger product QA eval set remains P1.
```

## 5. Intent-based Workflows

### 5.1 `definition`

Example:

```text
What is multi-head attention?
```

Workflow:

```text
classify definition
-> hybrid retrieval
-> rerank
-> context builder
-> LLM synthesis
-> citation verifier
```

Acceptance:

```text
intent=definition
strategy=hybrid_retrieval
synthesis_mode=llm
citations valid
```

### 5.2 `section_summary`

Example:

```text
Summarize section 3.2.
```

Workflow:

```text
classify section_summary
-> section_lookup_tool
-> retrieve section blocks
-> context compression if long
-> LLM synthesis
```

Blocked behavior:

```text
If section cannot be located, return blocked reason instead of summarizing unrelated chunks.
```

### 5.3 `count`

Example:

```text
How many references are in Attention Is All You Need?
```

Workflow:

```text
classify count
-> identify count target: references
-> reference_count_tool
-> deterministic count
-> LLM explanation with tool result
-> citation verifier
```

Acceptance:

- Count is produced by code, not guessed by the LLM.
- If the reference section is unavailable, return blocked reason.

### 5.4 `list`

Example:

```text
List the datasets used in the experiments.
```

Workflow:

```text
classify list
-> query decomposition if needed
-> targeted retrieval
-> extraction
-> LLM synthesis with citations
```

Acceptance:

- Output is a list.
- Partial evidence must be marked as partial.

### 5.5 `compare`

Example:

```text
Compare policy A and policy B.
```

Workflow:

```text
classify compare
-> decompose into subject A and B
-> parallel retrieval
-> align evidence by dimensions
-> LLM synthesis
```

Acceptance:

- Answer cites both sides.
- Missing side is explicitly reported.

### 5.6 `table_query`

Example:

```text
What does Table 2 show?
```

Workflow:

```text
classify table_query
-> table_lookup_tool
-> blocked path in P0 because table parsing/indexing is unavailable
```

Acceptance:

- Do not use normal top-k RAG if table structure is available.
- If table parsing is unavailable, return blocked reason.

### 5.7 `no_answer`

Example:

```text
What is the author's private salary?
```

Workflow:

```text
classify no_answer or evidence_insufficient
-> minimal retrieval
-> if no support, return insufficient evidence
```

Acceptance:

- No invented answer.
- `needs_human_review` may be true for ambiguous cases.

## 6. Feedback Workflow

```text
user submits feedback
-> validate trace_id
-> record local metric
-> record Langfuse score if enabled
-> include feedback in later eval dataset
```

Current status:

```text
/api/v1/feedback implemented.
Local Langfuse score smoke verified.
Feedback is not yet persisted in production DB.
```

## 7. Evaluation Workflow

Target flow:

```text
qa dataset
-> run query for each case
-> collect answer/citations/intent/strategy
-> check expected sources/pages/tool results
-> optional LLM-as-judge
-> write eval artifact
```

Minimum product eval dimensions:

| Dimension | Required |
|---|---|
| Intent correctness | yes |
| Retrieval source/page hit | yes |
| Citation validity | yes |
| No-answer behavior | yes |
| Tool result correctness | yes |
| LLM answer quality | P1 |
| Cost/latency | P1 |

## 8. Observability Workflow

Each query should record:

```text
trace_id
session_id
request_id
user_id or anonymous user
intent
strategy
retrieval top sources
tool result
synthesis_mode
synthesis_model
synthesis_status
fallback_reason
latency_ms
token_usage
cost estimate
citations_count
needs_human_review
```

Current gap:

```text
Some values exist in response or local metrics, but there is no persistent query trace table yet.
```

## 9. Review Questions

1. Should `count` intent first support only references, or all numbered/list/table counts?
2. Should section parsing be PDF-only first, or shared across PDF/HTML/DOCX?
3. Should feedback become part of evaluation data automatically, or require manual review first?
4. Should query diagnostics be visible to normal users or only in an advanced/debug panel?
5. Should the first production-like deployment use local Docker Compose or a cloud VM?

## 10. P0 Workflow Acceptance

Implementation design and task breakdown:

```text
Step 6 technical design: docs/p0-intent-routing-design.md
Step 7 task breakdown: docs/p0-implementation-plan.md
```

P0 workflow enhancement is complete when:

- Query response includes `intent` and `strategy`.
- `definition` questions still return `synthesis_mode=llm`.
- Reference count questions use a deterministic tool.
- Section lookup questions do not rely on unrelated top-k chunks.
- Fallback reason is visible in API and UI.
- Tests cover normal, blocked and fallback paths.

Current implementation boundary:

```text
Task 1-8 are implemented: API/graph schema, deterministic router, reference count tool, section lookup tool, table blocked path, graph strategy dispatch, deterministic tool-result answer pinning, Streamlit advanced diagnostics, and P0 intent eval artifact.
Task 9-10 remain pending until final docs sync, validation, commit, and push are complete.
```
