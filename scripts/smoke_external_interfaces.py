"""Smoke test currently configured external/runtime interfaces.

The script intentionally redacts secrets and stores only safe endpoint metadata
such as host, path, model names, counts, status codes, and short URL hashes.
"""
import argparse
from collections.abc import Iterable
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any
from urllib.parse import urlsplit

import httpx
from openai import OpenAI

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import settings  # noqa: E402


Check = dict[str, Any]


def write_json_output(payload: dict[str, Any], output_path: str | Path | None) -> None:
    """Persist smoke output as a reproducible local artifact."""
    if output_path is None:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def redact(value: Any) -> Any:
    """Best-effort redaction for exception text before writing artifacts."""
    if value is None:
        return None
    text = str(value)
    secrets = [
        settings.deepseek_api_key,
        settings.langfuse_secret_key,
        settings.api_key,
    ]
    for secret in secrets:
        if secret:
            text = text.replace(secret, "<redacted>")
    text = re.sub(r"sk-[A-Za-z0-9_\-]{8,}", "sk-<redacted>", text)
    return text


def endpoint_metadata(base_url: str) -> dict[str, Any]:
    parsed = urlsplit(base_url.strip())
    safe_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    return {
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "path": parsed.path or "/",
        "base_url_sha256_12": hashlib.sha256(safe_url.encode("utf-8")).hexdigest()[:12],
    }


def models_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/models"


def success_check(**values: Any) -> Check:
    return {"status": "ok", **values}


def failed_check(message: str, **values: Any) -> Check:
    return {"status": "failed", "error": redact(message), **values}


def blocked_check(reason: str, **values: Any) -> Check:
    return {"status": "blocked", "blocked_reason": redact(reason), **values}


def provider_models_check(timeout: float) -> Check:
    if not settings.deepseek_api_key:
        return blocked_check("DEEPSEEK_API_KEY is not configured.")
    if not settings.deepseek_base_url:
        return blocked_check("DEEPSEEK_BASE_URL is not configured.")

    started = time.perf_counter()
    metadata = endpoint_metadata(settings.deepseek_base_url)
    try:
        response = httpx.get(
            models_url(settings.deepseek_base_url),
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "KnowledgeOps-Smoke/1.0",
            },
            timeout=timeout,
        )
        elapsed = time.perf_counter() - started
        try:
            body = response.json()
        except ValueError:
            body = {}
        if response.status_code != 200:
            return failed_check(
                f"models endpoint returned HTTP {response.status_code}",
                **metadata,
                status_code=response.status_code,
                elapsed_seconds=elapsed,
                response_text=redact(response.text[:300]),
            )
        ids = sorted(
            str(item.get("id"))
            for item in body.get("data", [])
            if isinstance(item, dict) and item.get("id")
        )
        return success_check(
            **metadata,
            status_code=response.status_code,
            elapsed_seconds=elapsed,
            model_count=len(ids),
            deepseek_model_count=sum(1 for item in ids if item.startswith("deepseek")),
            model_ids=ids,
            deepseek_model_ids=[item for item in ids if item.startswith("deepseek")],
        )
    except Exception as exc:
        return failed_check(
            f"models endpoint request failed: {exc}",
            **metadata,
            elapsed_seconds=time.perf_counter() - started,
        )


