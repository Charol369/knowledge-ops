# Sprint 3 Design

## Objective
Turn the research workflow into a structured LangGraph agent graph and expose key capabilities through MCP and `/api/v1/query`.

## Scope
- LangGraph main graph refactor.
- Planner Node.
- Retrieval Orchestrator.
- Synthesizer.
- Reporter.
- Verifier / Reflection.
- Memory Checkpointer.
- Pydantic structured output.
- Citation enforcement and validation.
- MCP server integration with retrieval services and synthesizer.
- Claude Desktop integration test boundary.
- `/api/v1/query` connected to graph.
- ADR 004 and ADR 007.

## Constraints
- Requires Sprint 1-2 contracts for evidence, context, and artifacts.
- Do not implement Sprint 4 policy routing, auth, rate limiting, Langfuse hardening, or PostgresSaver migration in this Sprint.
- Claude Desktop setup is a manual integration action and cannot be assumed completed by code alone.

## Done When
- Graph nodes run in the documented order: plan -> retrieve -> synthesize -> report -> verify.
- `/api/v1/query` reaches the graph and returns structured output.
- Citations are required and validated against evidence metadata.
- MCP server exposes retrieval/synthesis capabilities suitable for local Claude Desktop configuration.
- ADR 004 and ADR 007 are recorded.

## Stop If
- Sprint 2 Context Builder output contract is unstable.
- Citation metadata is insufficient for validation.
- MCP/Claude Desktop integration needs user-local credentials or configuration that cannot be automated.

## Verification Commands
```powershell
uv run pytest tests/unit/test_agents.py tests/integration/test_query_api.py tests/integration/test_mcp_server.py
uv run uvicorn src.main:app --reload
uv run python -m src.mcp.server --help
```
