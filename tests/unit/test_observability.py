from src.observability.langfuse_setup import get_langfuse_handler
from src.observability.metrics import BusinessMetricsRecorder, business_metrics
from src.agents import graph as graph_module
from src.agents.planner import planner_node
from src.agents.verifier import verifier_node
import os
import sys
import types


def test_business_metrics_records_policy_fallback_guardrail_and_citation_events():
    recorder = BusinessMetricsRecorder()

    recorder.record_policy_decision(
        complexity="complex",
        model_tier="tier3",
        cache_hit=False,
        trace_id="trace-1",
    )
    recorder.record_policy_decision(
        complexity="standard",
        model_tier="tier2",
        cache_hit=True,
    )
    recorder.record_fallback(
        current_tier="tier3",
        fallback_tier="tier2",
        retry=True,
        trace_id="trace-1",
    )
    recorder.record_guardrail_decision(
        is_injection=True,
        level="local",
        blocked=False,
        trace_id="trace-2",
    )
    recorder.record_citation_verification(
        verified=True,
        needs_human_review=False,
        trace_id="trace-3",
    )

    snapshot = recorder.snapshot()

    assert snapshot["policy_decisions_total"] == 2
    assert snapshot["complexity_counts"] == {"complex": 1, "standard": 1}
    assert snapshot["model_tier_counts"] == {"tier3": 1, "tier2": 1}
    assert snapshot["cache_hits_total"] == 1
    assert snapshot["fallbacks_total"] == 1
    assert snapshot["retryable_fallbacks_total"] == 1
    assert snapshot["guardrail_injections_total"] == 1
    assert snapshot["guardrail_blocked_total"] == 0
    assert snapshot["citation_verifications_total"] == 1
    assert snapshot["citation_verified_total"] == 1
    assert snapshot["human_review_total"] == 0
    assert snapshot["trace_ids"] == ["trace-1", "trace-2", "trace-3"]


def test_business_metrics_global_recorder_can_reset():
    business_metrics.reset()
    business_metrics.record_policy_decision(
        complexity="simple",
        model_tier="tier1",
        cache_hit=False,
    )

    assert business_metrics.snapshot()["policy_decisions_total"] == 1

    business_metrics.reset()

    assert business_metrics.snapshot()["policy_decisions_total"] == 0


def test_langfuse_handler_is_disabled_without_complete_configuration(monkeypatch):
    monkeypatch.setattr("src.observability.langfuse_setup.settings.langfuse_enabled", False, raising=False)
    monkeypatch.setattr("src.observability.langfuse_setup.settings.langfuse_public_key", "")
    monkeypatch.setattr("src.observability.langfuse_setup.settings.langfuse_secret_key", "")

    assert get_langfuse_handler() is None


def test_langfuse_handler_is_disabled_when_not_explicitly_enabled(monkeypatch):
    calls = []

    monkeypatch.setattr("src.observability.langfuse_setup.settings.langfuse_enabled", False, raising=False)
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_public_key",
        "public",
    )
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_secret_key",
        "secret",
    )

    handler = get_langfuse_handler(handler_factory=lambda: calls.append("called"))

    assert handler is None
    assert calls == []


def test_langfuse_handler_uses_injected_factory_only_when_explicitly_configured(monkeypatch):
    sentinel = object()
    calls = []

    monkeypatch.setattr("src.observability.langfuse_setup.settings.langfuse_enabled", True, raising=False)
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_public_key",
        "public",
    )
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_secret_key",
        "secret",
    )

    handler = get_langfuse_handler(
        handler_factory=lambda: calls.append("called") or sentinel,
    )

    assert handler is sentinel
    assert calls == ["called"]


def test_langfuse_handler_safely_disables_when_factory_fails(monkeypatch):
    monkeypatch.setattr("src.observability.langfuse_setup.settings.langfuse_enabled", True, raising=False)
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_public_key",
        "public",
    )
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_secret_key",
        "secret",
    )

    assert get_langfuse_handler(handler_factory=lambda: (_ for _ in ()).throw(RuntimeError("auth failed"))) is None


