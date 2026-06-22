# P0 Intent-Aware QA Core Implementation Plan

Date: 2026-06-22

Status: Ready for development

Depends on:

- `docs/product-requirements.md`
- `docs/product-workflows.md`
- `docs/product-api-contract.md`
- `docs/product-data-model.md`
- `docs/p0-intent-routing-design.md`

## 1. Objective

Implement the P0 intent-aware QA core described in `docs/p0-intent-routing-design.md`.

The implementation must keep the current verified baseline stable:

```text
107 passed, 3 warnings
ruff: All checks passed
main pushed through 308222a
```

The next coding round is not allowed to claim P1/P2 capabilities such as ACL, Postgres persistence, real bge-m3 Docker runtime, real RAGAS, 100 QPS, or cloud deployment.

## 2. Delivery Scope

### In Scope

| Scope | Deliverable |
|---|---|
| Intent classification | Deterministic router for P0 intents. |
| Intent-aware execution | Graph routes count/section/table/normal questions differently. |
| Reference count | Deterministic tool result or precise blocked reason. |
| Section lookup | Deterministic section evidence or precise blocked reason. |
| Diagnostics | API and UI expose intent, strategy, tool status and fallback reason. |
| Tests | Unit and integration tests for normal, tool and blocked paths. |
| Docs | Status docs updated after verified implementation. |

### Out of Scope

| Out of scope | Reason |
|---|---|
| Postgres tables/migrations | Design exists; not required for P0 routing correctness. |
| User/group/document ACL | P2 security boundary, not part of local P0 proof. |
| Real bge-m3 runtime | Retrieval quality path comes after workflow correctness. |
| Real RAGAS metrics | Requires stable regression outputs first. |
| Locust 100 QPS | Load testing follows correctness. |
| Cloud deployment | Deployment follows stable local stack. |
| Next.js rewrite | Current UI is sufficient for P0. |

## 3. Implementation Order

Use this order. Do not start later tasks before earlier schema and routing contracts are stable.

```text
Task 1: Extend API and graph state schema
Task 2: Add deterministic QueryIntentRouter
Task 3: Add reference_count_tool
Task 4: Add section_lookup_tool and table blocked path
Task 5: Add intent-aware graph execution
Task 6: Update synthesis/reporter/verifier behavior for tool and blocked paths
Task 7: Extend API response and Streamlit diagnostics
Task 8: Add regression/eval artifacts
Task 9: Run validation and update docs
Task 10: Commit and push
```

## 4. Task Breakdown

### Task 1: Extend API And Graph State Schema

Goal:

```text
Add fields required to represent intent, strategy, tool output and diagnostics end-to-end.
```

Files:

```text
src/api/schemas.py
src/api/routes.py
src/agents/graph.py
tests/integration/test_query_api.py
tests/integration/test_streaming.py
```

Required changes:

- Add `intent`, `strategy`, `intent_confidence`, `tool_name`, `tool_status`, `tool_result`, `fallback_reason`, `diagnostics` to `QueryResponse`.
- Add matching fields to `AgentState`.
- Map graph result fields to API response fields.
- Include expanded fields in SSE completion.
- Keep existing fields backward compatible.

Acceptance:

```text
/api/v1/query response validates with new optional fields.
Existing query tests still pass.
No old response field is removed.
```

Tests:

```powershell
uv run pytest tests/integration/test_query_api.py tests/integration/test_streaming.py -q
```

### Task 2: Add Deterministic QueryIntentRouter

Goal:

```text
Classify P0 question intents without relying on external LLM calls.
```

Files:

```text
src/agents/intent_router.py
src/agents/graph.py
tests/unit/test_intent_router.py
```

Required changes:

- Implement `QueryIntentResult`.
- Implement `classify_query_intent(question: str, requested_intent: str | None = None)`.
- Support intents:
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
- Respect explicit `QueryRequest.intent` only if it is in the allowed set; otherwise fall back to router classification and record route reason.

Rule examples:

