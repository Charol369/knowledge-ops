"""Streamlit UI for the KnowledgeOps enterprise knowledge-base QA flow.

Run:
  uv run streamlit run frontend/app.py
"""
from __future__ import annotations

import json
import os
from typing import Any
from uuid import uuid4

import httpx
import streamlit as st


DEFAULT_API_BASE_URL = os.getenv("KNOWLEDGE_OPS_API_URL", "http://localhost:8000")
REQUEST_TIMEOUT_SECONDS = 120.0
SESSION_STATE_KEY = "knowledge_ops_session_id"


def build_api_headers(api_key: str | None) -> dict[str, str]:
    key = (api_key or "").strip()
    return {"X-API-Key": key} if key else {}


def create_session_id() -> str:
    return f"sess_{uuid4().hex}"


def parse_sse_events(payload: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    event_name = "message"
    data_lines: list[str] = []

    def flush_event() -> None:
        nonlocal event_name, data_lines
        if not data_lines:
            event_name = "message"
            return
        raw_data = "\n".join(data_lines)
        try:
            data: Any = json.loads(raw_data)
        except json.JSONDecodeError:
            data = raw_data
        events.append({"event": event_name, "data": data})
        event_name = "message"
        data_lines = []

    for raw_line in payload.splitlines():
        line = raw_line.strip()
        if not line:
            flush_event()
            continue
        if line.startswith("event:"):
            event_name = line.removeprefix("event:").strip() or "message"
        elif line.startswith("data:"):
            data_lines.append(line.removeprefix("data:").strip())
    flush_event()
    return events


def post_query_stream(
    *,
    api_base_url: str,
    payload: dict[str, Any],
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    url = f"{api_base_url.rstrip('/')}/api/v1/query/stream"
    with httpx.stream(
        "POST",
        url,
        json=payload,
        headers=build_api_headers(api_key),
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:
        response.raise_for_status()
        text = "".join(response.iter_text())
    return parse_sse_events(text)


def post_feedback(
    *,
    api_base_url: str,
    trace_id: str,
    score: float,
    comment: str | None,
    source: str = "streamlit-ui",
    api_key: str | None = None,
) -> dict[str, Any]:
    url = f"{api_base_url.rstrip('/')}/api/v1/feedback"
    response = httpx.post(
        url,
        json={
            "trace_id": trace_id,
            "score": score,
            "comment": comment or None,
            "source": source,
        },
        headers=build_api_headers(api_key),
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def extract_diagnostics_summary(result: dict[str, Any]) -> dict[str, Any]:
    diagnostics = result.get("diagnostics") if isinstance(result.get("diagnostics"), dict) else {}
    keys = (
        "intent",
        "strategy",
        "tool_name",
        "tool_status",
        "fallback_reason",
        "synthesis_mode",
        "synthesis_status",
        "synthesis_model",
    )
    summary: dict[str, Any] = {}
    for key in keys:
        value = result.get(key)
        if value is None:
            value = diagnostics.get(key)
        if value is not None:
            summary[key] = value
    return summary


def _apply_page_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ko-ink: #17211d;
            --ko-paper: #f7f2e8;
            --ko-line: #d8cbb7;
            --ko-accent: #1f6f5b;
            --ko-warm: #c56b37;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(197, 107, 55, 0.20), transparent 30rem),
                linear-gradient(135deg, #fbf7ef 0%, #e9f0e7 55%, #f6ead7 100%);
            color: var(--ko-ink);
        }
        .block-container {
            padding-top: 2rem;
            max-width: 1180px;
        }
        .ko-hero {
            border: 1px solid var(--ko-line);
            border-radius: 24px;
            padding: 1.4rem 1.6rem;
            background: rgba(255, 252, 246, 0.76);
            box-shadow: 0 18px 45px rgba(67, 48, 24, 0.10);
        }
        .ko-hero h1 {
            font-family: Georgia, 'Times New Roman', serif;
            letter-spacing: -0.04em;
            margin: 0 0 0.35rem 0;
        }
        .ko-label {
            color: var(--ko-accent);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.74rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_query_result(result: dict[str, Any]) -> None:
    st.subheader("Final Answer")
    st.markdown(result.get("answer") or "_No answer returned._")

    meta_columns = st.columns(6)
    meta_columns[0].metric("Confidence", f"{float(result.get('confidence', 0.0)):.2f}")
    meta_columns[1].metric("Session", result.get("session_id") or "n/a")
    meta_columns[2].metric("Trace", result.get("trace_id") or "n/a")
    meta_columns[3].metric("Artifact", result.get("artifact_session_id") or "n/a")
    meta_columns[4].metric("Synthesis", result.get("synthesis_mode") or "n/a")
    meta_columns[5].metric(
        "Human Review",
        "yes" if result.get("needs_human_review") else "no",
    )
    if result.get("synthesis_model") or result.get("synthesis_status"):
        st.caption(
            "synthesis_status="
            f"{result.get('synthesis_status') or 'n/a'}; "
            f"model={result.get('synthesis_model') or 'n/a'}"
        )
    if result.get("synthesis_blocked_reason"):
        st.warning(f"LLM synthesis fallback reason: {result['synthesis_blocked_reason']}")
    diagnostics_summary = extract_diagnostics_summary(result)
    if diagnostics_summary or result.get("tool_result") or result.get("diagnostics"):
        with st.expander("Advanced diagnostics", expanded=False):
            if diagnostics_summary:
                st.dataframe(
                    [{"field": key, "value": value} for key, value in diagnostics_summary.items()],
                    use_container_width=True,
                    hide_index=True,
                )
            if result.get("tool_result") is not None:
                st.caption("tool_result")
                st.json(result["tool_result"])
            if result.get("diagnostics") is not None:
                st.caption("raw diagnostics")
                st.json(result["diagnostics"])

    plan = result.get("plan") or []
    if plan:
        st.subheader("Plan")
        st.dataframe(plan, use_container_width=True, hide_index=True)

    citations = result.get("citations") or []
    st.subheader("Evidence / Citations")
    if not citations:
        st.info("No citations returned by the backend.")
    for index, citation in enumerate(citations, start=1):
        source = citation.get("source") or "unknown source"
        with st.expander(f"Citation {index}: {source}", expanded=index == 1):
            st.write(citation.get("snippet") or "No snippet.")
            st.caption(f"page: {citation.get('page')}")


def _render_feedback(api_base_url: str, api_key: str | None, result: dict[str, Any]) -> None:
    trace_id = result.get("trace_id")
    if not trace_id:
        st.info("Feedback requires a trace_id from the backend response.")
        return

    st.subheader("Feedback")
    score_label = st.radio(
        "Was this answer useful?",
        options=["Useful", "Neutral", "Not useful"],
        horizontal=True,
    )
    score_map = {"Useful": 1.0, "Neutral": 0.0, "Not useful": -1.0}
    comment = st.text_area("Comment", key="feedback_comment", height=90)
    if st.button("Submit feedback", type="secondary"):
        try:
            feedback_result = post_feedback(
                api_base_url=api_base_url,
                trace_id=trace_id,
                score=score_map[score_label],
                comment=comment,
                api_key=api_key,
            )
        except httpx.HTTPError as exc:
            st.error(f"Feedback failed: {exc}")
            return
        st.success(
            "Feedback captured locally; "
            f"Langfuse status: {feedback_result.get('langfuse_status')}"
        )
        if feedback_result.get("blocked_reason"):
            st.caption(feedback_result["blocked_reason"])


def main() -> None:
    st.set_page_config(
        page_title="KnowledgeOps",
        page_icon=None,
        layout="wide",
    )
    _apply_page_style()
    if SESSION_STATE_KEY not in st.session_state:
        st.session_state[SESSION_STATE_KEY] = create_session_id()

    st.markdown(
        """
        <div class="ko-hero">
          <div class="ko-label">Enterprise Knowledge QA</div>
          <h1>KnowledgeOps Answer Console</h1>
          <p>Ask questions against the indexed knowledge base and inspect
          grounded answers, citations, trace metadata, and feedback capture.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Backend")
        api_base_url = st.text_input("API base URL", value=DEFAULT_API_BASE_URL)
        api_key = st.text_input("API key", value="", type="password")
        st.header("Session")
        active_session_id = str(st.session_state[SESSION_STATE_KEY])
        st.caption(f"Auto session: {active_session_id}")
        if st.button("Start new session", type="secondary"):
            st.session_state[SESSION_STATE_KEY] = create_session_id()
            st.rerun()

        with st.expander("Advanced local / debug settings", expanded=False):
            manual_trace_id = st.text_input(
                "Manual trace/thread override",
                value="",
                help="Optional. Leave blank to use the automatic product session.",
            )
            docs_dir = st.text_input("docs_dir", value="data")
            index_dir = st.text_input("index_dir", value="data/faiss/sprint1")
            artifact_root = st.text_input("artifact_root", value="")
            embedding_backend = st.selectbox(
                "embedding_backend",
                options=["hash", "fake", "local", "huggingface"],
                index=0,
            )

    question = st.text_area(
        "Question",
        value="What is multi-head attention in Attention Is All You Need?",
        height=120,
    )

    if st.button("Ask knowledge base", type="primary"):
        if not question.strip():
            st.warning("Question is required.")
        else:
            payload: dict[str, Any] = {
                "question": question.strip(),
                "session_id": str(st.session_state[SESSION_STATE_KEY]),
                "docs_dir": docs_dir,
                "index_dir": index_dir,
                "embedding_backend": embedding_backend,
            }
            if manual_trace_id.strip():
                payload["thread_id"] = manual_trace_id.strip()
            if artifact_root.strip():
                payload["artifact_root"] = artifact_root.strip()

            progress_panel = st.status("Running knowledge query", expanded=True)
            try:
                events = post_query_stream(
                    api_base_url=api_base_url,
                    payload=payload,
                    api_key=api_key,
                )
            except httpx.HTTPStatusError as exc:
                progress_panel.update(label="Backend returned an error", state="error")
                st.error(f"{exc.response.status_code}: {exc.response.text[:500]}")
                return
            except httpx.HTTPError as exc:
                progress_panel.update(label="Backend request failed", state="error")
                st.error(str(exc))
                return

            completion: dict[str, Any] | None = None
            for event in events:
                event_name = event.get("event")
                data = event.get("data")
                if event_name == "progress" and isinstance(data, dict):
                    progress_panel.write(f"{data.get('stage')}: {data.get('trace_id')}")
                    if data.get("plan"):
                        progress_panel.write(f"Plan steps: {len(data['plan'])}")
                elif event_name == "completion" and isinstance(data, dict):
                    completion = data

            if completion is None:
                progress_panel.update(label="No completion event returned", state="error")
            else:
                st.session_state["last_response"] = completion
                progress_panel.update(label="Answer ready", state="complete")

    last_response = st.session_state.get("last_response")
    if isinstance(last_response, dict):
        _render_query_result(last_response)
        _render_feedback(api_base_url, api_key, last_response)


if __name__ == "__main__":
    main()