def provider_chat_check(model: str, timeout: float, expected_available: bool = True) -> Check:
    if not settings.deepseek_api_key:
        return blocked_check("DEEPSEEK_API_KEY is not configured.", model_requested=model)
    if not settings.deepseek_base_url:
        return blocked_check("DEEPSEEK_BASE_URL is not configured.", model_requested=model)

    started = time.perf_counter()
    try:
        client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout=timeout,
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Answer with exactly one word: ok"}],
            max_tokens=96,
            temperature=0,
        )
        choice = response.choices[0] if response.choices else None
        content = choice.message.content.strip() if choice and choice.message.content else ""
        usage = response.usage.model_dump(mode="json") if response.usage is not None else None
        return success_check(
            model_requested=model,
            model_returned=response.model,
            finish_reason=choice.finish_reason if choice else None,
            content=content,
            elapsed_seconds=time.perf_counter() - started,
            usage=usage,
            expectation="available" if expected_available else "unavailable",
            expectation_met=expected_available,
        )
    except Exception as exc:
        status_code = getattr(exc, "status_code", None)
        response_body = None
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                response_body = response.json()
            except Exception:
                response_body = getattr(response, "text", None)
        message = redact(exc)
        model_missing = "model_not_found" in str(message) or "not found" in str(message).lower()
        if not expected_available and (model_missing or status_code in {400, 404, 422, 503}):
            return {
                "status": "expected_unavailable",
                "model_requested": model,
                "status_code": status_code,
                "elapsed_seconds": time.perf_counter() - started,
                "error": message,
                "response": redact(response_body),
                "expectation": "unavailable",
                "expectation_met": True,
            }
        return failed_check(
            f"chat completion failed: {exc}",
            model_requested=model,
            status_code=status_code,
            elapsed_seconds=time.perf_counter() - started,
            response=redact(response_body),
            expectation="available" if expected_available else "unavailable",
            expectation_met=False,
        )


def http_check(url: str, *, expected_status: int = 200, timeout: float) -> Check:
    started = time.perf_counter()
    try:
        response = httpx.get(url, timeout=timeout)
        payload: dict[str, Any] = {
            "url": url,
            "status_code": response.status_code,
            "elapsed_seconds": time.perf_counter() - started,
        }
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                payload["json"] = response.json()
            except ValueError:
                payload["text"] = response.text[:200]
        else:
            payload["text"] = response.text[:200]
        if response.status_code == expected_status:
            return success_check(**payload)
        return failed_check(
            f"HTTP status {response.status_code}, expected {expected_status}",
            **payload,
        )
    except Exception as exc:
        return failed_check(
            f"HTTP request failed: {exc}",
            url=url,
            elapsed_seconds=time.perf_counter() - started,
        )


def run_command(args: list[str], timeout: float) -> Check:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            args,
            cwd=ROOT_DIR,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return blocked_check(
            f"Command is unavailable: {exc}",
            command=args[:3],
            elapsed_seconds=time.perf_counter() - started,
        )
    except subprocess.TimeoutExpired:
        return failed_check(
            f"Command timed out after {timeout} seconds.",
            command=args[:3],
            elapsed_seconds=time.perf_counter() - started,
        )

    payload = {
        "command": args[:3],
        "returncode": completed.returncode,
        "elapsed_seconds": time.perf_counter() - started,
        "stdout": redact(completed.stdout.strip()[:1000]),
        "stderr": redact(completed.stderr.strip()[:1000]),
    }
    if completed.returncode == 0:
        return success_check(**payload)
    return failed_check("Command returned non-zero exit code.", **payload)


def docker_compose_ps_check(timeout: float) -> Check:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=ROOT_DIR,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return blocked_check(
            f"Command is unavailable: {exc}",
            command=["docker", "compose", "ps"],
            elapsed_seconds=time.perf_counter() - started,
        )
    except subprocess.TimeoutExpired:
        return failed_check(
            f"Command timed out after {timeout} seconds.",
            command=["docker", "compose", "ps"],
            elapsed_seconds=time.perf_counter() - started,
        )

    if completed.returncode != 0:
        return failed_check(
            "Command returned non-zero exit code.",
            command=["docker", "compose", "ps"],
            returncode=completed.returncode,
            elapsed_seconds=time.perf_counter() - started,
            stdout=redact(completed.stdout.strip()[:1000]),
            stderr=redact(completed.stderr.strip()[:1000]),
        )

    services = []
    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            item = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        services.append(
            {
                "service": item.get("Service"),
                "name": item.get("Name"),
                "state": item.get("State"),
                "health": item.get("Health"),
                "status": item.get("Status"),
            }
        )
    return success_check(
        command=["docker", "compose", "ps"],
        returncode=completed.returncode,
        elapsed_seconds=time.perf_counter() - started,
        services=services,
        stderr=redact(completed.stderr.strip()[:1000]),
    )


