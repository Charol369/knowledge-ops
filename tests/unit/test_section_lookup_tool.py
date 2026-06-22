from pathlib import Path

from src.agents.document_tools import blocked_table_lookup_result, lookup_section


def test_section_lookup_tool_returns_section_scoped_evidence(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        """
        <body>
          <p>1 Introduction</p>
          <p>Intro text.</p>
          <p>3.2 Attention</p>
          <p>Multi-head attention section evidence.</p>
          <p>3.3 Training</p>
          <p>Training section text.</p>
        </body>
        """,
        encoding="utf-8",
    )

    result = lookup_section(docs_dir, "Summarize section 3.2")

    assert result.status == "ok"
    assert result.section_id == "3.2"
    assert result.section_title == "3.2 Attention"
    assert result.evidence
    assert "Multi-head attention section evidence" in result.evidence[0]["content"]
    assert "Training section text" not in result.evidence[0]["content"]


def test_section_lookup_tool_blocks_when_section_missing(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        "<body><p>1 Introduction</p><p>Only introduction exists.</p></body>",
        encoding="utf-8",
    )

    result = lookup_section(docs_dir, "Summarize section 3.2")

    assert result.status == "blocked"
    assert result.blocked_reason == "Section 3.2 was not located in the local documents."


def test_table_lookup_is_blocked_in_p0():
    result = blocked_table_lookup_result()

    assert result["status"] == "blocked"
    assert "Table parsing/indexing is not available" in result["blocked_reason"]

