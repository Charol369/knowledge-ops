from scripts.smoke_external_interfaces import (
    endpoint_metadata,
    redact,
    redact_nested,
    summarize,
    write_json_output,
)


def test_external_smoke_endpoint_metadata_does_not_include_api_key():
    metadata = endpoint_metadata("https://example.test/v1")

    assert metadata["scheme"] == "https"
    assert metadata["host"] == "example.test"
    assert metadata["path"] == "/v1"
    assert len(metadata["base_url_sha256_12"]) == 12


def test_external_smoke_redacts_key_like_values(monkeypatch):
    monkeypatch.setattr(
        "scripts.smoke_external_interfaces.settings.deepseek_api_key",
        "sk-test-secret-123456",
    )

    assert redact("failed with sk-test-secret-123456") == "failed with <redacted>"
    assert redact("failed with sk-another-secret-abcdef") == "failed with sk-<redacted>"


def test_external_smoke_redacts_nested_payload(monkeypatch):
    monkeypatch.setattr(
        "scripts.smoke_external_interfaces.settings.langfuse_secret_key",
        "sk-lf-secret-123456",
    )

    payload = {"outer": ["token sk-lf-secret-123456", {"inner": "ok"}]}

    assert redact_nested(payload) == {"outer": ["token <redacted>", {"inner": "ok"}]}


def test_external_smoke_summary_treats_expected_unavailable_as_non_failure():
    payload = {
        "checks": {
            "provider": {
                "chat": {"status": "ok"},
                "legacy": {"status": "expected_unavailable"},
            }
        }
    }

    summary = summarize(payload, strict=True)

    assert summary["status"] == "ok"
    assert summary["checks_total"] == 2
    assert summary["expected_unavailable_checks"] == ["provider.legacy"]


def test_external_smoke_summary_can_fail_on_blocked_when_strict():
    payload = {"checks": {"provider": {"models": {"status": "blocked"}}}}

    assert summarize(payload, strict=False)["status"] == "blocked"
    assert summarize(payload, strict=True)["status"] == "failed"


def test_external_smoke_can_persist_json_output(tmp_path):
    output = tmp_path / "results" / "external.json"

    write_json_output({"summary": {"status": "ok"}}, output)

    assert output.exists()
    assert '"status": "ok"' in output.read_text(encoding="utf-8")