| Pattern | Intent | Strategy |
|---|---|---|
| `what is`, `define`, `explain` | `definition` | `hybrid_retrieval` |
| `section 3.2`, `summarize 3.2` | `section_summary` | `section_lookup` |
| `how many references`, `number of citations` | `count` | `reference_count` |
| `table 2` | `table_query` | `table_lookup` |
| `private salary`, `personal password` | `no_answer` | `blocked` |

Acceptance:

```text
All P0 intents have deterministic tests.
Router output includes intent, strategy, confidence, route_reason and optional target.
No external API call is required.
```

Tests:

```powershell
uv run pytest tests/unit/test_intent_router.py -q
```

### Task 3: Add Reference Count Tool

Goal:

```text
Answer reference-count questions with deterministic evidence, not LLM guessing.
```

Files:

```text
src/agents/tools.py
or
src/tools/reference_count.py
tests/unit/test_reference_count_tool.py
tests/integration/test_query_api.py
```

Required changes:

- Implement `ReferenceCountResult`.
- Load docs using existing loaders.
- Locate likely references section.
- Count numbered references.
- Return:
  ```text
  status=ok, count, source, page_start/page_end, evidence
  ```
  or:
  ```text
  status=blocked, blocked_reason
  ```
- Do not call LLM for counting.

Blocked reasons:

| Condition | blocked_reason |
|---|---|
| no supported document text | `No supported local document text was loaded.` |
| references heading missing | `No references section was located.` |
| references found but entries uncountable | `References section was located, but entries could not be counted deterministically.` |

Acceptance:

```text
"How many references are in Attention Is All You Need?" returns strategy=reference_count and tool_name=reference_count_tool.
The count comes from tool_result, not LLM text inference.
If the tool cannot count, API returns a precise blocked reason.
```

Tests:

```powershell
uv run pytest tests/unit/test_reference_count_tool.py tests/integration/test_query_api.py -q
```

### Task 4: Add Section Lookup Tool And Table Blocked Path

Goal:

```text
Make section questions retrieve section-scoped evidence and make unsupported table questions block honestly.
```

Files:

```text
src/tools/section_lookup.py
src/agents/tools.py
tests/unit/test_section_lookup_tool.py
tests/integration/test_query_api.py
```

Required changes:

- Implement `SectionLookupResult`.
- Parse section targets from question.
- Locate heading by section number/title.
- Collect evidence until next same-or-higher-level heading.
- Return blocked reason when section is missing.
- For `table_query`, return `tool_status=blocked` with:
  ```text
  Table parsing/indexing is not available in the current P0 local index.
  ```

Acceptance:

```text
Section questions do not use unrelated top-k chunks when the requested section is missing.
Table questions do not hallucinate table content.
```

Tests:

```powershell
uv run pytest tests/unit/test_section_lookup_tool.py tests/integration/test_query_api.py -q
```

### Task 5: Add Intent-Aware Graph Execution

Goal:

```text
Wire router and tools into the LangGraph state flow.
```

Files:

```text
src/agents/graph.py
src/agents/orchestrator.py
src/agents/intent_router.py
src/agents/tools.py
tests/unit/test_agents.py
```

Required changes:

- Add `intent_router_node`.
- Add `query_executor_node` or update `retrieval_orchestrator_node` to dispatch by `strategy`.
- Preserve current hybrid retrieval behavior for `definition`, `list`, `compare`, `unknown`.
- Use tool evidence for `reference_count` and `section_lookup`.
- Set graph fields:
  ```text
  intent
  strategy
  tool_name
  tool_status
  tool_result
  fallback_reason
  blocked_reason
  ```

Recommended graph:

```text
START
-> intent_router
-> planner
-> retrieval_orchestrator_or_executor
-> synthesizer
-> reporter
-> verifier
-> END
```

Acceptance:

```text
Existing graph tests pass.
New graph tests prove intent/strategy/tool_result propagate to final graph output.
```

Tests:

```powershell
uv run pytest tests/unit/test_agents.py -q
```

### Task 6: Update Synthesis, Reporter And Verifier Behavior

Goal:

