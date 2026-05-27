# knowledge-ops-sprint-5 Specification

## ADDED Requirements

### Requirement: Streaming query API
The system SHALL provide `/api/v1/query/stream` for SSE streaming of graph-backed query progress and final answer.

#### Scenario: Client receives streamed research response
- **WHEN** a client calls the stream endpoint
- **THEN** the system emits ordered SSE events for progress and completion.

### Requirement: Feedback capture
The system SHALL provide `/api/v1/feedback` to submit Langfuse-compatible scores when observability is configured.

#### Scenario: User feedback is recorded
- **WHEN** feedback is submitted with a trace identifier and score
- **THEN** the system records the feedback or returns a clear configuration error.

### Requirement: Demo application
The system SHALL provide a Streamlit demo for the primary KnowledgeOps research flow.

#### Scenario: Demo executes golden path
- **WHEN** the demo user submits a question
- **THEN** the UI shows answer, citations, and trace/session information where available.

### Requirement: Final evaluation and documentation
The system SHALL record final benchmark/evaluation results and README v2.0 only from executed commands and actual system behavior.

#### Scenario: Benchmark results are documented
- **WHEN** benchmark commands complete
- **THEN** README and benchmark docs report measured results without fabricated claims.

### Requirement: Manual delivery boundaries
The system SHALL distinguish code deliverables from manual actions such as cloud deployment, video recording/upload, resume finalization, and applications.

#### Scenario: Manual deliverable remains explicit
- **WHEN** Sprint 5 completion is reported
- **THEN** manual actions are listed separately and are not claimed as automated code output.
