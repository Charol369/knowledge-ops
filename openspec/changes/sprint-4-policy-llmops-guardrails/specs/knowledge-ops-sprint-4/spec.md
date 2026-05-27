# knowledge-ops-sprint-4 Specification

## ADDED Requirements

### Requirement: Policy routing
The system SHALL classify query complexity and route model/tool choices through a policy layer.

#### Scenario: Complex query uses policy decision
- **WHEN** a query enters the graph-backed API
- **THEN** complexity classification and model routing decisions are recorded and applied.

### Requirement: Reliability controls
The system SHALL provide cache, retry, and fallback behavior for model/retrieval operations where applicable.

#### Scenario: Transient failure uses fallback path
- **WHEN** a configured operation fails transiently
- **THEN** retry/fallback behavior is applied without hiding unsupported final failures.

### Requirement: Observability
The system SHALL integrate Langfuse-compatible tracing, propagate `trace_id` to API responses, and capture business metrics.

#### Scenario: API response includes trace id
- **WHEN** a graph-backed request completes
- **THEN** the API response includes a trace identifier for observability lookup.

### Requirement: Guardrails and API protection
The system SHALL normalize Unicode, classify injection risk, enforce API key authentication, and apply rate limiting.

#### Scenario: Protected endpoint rejects missing API key
- **WHEN** a protected endpoint is called without a valid API key
- **THEN** the request is rejected without leaking sensitive configuration.

### Requirement: Persistent checkpointing
The system SHALL support PostgresSaver as the production checkpoint backend.

#### Scenario: Postgres checkpointing is configured
- **WHEN** Postgres configuration is present
- **THEN** graph checkpointing uses PostgresSaver instead of MemorySaver.
