# KnowledgeOps Product API Contract

Date: 2026-06-22

Status: Draft for review

## 1. API Design Goals

The API must support a real enterprise knowledge-base question-answering product, not only a local demonstration.

API principles:

1. Stable request/response schemas.
2. Explicit session, trace and diagnostics fields.
3. Intent and strategy are first-class response fields.
4. LLM, retrieval and tool fallback reasons are visible.
5. Normal users should not manually provide trace IDs.
6. Future auth/ACL can be added without breaking query contracts.

## 2. Versioning

Base path:

```text
/api/v1
```

Breaking changes should use:

```text
/api/v2
```

## 3. Common Types

### 3.1 Citation

```json
{
  "source": "data/attention_is_all_you_need.pdf",
  "page": 4,
  "snippet": "Multi-head attention allows the model..."
}
```

Fields:

| Field | Type | Required | Notes |
|---|---|---:|---|
| `source` | string | yes | normalized source URI/path |
| `page` | integer/null | no | source page if available |
| `snippet` | string/null | no | short supporting evidence |

### 3.2 QueryIntent

```json
{
  "intent": "definition",
  "confidence": 0.91,
  "rewrite": "What is multi-head attention?",
  "needs_tool": false,
  "strategy": "hybrid_retrieval"
}
```

Allowed intents for P0:

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

### 3.3 Diagnostics

```json
{
  "strategy": "hybrid_retrieval",
  "tool_name": null,
  "tool_status": null,
  "retrieval_top_k": 5,
  "fallback_reason": null,
  "latency_ms": 1234,
  "token_usage": {
    "prompt_tokens": 1000,
    "completion_tokens": 200
  }
}
```

Diagnostics should be returned when:

```text
include_diagnostics=true
```

or in local/dev mode by default.

## 4. Query API

### 4.1 `POST /api/v1/query`

Purpose:

```text
Run one enterprise knowledge-base question-answering request.
```

Current implementation exists, but should be extended to this target contract.

Request:

```json
{
  "question": "What is multi-head attention in Attention Is All You Need?",
  "session_id": "optional-client-session",
  "document_filters": {
    "document_ids": ["doc_attention"],
    "source_type": "pdf",
    "tags": ["paper"]
  },
  "options": {
    "include_diagnostics": true,
    "stream": false,
    "embedding_backend": "hash"
  }
}
```

Current compatibility fields:

| Current field | Keep? | Target migration |
|---|---:|---|
| `thread_id` | temporary | replace normal UI usage with `session_id`; keep API backward compatibility |
| `docs_dir` | dev only | move under options/admin context |
| `index_dir` | dev only | move under options/admin context |
| `embedding_backend` | dev only | move under options |

Target response:

```json
{
  "answer": "Multi-head attention consists of several attention layers...",
  "confidence": 0.85,
  "intent": "definition",
  "strategy": "hybrid_retrieval",
  "plan": [
    {
      "step_id": "1",
      "description": "Identify local evidence...",
      "status": "completed"
    }
  ],
  "citations": [
    {
      "source": "data/attention_is_all_you_need.pdf",
      "page": 4,
      "snippet": "Multi-head attention allows..."
    }
  ],
  "model_tier_used": "tier3",
  "synthesis_mode": "llm",
  "synthesis_status": "ok",
  "synthesis_model": "deepseek-v4-pro",
  "synthesis_blocked_reason": null,
  "tool_name": null,
  "tool_status": null,
  "tool_result": null,
  "session_id": "sess_...",
  "trace_id": "trace_...",
  "request_id": "req_...",
  "artifact_session_id": "20260622T...",
  "needs_human_review": false,
  "diagnostics": {
    "retrieval_top_k": 5,
    "fallback_reason": null
  }
}
```

Error or blocked response should still be HTTP 200 when the request was processed but the knowledge answer is unavailable:

```json
{
  "answer": "The knowledge base does not contain enough information to answer this.",
  "confidence": 0.0,
  "intent": "no_answer",
  "strategy": "blocked",
  "citations": [],
  "needs_human_review": true,
  "diagnostics": {
    "fallback_reason": "No references section was located."
  }
}
```

HTTP errors are reserved for invalid request/auth/server failures:

| Code | Meaning |
|---:|---|
| 400 | malformed request |
| 401 | missing/invalid API key |
| 403 | permission denied |
| 422 | schema validation error |
| 429 | rate limit |
| 500 | unhandled server error |

## 5. Streaming Query API

### 5.1 `POST /api/v1/query/stream`

Purpose:

```text
Run the same query contract with progress events.
```

Current implementation emits bounded SSE progress and completion events. It is not token-level streaming yet.