```text
Ensure final answers respect deterministic tool results and blocked paths.
```

Files:

```text
src/agents/synthesizer.py
src/agents/reporter.py
src/agents/verifier.py
tests/unit/test_agents.py
tests/unit/test_llm_synthesizer.py
tests/unit/test_citation.py
```

Required changes:

- For successful `reference_count`, final answer must include `tool_result.count`.
- For blocked tool paths, final answer must state that evidence/tool support is insufficient.
- LLM synthesis must not override deterministic count.
- Citation verifier should accept tool evidence when present.
- `needs_human_review` should be true for blocked valid document questions.

Acceptance:

```text
Count answer uses deterministic tool count.
Blocked answer does not claim unsupported facts.
Citation verifier still passes supported answers.
```

Tests:

```powershell
uv run pytest tests/unit/test_agents.py tests/unit/test_llm_synthesizer.py tests/unit/test_citation.py -q
```

### Task 7: Extend API Response And Streamlit Diagnostics

Goal:

```text
Expose routing/tool/fallback status to developers and local product validation without cluttering normal answer usage.
```

Files:

```text
frontend/app.py
src/api/schemas.py
src/api/routes.py
tests/integration/test_frontend_demo.py
tests/integration/test_query_api.py
tests/integration/test_streaming.py
```

Required changes:

- Show `intent`, `strategy`, `tool_status`, `fallback_reason` in UI metadata or diagnostics expander.
- Keep normal user flow simple.
- Do not reintroduce required manual trace input.
- API response fields should be visible in Streamlit result rendering.

Acceptance:

```text
UI can display diagnostics from a completion payload.
Manual thread/trace remains advanced/debug only.
```

Tests:

```powershell
uv run pytest tests/integration/test_frontend_demo.py tests/integration/test_query_api.py tests/integration/test_streaming.py -q
```

### Task 8: Add Regression/Eval Artifacts

Goal:

```text
Create a small reproducible P0 intent QA regression set.
```

Files:

```text
eval/intent_qa.jsonl
scripts/evaluate_intent_qa.py
eval/results/intent_qa_latest.json
docs/benchmark.md
tests/unit or tests/integration for script import/smoke
```

Required changes:

- Add 10-20 examples across:
  ```text
  definition
  count
  section_summary
  table_query
  no_answer
  list
  ```
- Evaluate:
  ```text
  expected_intent
  expected_strategy
  expected_tool_status
  expected_sources/pages where applicable
  expected_answer_contains where deterministic
  ```
- Add `--output` to persist result artifact if creating a new script.

Acceptance:

```text
P0 regression can be rerun locally and writes JSON result artifact.
Benchmark docs state exactly what was measured.
```

Tests / command:

```powershell
uv run python scripts/evaluate_intent_qa.py --dataset eval/intent_qa.jsonl --output eval/results/intent_qa_latest.json
```

### Task 9: Validation And Documentation

Goal:

```text
Verify implementation and update evidence-backed status docs.
```

Commands:

```powershell
uv run pytest -q
uv run ruff check src tests frontend\app.py
uv run python -m py_compile frontend\app.py src\api\schemas.py src\api\routes.py src\agents\graph.py
```

API smoke examples:

```powershell
uv run python -c "from fastapi.testclient import TestClient; from src.main import app; c=TestClient(app); r=c.post('/api/v1/query', json={'question':'What is multi-head attention in Attention Is All You Need?','docs_dir':'data','index_dir':'data/faiss/sprint1','embedding_backend':'hash'}); b=r.json(); print(r.status_code, b.get('intent'), b.get('strategy'), b.get('synthesis_mode'))"
```

```powershell
uv run python -c "from fastapi.testclient import TestClient; from src.main import app; c=TestClient(app); r=c.post('/api/v1/query', json={'question':'How many references are in Attention Is All You Need?','docs_dir':'data','index_dir':'data/faiss/sprint1','embedding_backend':'hash'}); b=r.json(); print(r.status_code, b.get('intent'), b.get('strategy'), b.get('tool_name'), b.get('tool_status'), b.get('tool_result'))"
```

