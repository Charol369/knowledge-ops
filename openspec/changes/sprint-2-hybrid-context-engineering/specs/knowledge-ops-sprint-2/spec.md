# knowledge-ops-sprint-2 Specification

## ADDED Requirements

### Requirement: Hybrid retrieval
The system SHALL combine dense and sparse retrieval candidates using RRF and support reranking with a Cross-Encoder stage.

#### Scenario: Hybrid retrieval returns fused evidence
- **WHEN** a query is submitted to hybrid retrieval
- **THEN** dense and BM25 candidates are fused and returned in ranked order with citation metadata.

### Requirement: Query transformation
The system SHALL support HyDE, Multi-Query, and Query Decomposition as independent query transformation strategies.

#### Scenario: Query expansion produces retrievable variants
- **WHEN** a complex research query is transformed
- **THEN** the system produces expanded or decomposed query variants without requiring agent graph orchestration.

### Requirement: Context Builder
The system SHALL assemble bounded, citation-ready context from retrieval results and prior artifacts.

#### Scenario: Evidence becomes prompt context
- **WHEN** retrieval returns evidence chunks
- **THEN** Context Builder deduplicates, orders, budgets, and formats the evidence for synthesis.

### Requirement: Retrieval evaluation baseline
The system SHALL provide a RAGAS dataset scaffold and runner for local evaluation.

#### Scenario: Evaluation can be dry-run locally
- **WHEN** the evaluation runner is invoked in dry-run mode
- **THEN** it validates dataset and pipeline wiring without fabricating metric results.
