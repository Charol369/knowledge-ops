from langchain_core.documents import Document

from src.agents.qa_agent import qa_agent
from src.agents.report_agent import report_agent
from src.agents.summary_agent import summary_agent
from src.agents import tools as tools_module
from src.ingest.splitters import split_by_doc_type


def _state_with_evidence() -> dict:
    return {
        "question": "What does the evidence say?",
        "evidence": [
            {
                "content": "KnowledgeOps keeps answers grounded.",
                "source": "fixture.md",
                "page": 1,
            }
        ],
        "context": {},
        "execution_path": [],
    }


def test_split_by_doc_type_uses_existing_recursive_splitter_without_hard_failure():
    docs = [
        Document(
            page_content="A long technical paragraph. " * 80,
            metadata={"source": "paper.pdf"},
        )
    ]

    chunks = split_by_doc_type(docs)

    assert chunks
    assert all(chunk.metadata["source"] == "paper.pdf" for chunk in chunks)


def test_legacy_agent_entrypoints_return_grounded_state_without_notimplemented():
    state = _state_with_evidence()

    summarized = summary_agent(state)
    answered = qa_agent(state)
    reported = report_agent({**state, "synthesis": summarized["synthesis"]})

    assert "KnowledgeOps keeps answers grounded" in summarized["synthesis"]
    assert answered["answer"]
    assert answered["citations"] == [{"source": "fixture.md", "page": 1, "snippet": None}]
    assert reported["answer"]
    assert reported["citations"] == [{"source": "fixture.md", "page": 1, "snippet": None}]


def test_legacy_tools_use_retrieval_and_synthesis_services(monkeypatch):
    class FakeRetrievalOrchestrator:
        def __init__(self, top_k=None):
            self.top_k = top_k

        def gather_evidence(self, question, plan):
            return [
                {
                    "content": f"Evidence for {question}",
                    "source": "tool-fixture.md",
                    "page": 2,
                }
            ]

    monkeypatch.setattr(
        tools_module,
        "RetrievalOrchestrator",
        FakeRetrievalOrchestrator,
    )

    search_result = tools_module.search_kb.invoke({"query": "agent tools", "top_k": 1})
    summary_result = tools_module.summarize_evidence.invoke({"query": "agent tools"})

    assert "tool-fixture.md" in search_result
    assert "Evidence for agent tools" in summary_result
