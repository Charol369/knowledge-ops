---
change: sprint-3-agent-graph-mcp
status: draft
---

# Sprint 3 Technical Design: LangGraph Agent Graph + MCP Tool Layer

## Objective
Implement the KnowledgeOps cognitive chain as a graph and expose it through stable API/MCP interfaces.

## Architecture Slice
- Cognitive Agent Layer: LangGraph nodes and graph state.
- Guardrails foundation: structured output and citation validation only.
- MCP Server: retrieval/synthesis tool boundary.
- API Layer: `/api/v1/query` graph entrypoint.

## Scope
Sprint 3 owns agent graph composition and MCP/API wiring, not production policy, auth, rate limiting, observability hardening, streaming, or final demo assets.

## Constraints
- Sprint 1-2 retrieval/context/artifact contracts must be stable.
- Manual Claude Desktop setup should be documented but not treated as automated code delivery.
- Do not bypass citation validation to pass tests.

## Acceptance
Sprint 3 is acceptable when local API/MCP paths can invoke the graph and structured, cited output is validated.
