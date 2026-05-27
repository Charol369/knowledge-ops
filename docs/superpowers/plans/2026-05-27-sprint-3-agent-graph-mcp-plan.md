---
change: sprint-3-agent-graph-mcp
design-doc: docs/superpowers/specs/2026-05-27-sprint-3-agent-graph-mcp-design.md
status: draft
---

# Sprint 3 Plan: LangGraph Agent Graph + MCP Tool Layer

## Objective
Represent KnowledgeOps as an auditable LangGraph workflow and connect it to API and MCP surfaces.

## Scope
1. Refactor main graph around planner, retrieval orchestrator, synthesizer, reporter, verifier/reflection, and memory checkpointer.
2. Enforce Pydantic structured output.
3. Enforce and validate citations.
4. Wire MCP server to retrieval services and synthesizer.
5. Connect `/api/v1/query` to the graph.
6. Document Claude Desktop local integration boundary.
7. Write ADR 004 and ADR 007.

## Constraints
- Requires completed Sprint 1-2 contracts.
- Do not implement Sprint 4 policy, auth, rate limiting, Langfuse, PostgresSaver, or injection hardening.
- Do not treat manual Claude Desktop configuration as code-complete delivery.

## Done When
- Graph executes `plan -> retrieve -> synthesize -> report -> verify` locally.
- `/api/v1/query` returns graph-backed structured responses.
- Citation validation rejects unsupported citations.
- MCP server exposes retrieval/synthesis tools.
- ADR 004 and ADR 007 are recorded.

## Stop If
- Retrieval/context outputs from Sprint 2 are not stable enough to feed graph state.
- Citation metadata cannot be traced to evidence.
- Local MCP client configuration requires user-only manual steps.

## Checklist Mapping
| Backlog Item | Plan Step |
|---|---|
| LangGraph 主图重构 | Graph composition |
| Planner Node | Graph nodes |
| Retrieval Orchestrator | Graph nodes |
| Synthesizer | Graph nodes |
| Reporter | Graph nodes |
| Verifier / Reflection | Graph nodes |
| Memory Checkpointer | Graph state |
| Pydantic structured_output | Output contract |
| Citation 强制 + 校验 | Evidence validation |
| MCP Server 接 Retrieval Services + Synthesizer | MCP layer |
| Claude Desktop 接入测试 | Manual integration validation |
| `/api/v1/query` 接通 Agent graph | API layer |
| ADR 004 + ADR 007 | Architecture records |

## Verification Commands
```powershell
uv run pytest tests/unit/test_agents.py tests/integration/test_query_api.py tests/integration/test_mcp_server.py
uv run uvicorn src.main:app --reload
uv run python -m src.mcp.server --help
```

## Dependency on Previous Sprints
Depends on Sprint 1 and Sprint 2. Sprint 3 must be recalibrated after Sprint 2 because graph state should follow actual retrieval/context contracts.

## Manual / Non-Code Delivery Boundary
Claude Desktop configuration/testing may require manual client-side setup. Public demo, cloud deployment, resume, and applications are excluded.

## `/goal` Draft Outline
- Read final Sprint 1-2 contracts first.
- Implement LangGraph nodes and state.
- Wire API and MCP to graph-backed services.
- Add structured output and citation validation tests.
- Record ADR 004/007.

## `/goal` Readiness
Do not finalize before Sprint 1-2 are executed and retrieval/context contracts are recalibrated.
