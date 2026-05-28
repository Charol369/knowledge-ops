from langgraph.checkpoint.memory import MemorySaver

from src.agents.memory import get_checkpointer, get_checkpointer_status


def test_checkpointer_defaults_to_memory_without_postgres_configuration(monkeypatch):
    monkeypatch.setattr("src.agents.memory.settings.postgres_saver_dsn", "")

    checkpointer = get_checkpointer()
    status = get_checkpointer_status()

    assert isinstance(checkpointer, MemorySaver)
    assert status.backend == "memory"
    assert status.configured is False
    assert status.active is True
    assert status.blocked_reason is None
    assert status.pending_reason == "PostgresSaver disabled: no postgres_saver_dsn configured; using MemorySaver."


def test_checkpointer_falls_back_to_memory_when_postgres_factory_is_unavailable(monkeypatch):
    monkeypatch.setattr("src.agents.memory.settings.postgres_saver_dsn", "postgresql://local/test")

    checkpointer = get_checkpointer(postgres_saver_factory=None)
    status = get_checkpointer_status(postgres_saver_factory=None)

    assert isinstance(checkpointer, MemorySaver)
    assert status.backend == "memory"
    assert status.configured is True
    assert status.active is True
    assert status.blocked_reason == (
        "PostgresSaver configured but no local factory/dependency is available; using MemorySaver fallback."
    )


def test_checkpointer_uses_injected_postgres_factory_when_configured(monkeypatch):
    class FakePostgresSaver:
        pass

    sentinel = FakePostgresSaver()
    calls = []

    monkeypatch.setattr("src.agents.memory.settings.postgres_saver_dsn", "postgresql://local/test")

    checkpointer = get_checkpointer(
        postgres_saver_factory=lambda dsn: calls.append(dsn) or sentinel
    )
    status = get_checkpointer_status(
        postgres_saver_factory=lambda dsn: calls.append(f"status:{dsn}") or sentinel
    )

    assert checkpointer is sentinel
    assert status.backend == "postgres"
    assert status.configured is True
    assert status.active is True
    assert status.blocked_reason is None
    assert calls == ["postgresql://local/test", "status:postgresql://local/test"]


def test_checkpointer_fallback_reports_factory_failure_without_raising(monkeypatch):
    monkeypatch.setattr("src.agents.memory.settings.postgres_saver_dsn", "postgresql://local/test")

    def failing_factory(dsn: str):
        raise RuntimeError(f"connection failed for {dsn}")

    checkpointer = get_checkpointer(postgres_saver_factory=failing_factory)
    status = get_checkpointer_status(postgres_saver_factory=failing_factory)

    assert isinstance(checkpointer, MemorySaver)
    assert status.backend == "memory"
    assert status.configured is True
    assert status.active is True
    assert status.blocked_reason == (
        "PostgresSaver configured but unavailable: connection failed for postgresql://local/test; "
        "using MemorySaver fallback."
    )
