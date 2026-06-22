from pathlib import Path

from src.agents.document_tools import count_references


def test_reference_count_tool_counts_numbered_references(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        """
        <body>
          <h1>Paper</h1>
          <h2>References</h2>
          <p>[1] Alpha reference.</p>
          <p>[2] Beta reference.</p>
          <p>[3] Gamma reference.</p>
        </body>
        """,
        encoding="utf-8",
    )

    result = count_references(docs_dir)

    assert result.status == "ok"
    assert result.count == 3
    assert result.source and result.source.endswith("paper.html")
    assert result.evidence
    assert result.evidence[0]["reference_count"] == 3


def test_reference_count_tool_blocks_when_references_missing(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        "<body><p>No bibliography here.</p></body>",
        encoding="utf-8",
    )

    result = count_references(docs_dir)

    assert result.status == "blocked"
    assert result.count is None
    assert result.blocked_reason == "No references section was located."

