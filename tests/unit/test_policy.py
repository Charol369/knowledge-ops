import time

from src.policy import (
    ComplexityClassifier,
    FallbackPolicy,
    LocalResponseCache,
    ModelRouter,
)


def test_complexity_classifier_is_deterministic_and_local():
    classifier = ComplexityClassifier()

    assert classifier.classify("hi") == "simple"
    assert classifier.classify("What is RAG?") == "standard"
    assert (
        classifier.classify(
            "Compare multiple documents, analyze tradeoffs, and draft an executive report."
        )
        == "complex"
    )


def test_model_router_maps_complexity_to_model_tiers_without_model_calls():
    router = ModelRouter()

    assert router.route("simple") == "tier1"
    assert router.route("standard") == "tier2"
    assert router.route("complex") == "tier3"


def test_fallback_policy_retries_only_transient_failures():
    policy = FallbackPolicy()

    assert policy.should_retry("timeout while calling model") is True
    assert policy.should_retry("HTTP 503 service unavailable") is True
    assert policy.should_retry("401 unauthorized api key") is False
    assert policy.should_retry("validation failed permanently") is False


def test_local_response_cache_returns_values_until_ttl_expires():
    now = [100.0]
    cache = LocalResponseCache(ttl_seconds=10, clock=lambda: now[0])

    cache.set("question", {"answer": "cached"})

    assert cache.get("question") == {"answer": "cached"}
    now[0] += 11
    assert cache.get("question") is None


def test_local_response_cache_default_clock_is_callable():
    cache = LocalResponseCache(ttl_seconds=1)

    cache.set("key", "value")

    assert cache.get("key") == "value"
    time.sleep(1.05)
    assert cache.get("key") is None