def docker_exec_checks(timeout: float) -> dict[str, Check]:
    return {
        "clickhouse_select_1": run_command(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "clickhouse",
                "clickhouse-client",
                "--user",
                "clickhouse",
                "--password",
                "clickhouse",
                "--query",
                "SELECT 1",
            ],
            timeout=timeout,
        ),
        "postgres_pg_isready": run_command(
            ["docker", "compose", "exec", "-T", "postgres", "pg_isready", "-U", "postgres"],
            timeout=timeout,
        ),
        "redis_ping": run_command(
            ["docker", "compose", "exec", "-T", "redis", "redis-cli", "-a", "myredissecret", "ping"],
            timeout=timeout,
        ),
    }


def app_container_provider_check(model: str, timeout: float) -> Check:
    code = """
import json
import os
import sys
import time
from openai import OpenAI

expected_model = sys.argv[1] if len(sys.argv) > 1 else ""
model = os.environ.get("DEEPSEEK_MODEL", "")
if not model:
    model = "__missing__"
target = os.environ.get("DEEPSEEK_MODEL", "")
base_url = os.environ.get("DEEPSEEK_BASE_URL", "")
api_key = os.environ.get("DEEPSEEK_API_KEY", "")
if not (target and base_url and api_key):
    print(json.dumps({"status": "blocked", "blocked_reason": "container model/base_url/api_key incomplete", "model_requested": target or model, "expected_model": expected_model}))
    raise SystemExit(0)
if expected_model and target != expected_model:
    print(json.dumps({"status": "failed", "model_requested": target, "expected_model": expected_model, "error": "container DEEPSEEK_MODEL differs from host settings"}))
    raise SystemExit(0)
started = time.perf_counter()
try:
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)
    response = client.chat.completions.create(
        model=target,
        messages=[{"role": "user", "content": "Answer with exactly one word: ok"}],
        max_tokens=96,
        temperature=0,
    )
    choice = response.choices[0] if response.choices else None
    print(json.dumps({
        "status": "ok",
        "model_requested": target,
        "expected_model": expected_model,
        "model_returned": response.model,
        "content": choice.message.content.strip() if choice and choice.message.content else "",
        "finish_reason": choice.finish_reason if choice else None,
        "elapsed_seconds": time.perf_counter() - started,
        "usage": response.usage.model_dump(mode="json") if response.usage else None,
    }))
except Exception as exc:
    print(json.dumps({
        "status": "failed",
        "model_requested": target,
        "error": str(exc),
        "elapsed_seconds": time.perf_counter() - started,
    }))
"""
    command_result = run_command(
        ["docker", "compose", "exec", "-T", "app", "python", "-c", code, model],
        timeout=timeout,
    )
    if command_result["status"] != "ok":
        return command_result
    try:
        payload = json.loads(str(command_result.get("stdout", "{}")))
    except json.JSONDecodeError:
        return failed_check(
            "Container provider smoke returned non-JSON output.",
            command=command_result.get("command"),
            stdout=command_result.get("stdout"),
            stderr=command_result.get("stderr"),
        )
    payload = redact_nested(payload)
    if isinstance(payload, dict) and payload.get("status") == "ok":
        return success_check(**{key: value for key, value in payload.items() if key != "status"})
    if isinstance(payload, dict) and payload.get("status") == "blocked":
        return blocked_check(
            str(payload.get("blocked_reason", "container provider smoke blocked")),
            **{key: value for key, value in payload.items() if key not in {"status", "blocked_reason"}},
        )
    return failed_check(
        str(payload.get("error", "container provider smoke failed")) if isinstance(payload, dict) else str(payload),
        **({key: value for key, value in payload.items() if key not in {"status", "error"}} if isinstance(payload, dict) else {}),
    )


def redact_nested(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): redact_nested(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_nested(item) for item in value]
    if isinstance(value, str):
        return redact(value)
    return value