def test_langfuse_handler_maps_settings_to_sdk_environment(monkeypatch):
    seen = {}

    class FakeCallbackHandler:
        def __init__(self):
            seen["public_key"] = os.environ.get("LANGFUSE_PUBLIC_KEY")
            seen["secret_key"] = os.environ.get("LANGFUSE_SECRET_KEY")
            seen["host"] = os.environ.get("LANGFUSE_HOST")

    fake_module = types.ModuleType("langfuse.langchain")
    fake_module.CallbackHandler = FakeCallbackHandler

    monkeypatch.setitem(sys.modules, "langfuse.langchain", fake_module)
    monkeypatch.setattr("src.observability.langfuse_setup.settings.langfuse_enabled", True)
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_public_key",
        "public-from-settings",
    )
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_secret_key",
        "secret-from-settings",
    )
    monkeypatch.setattr(
        "src.observability.langfuse_setup.settings.langfuse_host",
        "http://localhost:3000",
    )
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_HOST", raising=False)

    handler = get_langfuse_handler()

    assert isinstance(handler, FakeCallbackHandler)
    assert seen == {
        "public_key": "public-from-settings",
        "secret_key": "secret-from-settings",
        "host": "http://localhost:3000",
    }


def test_planner_records_policy_decision_with_trace_id():
    business_metrics.reset()

    result = planner_node(
        {
            "question": "Compare multiple documents and analyze tradeoffs.",
            "execution_path": [],
            "trace_id": "trace-policy",
        }
    )

    snapshot = business_metrics.snapshot()
    assert result["complexity"] == "complex"
    assert result["model_tier"] == "tier3"
    assert snapshot["policy_decisions_total"] == 1
    assert snapshot["complexity_counts"] == {"complex": 1}
    assert snapshot["model_tier_counts"] == {"tier3": 1}
    assert snapshot["trace_ids"] == ["trace-policy"]


def test_verifier_records_citation_verification_with_trace_id():
    business_metrics.reset()

    verifier_node(
        {
            "answer": "Grounded answer",
            "citations": [{"source": "fixture.md", "page": 1, "snippet": None}],
            "context": {
                "evidence": [
                    {
                        "content": "Grounded answer",
                        "source": "fixture.md",
                        "page": 1,
                    }
                ]
            },
            "evidence": [],
            "execution_path": [],
            "trace_id": "trace-citation",
        }
    )

    snapshot = business_metrics.snapshot()
    assert snapshot["citation_verifications_total"] == 1
    assert snapshot["citation_verified_total"] == 1
    assert snapshot["human_review_total"] == 0
    assert snapshot["trace_ids"] == ["trace-citation"]


def test_graph_injects_optional_langfuse_callback_without_requiring_server(
    monkeypatch,
    tmp_path,
):
    sentinel_handler = object()
    captured = {}

    class FakeGraph:
        def invoke(self, state, config):
            captured["state"] = state
            captured["config"] = config
            return {
                **state,
                "plan": ["Retrieve local evidence.", "Answer with citations."],
                "evidence": [],
                "answer": "Answer grounded in local evidence.",
                "trace_id": state["trace_id"],
            }

    monkeypatch.setattr(graph_module, "build_graph", lambda: FakeGraph())
    monkeypatch.setattr(graph_module, "get_langfuse_handler", lambda: sentinel_handler)

    result = graph_module.run_research_graph(
        question="How is tracing configured?",
        thread_id="trace-hook",
        artifact_root=tmp_path,
    )

    assert result["trace_id"] == "trace-hook"
    assert captured["config"]["configurable"]["thread_id"] == "trace-hook"
    assert captured["config"]["callbacks"] == [sentinel_handler]