Docs to update:

```text
README.md
docs/api.md
docs/architecture.md
docs/benchmark.md
docs/career-materials.md
docs/delivery.md
docs/product-requirements.md
docs/product-workflows.md
docs/product-api-contract.md
```

Rules:

- Update test count only after `uv run pytest -q` completes.
- Do not claim exact reference count unless the tool and test prove it.
- Do not claim RAGAS/QPS/cloud/bge-m3/ACL as complete.

### Task 10: Commit And Push

Goal:

```text
Make the implementation reproducible from GitHub.
```

Commands:

```powershell
git status --short --branch
git add .
git commit -m "feat: add intent-aware qa routing"
git push
git status --short --branch
git log --oneline -3
```

Acceptance:

```text
Working tree is clean.
origin/main contains the new commit.
Final summary includes commit hash and validation outputs.
```

## 5. Milestones

| Milestone | Tasks | Done when |
|---|---|---|
| M1 Schema + router | Task 1-2 | API fields exist; router tests pass |
| M2 Tools | Task 3-4 | count/section/table blocked tests pass |
| M3 Graph integration | Task 5-6 | graph/API returns intent-aware outputs |
| M4 UI + regression | Task 7-8 | UI shows diagnostics; eval artifact exists |
| M5 Closure | Task 9-10 | full tests pass; docs updated; commit pushed |

## 6. File Ownership Map

| Area | Files |
|---|---|
| API contract | `src/api/schemas.py`, `src/api/routes.py`, `docs/api.md` |
| Graph routing | `src/agents/graph.py`, `src/agents/intent_router.py`, `src/agents/orchestrator.py` |
| Deterministic tools | `src/agents/tools.py` or `src/tools/*.py` |
| Generation/reporting | `src/agents/synthesizer.py`, `src/agents/reporter.py`, `src/agents/verifier.py` |
| UI diagnostics | `frontend/app.py` |
| Tests | `tests/unit/test_intent_router.py`, `tests/unit/test_reference_count_tool.py`, `tests/unit/test_section_lookup_tool.py`, `tests/integration/test_query_api.py`, `tests/integration/test_streaming.py`, `tests/integration/test_frontend_demo.py` |
| Eval | `eval/intent_qa.jsonl`, `scripts/evaluate_intent_qa.py`, `eval/results/intent_qa_latest.json` |
| Docs | `README.md`, `docs/*.md` |

## 7. Risk Register

| Risk | Mitigation |
|---|---|
| Reference section parsing fails on PDFs with wrapped lines | Return blocked reason; do not guess. Add fixture tests. |
| Section heading detection misses layout-specific headings | Return blocked reason; keep algorithm deterministic. |
| Intent rules overfit English examples | Keep explicit tests and add Chinese/English patterns incrementally. |
| LLM synthesis overwrites tool count | Reporter/synthesizer must pin tool_result count in final answer. |
| API response grows too noisy | Put detailed fields in `diagnostics`; UI shows them in expander. |
| Regression dataset becomes claim inflation | Docs must label it as P0 local regression, not production quality evaluation. |

## 8. Open Decisions Before Coding

These should be confirmed before starting Task 3/4:

1. Should P0 reference count support only references, or also citations mentioned in text?
2. Should section lookup target only numbered sections first, or also title-only headings?
3. Should `table_query` be blocked in P0, or should it retrieve nearby table caption text as partial evidence?
4. Should diagnostics always be returned, or only in local/dev mode?
5. Should `QueryRequest.intent` be treated as trusted caller override or only as a hint?

Recommended defaults:

```text
1. references only
2. numbered sections first
3. blocked with precise reason
4. always returned in P0 local product mode
5. hint only unless it matches allowed intents
```

## 9. Definition Of Done

The P0 implementation is done only when:

- Full validation commands pass.
- API and SSE responses expose intent-aware fields.
- Count and section workflows are tested.
- Blocked paths are explicit and do not hallucinate.
- Docs and career materials state only verified facts.
- Changes are committed and pushed.