def iter_checks(payload: Any, prefix: str = "") -> Iterable[tuple[str, Check]]:
    if isinstance(payload, dict) and "status" in payload:
        yield prefix.rstrip("."), payload
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield from iter_checks(value, f"{prefix}{key}.")


def summarize(payload: dict[str, Any], *, strict: bool) -> dict[str, Any]:
    failures: list[str] = []
    blocked: list[str] = []
    expected_unavailable: list[str] = []
    checked = 0
    for name, check in iter_checks(payload.get("checks", {})):
        checked += 1
        status = check.get("status")
        if status == "failed":
            failures.append(name)
        elif status == "blocked":
            blocked.append(name)
        elif status == "expected_unavailable":
            expected_unavailable.append(name)

    if failures or (strict and blocked):
        status = "failed"
    elif blocked:
        status = "blocked"
    else:
        status = "ok"

    return {
        "status": status,
        "strict": strict,
        "checks_total": checked,
        "failed_checks": failures,
        "blocked_checks": blocked,
        "expected_unavailable_checks": expected_unavailable,
    }


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    configured_models = parse_csv(args.models) or [
        settings.deepseek_model,
        settings.cheap_model,
    ]
    unique_models = []
    for model in configured_models:
        if model and model not in unique_models:
            unique_models.append(model)

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": "KnowledgeOps external/runtime interface smoke.",
        "provider_endpoint": endpoint_metadata(settings.deepseek_base_url)
        if settings.deepseek_base_url
        else None,
        "checks": {
            "provider": {
                "models_list": provider_models_check(timeout=args.timeout),
                "chat_models": {
                    model: provider_chat_check(model, timeout=args.timeout, expected_available=True)
                    for model in unique_models
                },
                "expected_unavailable_models": {
                    model: provider_chat_check(model, timeout=args.timeout, expected_available=False)
                    for model in parse_csv(args.expected_unavailable_models)
                },
            }
        },
    }

    if not args.skip_local_services:
        payload["checks"]["local_services"] = {
            "api_health": http_check("http://localhost:8000/health", timeout=args.timeout),
            "langfuse_web": http_check("http://localhost:3000", timeout=args.timeout),
            "milvus_health": http_check("http://localhost:9092/healthz", timeout=args.timeout),
            "minio_health": http_check("http://localhost:9090/minio/health/live", timeout=args.timeout),
            "clickhouse_ping": http_check("http://localhost:8123/ping", timeout=args.timeout),
        }

    if not args.skip_docker_exec:
        payload["checks"]["docker"] = {
            "compose_ps": docker_compose_ps_check(timeout=args.timeout),
            "exec": docker_exec_checks(timeout=args.timeout),
        }

    if args.include_container_provider:
        payload["checks"].setdefault("docker", {})
        payload["checks"]["docker"]["app_container_provider"] = app_container_provider_check(
            settings.deepseek_model,
            timeout=args.timeout,
        )

    payload["summary"] = summarize(payload, strict=args.strict)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run KnowledgeOps external interface smoke checks.")
    parser.add_argument(
        "--models",
        default="",
        help="Comma-separated provider models expected to be callable. Defaults to configured deepseek/cheap models.",
    )
    parser.add_argument(
        "--expected-unavailable-models",
        default="deepseek-chat,deepseek-reasoner",
        help="Comma-separated legacy aliases to probe without failing when unavailable.",
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", default=None)
    parser.add_argument(
        "--skip-local-services",
        action="store_true",
        help="Skip localhost API/Langfuse/Milvus/MinIO/ClickHouse HTTP checks.",
    )
    parser.add_argument(
        "--skip-docker-exec",
        action="store_true",
        help="Skip docker compose ps/exec checks for ClickHouse/Postgres/Redis.",
    )
    parser.add_argument(
        "--include-container-provider",
        action="store_true",
        help="Also call the configured provider from the running Docker app container.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any checked interface fails or is blocked.",
    )
    args = parser.parse_args()

    payload = run_smoke(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    write_json_output(payload, args.output)
    return 0 if payload["summary"]["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
