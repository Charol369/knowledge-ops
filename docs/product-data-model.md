# KnowledgeOps Product Data Model

Date: 2026-06-22

Status: Draft for review

## 1. Data Model Goals

This document defines the target product data model for KnowledgeOps.

The immediate implementation may still use local files and artifacts, but the model must be clear enough to migrate to Postgres/object storage/vector DB without redesigning the product.

Goals:

1. Stable document and chunk identity.
2. Version-aware ingestion.
3. Metadata and section-aware retrieval.
4. ACL-ready schema.
5. Query trace, feedback and eval persistence.
6. Evidence-backed answers and reproducible artifacts.

## 2. Entity Overview

```text
Tenant
User
Group
ACLPolicy

Document
DocumentVersion
DocumentBlock
Chunk
EmbeddingRecord
IndexVersion
IngestionJob

QuerySession
QueryTrace
Citation
Feedback

EvaluationCase
EvaluationRun
EvaluationResult
```

P0 does not require all tables to exist physically. It requires the schema to guide Pydantic models, artifacts and future Postgres migration.

## 3. Identity Rules

| Entity | ID rule |
|---|---|
| `tenant_id` | stable external ID or generated `tenant_...` |
| `user_id` | stable from auth provider; local MVP may use `anonymous` |
| `document_id` | deterministic hash of source URI + tenant, or stored generated ID |
| `version_id` | document_id + version_hash |
| `block_id` | version_id + block order/path |
| `chunk_id` | version_id + chunk order/hash |
| `trace_id` | generated per query request unless caller provides one |
| `session_id` | generated per conversation/session |
| `artifact_session_id` | local artifact run ID for files under `data/artifacts` |

## 4. Access Control Entities

### 4.1 Tenant

```text
tenants
- tenant_id: string primary key
- name: string
- status: active | disabled
- created_at: datetime
- updated_at: datetime
```

P0:

```text
Use tenant_id="default".
```

### 4.2 User

```text
users
- user_id: string primary key
- tenant_id: string
- email: string
- display_name: string
- status: active | disabled
- created_at: datetime
- updated_at: datetime
```

P0:

```text
Use user_id="anonymous" or API-key identity.
```

### 4.3 Group

```text
groups
- group_id: string primary key
- tenant_id: string
- name: string
- created_at: datetime
```

```text
user_groups
- user_id: string
- group_id: string
```

### 4.4 ACLPolicy

```text
acl_policies
- acl_policy_id: string primary key
- tenant_id: string
- visibility: public | tenant | group | private
- allowed_user_ids: json
- allowed_group_ids: json
- source_acl_hash: string
- created_at: datetime
- updated_at: datetime
```

Rule:

```text
ACL must be checked before evidence is sent to any LLM.
```

## 5. Document Entities

### 5.1 Document

```text
documents
- document_id: string primary key
- tenant_id: string
- source_type: local_file | upload | confluence | sharepoint | drive | git | url
- source_uri: string
- title: string
- mime_type: string
- status: created | ready | blocked | failed | deleted
- current_version_id: string
- acl_policy_id: string
- metadata: json
- created_at: datetime
- updated_at: datetime
```

Required metadata:

```json
{
  "author": null,
  "department": null,
  "tags": [],
  "language": "en",
  "page_count": 15
}
```

### 5.2 DocumentVersion

```text
document_versions
- version_id: string primary key
- document_id: string
- version_hash: string
- source_updated_at: datetime
- parser_name: string
- parser_version: string
- raw_object_uri: string
- parsed_object_uri: string
- status: parsed | indexed | blocked | failed
- blocked_reason: string nullable
- created_at: datetime
```

Purpose:

```text
Support incremental indexing and reproducible answers.
```

### 5.3 DocumentBlock

```text
document_blocks
- block_id: string primary key
- version_id: string
- document_id: string
- block_type: title | heading | paragraph | table | figure | reference | appendix | footer | unknown
- section_path: string
- page_start: integer nullable
- page_end: integer nullable
- order_index: integer
- text: text
- metadata: json
```

Examples:

```json
{
  "block_type": "reference",
  "section_path": "References",
  "page_start": 10,
  "metadata": {
    "reference_index": 38
  }
}
```

### 5.4 Chunk

```text
chunks
- chunk_id: string primary key
- version_id: string
- document_id: string
- tenant_id: string
- text: text
- source_uri: string
- page_start: integer nullable
- page_end: integer nullable
- section_path: string
- block_ids: json
- block_type: paragraph | table | reference | mixed
- token_count: integer
- acl_policy_id: string
- metadata: json
- created_at: datetime
```

Chunk metadata should include:

```json
{
  "source": "data/attention_is_all_you_need.pdf",
  "page": 4,
  "section_path": "3.2 Attention",
  "document_title": "Attention Is All You Need"
}
```

## 6. Index Entities

### 6.1 EmbeddingRecord

```text
embedding_records
- embedding_id: string primary key
- chunk_id: string
- model_name: string
- model_version: string
- vector_dim: integer
- vector_store: milvus | faiss | pgvector
- vector_ref: string
- created_at: datetime
```

### 6.2 IndexVersion

```text
index_versions
- index_version_id: string primary key
- tenant_id: string
- index_type: dense | sparse | metadata | section | reference | table
- backend: milvus | faiss | bm25 | opensearch | postgres
- status: building | ready | failed | retired
- documents_count: integer
- chunks_count: integer
- created_at: datetime
- activated_at: datetime nullable
```

Rule:

```text
Queries should read from active ready index versions.
```

## 7. Ingestion Entities

