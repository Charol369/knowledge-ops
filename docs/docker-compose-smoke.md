# Docker Compose + Local Langfuse Smoke

Date: 2026-06-22

This document records the local full-stack Docker Compose smoke that was actually executed. It does not claim cloud deployment, production persistence, real bge-m3 inference, real RAGAS scoring, or 100 QPS load-test completion.

## Environment

| Item | Observed value |
|---|---|
| OS | Windows local development machine |
| Docker CLI / Engine | `29.4.3` |
| Docker Desktop | `4.73.0` |
| Docker Compose | `v5.1.3` |
| API endpoint | `http://localhost:8000` |
| Langfuse UI | `http://localhost:3000` |
| Milvus | `localhost:19530`, health on `localhost:9092/healthz` |
| MinIO | API `localhost:9090`, console `localhost:9091` |

## Services Verified

`docker compose ps` showed these services running locally:

| Service | Status observed |
|---|---|
| `knowledge-ops-app` | `Up`, healthy |
| `knowledge-ops-milvus` | `Up`, healthy |
| `knowledge-ops-langfuse-web` | `Up` |
| `knowledge-ops-langfuse-worker` | `Up` |
| `knowledge-ops-clickhouse` | `Up`, healthy |
| `knowledge-ops-postgres` | `Up`, healthy |
| `knowledge-ops-redis` | `Up`, healthy |
| `knowledge-ops-minio` | `Up`, healthy |

## Smoke Commands And Evidence

| Check | Result |
|---|---|
| `Invoke-WebRequest http://localhost:8000/health` | `200`, `{"status":"ok","version":"0.0.1"}` |
| `Invoke-WebRequest http://localhost:3000` | `200`, Langfuse web HTML returned |
| `Invoke-WebRequest http://localhost:9092/healthz` | `200`, `OK` |
| POST `/api/v1/query` | `200`, returned 3-step plan, 5 citations, confidence `0.85`, artifact session `20260622T065008Z-7380c05d` |
| POST `/api/v1/feedback` | `200`, `langfuse_status=recorded` |
| POST `/api/v1/query/stream` | `progress -> progress -> completion`, artifact session `20260622T065503Z-d21505ba` |
| ClickHouse `traces` lookup | trace id `54c7f956ce5e27e7daf5fd007adc051e` present |
| ClickHouse `scores` lookup | score attached to the same trace id `54c7f956ce5e27e7daf5fd007adc051e` |

## Trace Alignment

Application-facing trace id:

```text
docker-compose-langfuse-aligned-20260622
```

Langfuse/W3C trace id used for local trace and score:

```text
54c7f956ce5e27e7daf5fd007adc051e
```

The API still returns the application trace id. Internally, Langfuse tracing and feedback scoring map the application trace id to a deterministic 32-character lowercase hex trace id so trace and score are queryable under the same Langfuse id.

## Fixes Required During Smoke

| Issue | Fix |
|---|---|
| `langfuse-worker` rejected `ENCRYPTION_KEY` | Quoted the 64-character hex string in `docker-compose.yml` so Compose passes it as a string. |
| `langfuse-web` failed ClickHouse migrations with `Permission denied` | Moved ClickHouse data/log storage from Windows bind mounts to Docker named volumes. |
| Docker app build attempted to install large Torch/CUDA transitive packages | Added lightweight `requirements.docker.txt` and made HuggingFace embedding import lazy. Docker smoke uses `embedding_backend=hash`. |
| Docker build context included local data and agent cache directories | Added `.dockerignore` to exclude `data/`, `.venv/`, `.claude/`, `.continue/`, and other local-only paths. |
| Langfuse score wrote to the application trace id, while LangGraph callback generated another id | Added deterministic trace id mapping and passed `trace_context` to the Langfuse LangChain callback. |

## Paid API Check

The configured OpenAI-compatible endpoint was reachable and `/models` returned 18 models. The current provider exposes two DeepSeek-named models:

- `deepseek-v4-pro`
- `deepseek-v4-flash`

Minimal Chat Completions requests succeeded for both current models:

| Model requested | Result |
|---|---|
| `deepseek-v4-pro` | request succeeded, response content `ok` |
| `deepseek-v4-flash` | request succeeded, response content `ok` |
| Docker app container configured model | request succeeded, response content `ok` |

The current provider does not expose the official aliases `deepseek-chat` or `deepseek-reasoner`; both are treated as expected-unavailable for this provider. Do not claim official DeepSeek endpoint verification, production cost tracking, or main-chain paid generation from this smoke alone.

## Remaining Boundaries

| Item | Status |
|---|---|
| Real `bge-m3` inside Docker | Not included in the lightweight Docker app image. |
| Real RAGAS metrics | Not run. Existing RAGAS path remains dry-run scaffold. |
| Locust 100 QPS x 5min | Not run. |
| Cloud deployment | Not run. |
| Production secrets / TLS / reverse proxy | Not configured. |
| Official DeepSeek endpoint / aliases | Not verified; current provider uses `deepseek-v4-pro` / `deepseek-v4-flash`, while `deepseek-chat` / `deepseek-reasoner` are unavailable. |
