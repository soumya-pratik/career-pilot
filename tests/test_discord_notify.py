from __future__ import annotations

from career_pilot.tools.discord_notify import _chunk_message, format_digest


def test_format_digest_includes_sections() -> None:
    text = format_digest(
        summary="You fit backend roles.",
        role_lines=["- **Backend Engineer** — strong Python"],
        job_lines=["- **BE** @ Acme — https://example.com"],
        errors=["JSEARCH skipped"],
    )
    assert "Career Pilot" in text
    assert "Suggested roles" in text
    assert "Matching jobs" in text
    assert "Notes / errors" in text


def test_chunk_message_splits_long_text() -> None:
    text = "a" * 50 + "\n" + "b" * 50
    chunks = _chunk_message(text, limit=60)
    assert len(chunks) >= 2
    assert "".join(chunks).replace("\n", "") == ("a" * 50 + "b" * 50)
