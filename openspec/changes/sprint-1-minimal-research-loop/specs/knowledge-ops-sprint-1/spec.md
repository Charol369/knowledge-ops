# knowledge-ops-sprint-1 Specification

## ADDED Requirements

### Requirement: Local ingestion baseline
The system SHALL ingest PDF, Word, and HTML documents into normalized documents with metadata suitable for citation and retrieval.

#### Scenario: PDF pages preserve evidence metadata
- **WHEN** a PDF is loaded
- **THEN** each resulting document includes `source` and `page` metadata where available.

### Requirement: Dense retrieval baseline
The system SHALL build and persist a FAISS dense index and expose a dense retrieval interface using k=5.

#### Scenario: Query returns dense evidence
- **WHEN** the CLI or service submits a research query
- **THEN** the dense retriever returns up to 5 evidence chunks with source metadata.

### Requirement: Minimal research loop
The system SHALL run a local question -> plan -> retrieve -> synthesize -> answer loop and persist plan, evidence, and final answer artifacts.

#### Scenario: CLI completes local research
- **WHEN** a user submits a question to the CLI loop
- **THEN** the system creates a minimal plan, retrieves evidence, synthesizes an answer, and writes session artifacts.

### Requirement: Ingest API skeleton
The system SHALL expose `/api/v1/ingest` as a skeleton endpoint without authentication in Sprint 1.

#### Scenario: Ingest endpoint exists without Sprint 4 security
- **WHEN** the API is started locally
- **THEN** `/api/v1/ingest` is routable but does not yet enforce API key auth or rate limiting.
