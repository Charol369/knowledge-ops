# Sprint 1: Minimal Research Loop + Evidence Pipeline

## Why
KnowledgeOps needs a local, reproducible research loop before advanced retrieval, agent graph, policy, or demo work can be safely implemented.

## What
- Implement document ingestion for PDF, Word, and HTML with source/page metadata where applicable.
- Add chunking, embedding configuration, FAISS dense index persistence, and dense retrieval.
- Build a minimal planner and CLI research loop: question -> plan -> retrieve -> synthesize -> answer.
- Persist session artifacts for plan, evidence, and final answer.
- Add `/api/v1/ingest` skeleton without authentication.
- Add unit loader tests and Sprint 1 baseline benchmark documentation.

## Non-Code / Manual Boundaries
- No real API keys or paid external model calls are required.
- No cloud deployment, real demo video, resume, or job-application work belongs in this Sprint.
- Benchmark documentation may record only locally executed Sprint 1 baseline results.

## Dependencies
This is the foundation Sprint and has no prior Sprint dependency.
