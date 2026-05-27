# Sprint 3: LangGraph Agent Graph + MCP Tool Layer

## Why
Once retrieval and context engineering are stable, KnowledgeOps needs its cognitive workflow expressed as an auditable agent graph and exposed through MCP/API boundaries.

## What
- Refactor the main agent workflow into LangGraph nodes.
- Implement Planner, Retrieval Orchestrator, Synthesizer, Reporter, Verifier/Reflection, and Memory Checkpointer.
- Enforce Pydantic structured output and citation validation.
- Connect MCP server to retrieval services and synthesizer.
- Test Claude Desktop integration boundary.
- Connect `/api/v1/query` to the agent graph.
- Record ADR 004 and ADR 007.

## Non-Code / Manual Boundaries
- Claude Desktop wiring may require manual local client configuration and should be documented separately from code acceptance.
- No public demo video, cloud deployment, resume, or application work belongs here.

## Dependencies
Depends on Sprint 1 ingestion/artifacts and Sprint 2 retrieval/context contracts.