Event sequence:

```text
progress: accepted
progress: intent_classified
progress: retrieval_started
progress: synthesis_started
progress: graph_completed
completion: QueryResponse
```

P0 may keep the current shorter sequence:

```text
progress: started
progress: graph_completed
completion
```

Target progress event:

```json
{
  "stage": "intent_classified",
  "trace_id": "trace_...",
  "intent": "count",
  "strategy": "reference_count_tool"
}
```

## 6. Document APIs

### 6.1 `POST /api/v1/documents/ingest`

Purpose:

```text
Start an ingestion job.
```

Request:

```json
{
  "source_type": "local_directory",
  "path": "data/company_docs",
  "tenant_id": "default",
  "build_index": true,
  "embedding_backend": "hash"
}
```

Response:

```json
{
  "job_id": "ingest_...",
  "status": "queued",
  "documents_seen": 12,
  "blocked_reason": null
}
```

Current compatibility:

```text
Existing /api/v1/ingest can remain as local/admin compatibility endpoint.
New product endpoint should wrap it or replace it after schema stabilization.
```

### 6.2 `GET /api/v1/documents`

Purpose:

```text
List documents visible to the current user/admin.
```

Response:

```json
{
  "documents": [
    {
      "document_id": "doc_...",
      "title": "Attention Is All You Need",
      "source_type": "pdf",
      "source_uri": "data/attention_is_all_you_need.pdf",
      "version_hash": "sha256:...",
      "status": "ready",
      "chunks_count": 93,
      "updated_at": "2026-06-22T00:00:00Z"
    }
  ]
}
```

### 6.3 `GET /api/v1/documents/{document_id}`

Purpose:

```text
Inspect one document and its index status.
```

Response:

```json
{
  "document_id": "doc_...",
  "title": "...",
  "source_uri": "...",
  "status": "ready",
  "sections": [
    {
      "section_id": "sec_...",
      "title": "3.2 Attention",
      "page_start": 3,
      "page_end": 4
    }
  ],
  "index_status": {
    "dense": "ready",
    "sparse": "ready",
    "metadata": "ready"
  }
}
```

## 7. Feedback API

### 7.1 `POST /api/v1/feedback`

Current endpoint exists.

Target request:

```json
{
  "trace_id": "trace_...",
  "score": 1.0,
  "comment": "Useful answer.",
  "source": "web-ui",
  "labels": ["correct", "well-cited"]
}
```

Target response:

```json
{
  "status": "ok",
  "trace_id": "trace_...",
  "storage": "local-memory",
  "langfuse_status": "recorded",
  "blocked_reason": null
}
```

P1 target:

```text
Persist feedback to Postgres and optionally promote reviewed feedback to eval dataset.
```

## 8. Diagnostics APIs

### 8.1 `GET /health`

Current endpoint exists.

Target response:

```json
{
  "status": "ok",
  "version": "0.0.1",
  "dependencies": {
    "vector_store": "ok",
    "llm_provider": "ok",
    "metadata_store": "ok"
  }
}
```

### 8.2 `GET /api/v1/diagnostics/provider`

Purpose:

```text
Inspect current configured model provider without exposing secrets.
```

Response:

```json
{
  "status": "ok",
  "base_url_hash": "ca6e900ccdd0",
  "models": ["deepseek-v4-pro", "deepseek-v4-flash"],
  "active_synthesis_model": "deepseek-v4-pro"
}
```

This endpoint should require admin/API key access.

## 9. Backward Compatibility Plan

| Current field/endpoint | Target |
|---|---|
| `thread_id` | keep as alias for `session_id` during transition |
| `docs_dir` | dev/admin option only |
| `index_dir` | dev/admin option only |
| `/api/v1/ingest` | keep local compatibility; add `/api/v1/documents/ingest` |
| Streamlit manual trace field | move to advanced/debug panel |

## 10. Review Questions

1. Should diagnostics be returned by default in local mode only, or always returned?
2. Should `POST /api/v1/query` expose `docs_dir/index_dir` after product hardening?
3. Should document ingestion be synchronous for local MVP or always queued?
4. Should feedback immediately enter eval data, or require manual approval?
5. Should provider diagnostics be exposed through API or only CLI script?

## 11. P0 API Acceptance

P0 API work is complete when:

- `/api/v1/query` returns `intent` and `strategy`.
- `/api/v1/query` returns `synthesis_blocked_reason` when fallback happens.
- `/api/v1/query/stream` emits at least started/graph_completed/completion with the expanded response.
- Normal UI no longer requires manual trace ID.
- Existing tests pass and new API schema tests cover intent/tool/fallback fields.
