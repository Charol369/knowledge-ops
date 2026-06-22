from src.agents.llm_synthesizer import LLMSynthesizer
from src.config import settings


def test_llm_synthesizer_returns_verified_answer_with_citations(monkeypatch):
    monkeypatch.setattr(settings, "llm_synthesis_enabled", True)
    monkeypatch.setattr(settings, "llm_synthesis_retry_count", 1)
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test")
    monkeypatch.setattr(settings, "deepseek_base_url", "https://provider.example/v1")
    monkeypatch.setattr(settings, "primary_model", "deepseek-v4-pro")

    def fake_completion_create(**kwargs):
        assert kwargs["model"] == "deepseek-v4-pro"
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            "Multi-head attention runs attention heads in parallel "
                            "and combines their projected outputs "
                            "[source: paper.pdf, page 4]."
                        )
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 8},
        }

    result = LLMSynthesizer(completion_create=fake_completion_create).synthesize(
        question="What is multi-head attention?",
        evidence=[
            {
                "source": "paper.pdf",
                "page": 4,
                "content": "Multi-head attention runs several attention heads in parallel.",
            }
        ],
        model_tier="tier2",
    )

    assert result.status == "ok"
    assert result.model == "deepseek-v4-pro"
    assert "parallel" in result.answer
    assert result.usage == {"prompt_tokens": 10, "completion_tokens": 8}


def test_llm_synthesizer_renders_structured_json_answer_with_local_citations(monkeypatch):
    monkeypatch.setattr(settings, "llm_synthesis_enabled", True)
    monkeypatch.setattr(settings, "llm_synthesis_retry_count", 1)
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test")
    monkeypatch.setattr(settings, "deepseek_base_url", "https://provider.example/v1")
    monkeypatch.setattr(settings, "primary_model", "deepseek-v4-pro")

    def fake_completion_create(**kwargs):
        assert "Return valid JSON only" in kwargs["messages"][0]["content"]
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"paragraphs":[{"text":"Multi-head attention runs heads in parallel.",'
                            '"citations":[{"source":"paper.pdf","page":4}]}]}'
                        )
                    }
                }
            ]
        }

    result = LLMSynthesizer(completion_create=fake_completion_create).synthesize(
        question="What is multi-head attention?",
        evidence=[
            {
                "source": "paper.pdf",
                "page": 4,
                "content": "Multi-head attention runs several attention heads in parallel.",
            }
        ],
        model_tier="tier2",
    )

    assert result.status == "ok"
    assert result.answer == (
        "Multi-head attention runs heads in parallel. [source: paper.pdf, page 4]"
    )


def test_llm_synthesizer_retries_when_first_answer_has_no_parseable_citations(monkeypatch):
    monkeypatch.setattr(settings, "llm_synthesis_enabled", True)
    monkeypatch.setattr(settings, "llm_synthesis_retry_count", 1)
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test")
    monkeypatch.setattr(settings, "deepseek_base_url", "https://provider.example/v1")
    monkeypatch.setattr(settings, "primary_model", "deepseek-v4-pro")
    calls = []

    def fake_completion_create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return {"choices": [{"message": {"content": "Multi-head attention runs heads in parallel."}}]}
        assert "Previous answer that failed citation validation" in kwargs["messages"][1]["content"]
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            "Multi-head attention runs heads in parallel "
                            "[source: paper.pdf, page 4]."
                        )
                    }
                }
            ]
        }

    result = LLMSynthesizer(completion_create=fake_completion_create).synthesize(
        question="What is multi-head attention?",
        evidence=[
            {
                "source": "paper.pdf",
                "page": 4,
                "content": "Multi-head attention runs several attention heads in parallel.",
            }
        ],
        model_tier="tier2",
    )

    assert len(calls) == 2
    assert result.status == "ok"
    assert "[source: paper.pdf, page 4]" in result.answer


def test_llm_synthesizer_blocks_without_provider_config(monkeypatch):
    monkeypatch.setattr(settings, "llm_synthesis_enabled", True)
    monkeypatch.setattr(settings, "deepseek_api_key", "")

    result = LLMSynthesizer().synthesize(
        question="What is multi-head attention?",
        evidence=[{"source": "paper.pdf", "page": 4, "content": "evidence"}],
        model_tier="tier2",
    )

    assert result.status == "blocked"
    assert "provider" in result.blocked_reason
