from frontend import app as frontend_app


def test_demo_parses_sse_events_for_progress_and_completion():
    payload = (
        'event: progress\n'
        'data: {"stage":"started","trace_id":"trace-ui"}\n\n'
        'event: completion\n'
        'data: {"answer":"done","trace_id":"trace-ui"}\n\n'
    )

    events = frontend_app.parse_sse_events(payload)

    assert events == [
        {
            "event": "progress",
            "data": {"stage": "started", "trace_id": "trace-ui"},
        },
        {
            "event": "completion",
            "data": {"answer": "done", "trace_id": "trace-ui"},
        },
    ]


def test_demo_builds_api_key_header_only_when_configured():
    assert frontend_app.build_api_headers("") == {}
    assert frontend_app.build_api_headers("  ") == {}
    assert frontend_app.build_api_headers("secret") == {"X-API-Key": "secret"}