### 7.1 IngestionJob

```text
ingestion_jobs
- job_id: string primary key
- tenant_id: string
- source_type: string
- source_config_hash: string
- status: queued | running | completed | blocked | failed | cancelled
- documents_seen: integer
- documents_indexed: integer
- chunks_created: integer
- blocked_reason: string nullable
- error_message: string nullable
- created_at: datetime
- started_at: datetime nullable
- finished_at: datetime nullable
```

P0:

```text
Can be represented by JSON artifact.
```

P1/P2:

```text
Persist in Postgres and process through worker queue.
```

## 8. Query Entities

### 8.1 QuerySession

```text
query_sessions
- session_id: string primary key
- tenant_id: string
- user_id: string
- title: string nullable
- created_at: datetime
- updated_at: datetime
```

P0:

```text
Generate session_id automatically in UI/API.
```

### 8.2 QueryTrace

```text
query_traces
- trace_id: string primary key
- session_id: string
- tenant_id: string
- user_id: string
- question: text
- normalized_question: text
- intent: string
- strategy: string
- model_tier: string
- synthesis_mode: llm | deterministic_fallback | blocked
- synthesis_status: ok | failed | blocked | disabled
- synthesis_model: string nullable
- synthesis_blocked_reason: string nullable
- tool_name: string nullable
- tool_status: string nullable
- retrieval_top_k: integer nullable
- citations_count: integer
- confidence: float
- needs_human_review: boolean
- latency_ms: integer nullable
- token_usage: json nullable
- cost: numeric nullable
- artifact_session_id: string nullable
- created_at: datetime
```

Current status:

```text
Some fields exist in API response/artifacts, but no persistent table exists.
```

### 8.3 Citation

```text
citations
- citation_id: string primary key
- trace_id: string
- chunk_id: string nullable
- document_id: string nullable
- source_uri: string
- page: integer nullable
- snippet: text nullable
- support_status: valid | invalid | unknown
- created_at: datetime
```

### 8.4 Feedback

```text
feedback
- feedback_id: string primary key
- trace_id: string
- user_id: string nullable
- score: float
- comment: text nullable
- labels: json
- source: string
- langfuse_status: string nullable
- created_at: datetime
```

Current status:

```text
Local-memory feedback exists.
Langfuse score smoke exists.
Persistent feedback table does not exist.
```

## 9. Evaluation Entities

### 9.1 EvaluationCase

```text
evaluation_cases
- case_id: string primary key
- dataset_name: string
- question: text
- expected_intent: string nullable
- expected_sources: json
- expected_pages: json
- expected_answer_contains: json
- expected_tool_result: json nullable
- tags: json
- created_at: datetime
```

### 9.2 EvaluationRun

```text
evaluation_runs
- run_id: string primary key
- dataset_name: string
- git_commit: string
- config_hash: string
- status: running | completed | failed
- cases_total: integer
- cases_passed: integer
- created_at: datetime
- finished_at: datetime nullable
```

### 9.3 EvaluationResult

```text
evaluation_results
- result_id: string primary key
- run_id: string
- case_id: string
- trace_id: string nullable
- passed: boolean
- retrieval_hit: boolean nullable
- citation_valid: boolean nullable
- intent_correct: boolean nullable
- answer_score: float nullable
- failure_reason: string nullable
- created_at: datetime
```

P0:

```text
JSONL dataset and JSON result artifacts are sufficient.
```

P1/P2:

```text
Persist eval runs and trend quality over time.
```

## 10. Storage Mapping by Phase

### P0

| Entity | Storage |
|---|---|
| Raw docs | local `data/` |
| Chunks | in-memory / FAISS pickle |
| Query artifacts | `data/artifacts/` |
| Eval artifacts | `eval/results/` |
| Feedback | local memory + Langfuse smoke |

### P1

| Entity | Storage |
|---|---|
| Document metadata | Postgres or JSON artifact |
| Chunk metadata | Postgres or local JSON |
| Dense vectors | Milvus or FAISS |
| Sparse index | local BM25 or OpenSearch |
| Eval results | JSON artifacts |

### P2

| Entity | Storage |
|---|---|
| Metadata | Postgres |
| Raw docs | S3/MinIO |
| Vectors | Milvus/pgvector |
| Sparse search | OpenSearch/Elasticsearch |
| Jobs | Postgres + Redis queue |
| Trace/feedback | Postgres + Langfuse |

## 11. Migration Notes

The current code should not jump directly to full DB migration. Recommended sequence:

1. Introduce Pydantic models for Document/Chunk/QueryTrace.
2. Write local JSON artifacts using the target schema.
3. Update retrieval to carry `document_id`, `chunk_id`, `section_path`.
4. Add Postgres only after schema stabilizes.
5. Add ACL filters before exposing multi-user access.

## 12. Review Questions

1. Should `document_id` be deterministic from source URI or generated and stored?
2. Should chunks be stored in Postgres text columns, object storage, or vector DB metadata?
3. Should `QueryTrace` be persisted before introducing user auth?
4. Should `Feedback` become eval data automatically, or only after review?
5. Which storage migration should happen first: document metadata or query traces?

## 13. P0 Data Model Acceptance

P0 data model is complete when:

- Query response and artifacts include `intent`, `strategy`, `synthesis_*`, and `fallback_reason`.
- Chunks/evidence carry normalized `source`, `page`, and eventually `section_path`.
- Tool results can be represented as structured JSON.
- Eval datasets can assert expected intent, sources/pages and tool results.
- Data model docs are used before adding Postgres migrations.
