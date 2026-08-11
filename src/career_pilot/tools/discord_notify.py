from __future__ import annotations

import httpx

DISCORD_CONTENT_LIMIT = 1900  # leave margin under Discord's 2000 char limit


def post_webhook(
    webhook_url: str,
    content: str,
    *,
    username: str = "Career Pilot",
    timeout: float = 30.0,
) -> None:
    """Post one or more messages to a Discord webhook.

    Long content is split into chunks under Discord's character limit.
    Raises ValueError if webhook_url is missing.
    Raises httpx.HTTPError on transport/HTTP failures.
    """
    if not webhook_url:
        raise ValueError("DISCORD_WEBHOOK_URL is not set")

    chunks = _chunk_message(content, DISCORD_CONTENT_LIMIT)
    with httpx.Client(timeout=timeout) as client:
        for chunk in chunks:
            response = client.post(
                webhook_url,
                json={"content": chunk, "username": username},
            )
            response.raise_for_status()


def format_digest(
    *,
    summary: str,
    role_lines: list[str],
    job_lines: list[str],
    errors: list[str] | None = None,
) -> str:
    """Build a Discord-friendly markdown digest."""
    parts: list[str] = ["**Career Pilot — Job Scout Digest**", ""]
    if summary:
        parts.append(summary.strip())
        parts.append("")

    if role_lines:
        parts.append("**Suggested roles**")
        parts.extend(role_lines)
        parts.append("")

    if job_lines:
        parts.append("**Matching jobs**")
        parts.extend(job_lines)
        parts.append("")

    if errors:
        parts.append("**Notes / errors**")
        for err in errors:
            parts.append(f"- {err}")

    return "\n".join(parts).strip()


def _chunk_message(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in text.splitlines(keepends=True):
        if current_len + len(line) > limit and current:
            chunks.append("".join(current).rstrip())
            current = []
            current_len = 0
        # Hard-split oversized single lines
        while len(line) > limit:
            chunks.append(line[:limit])
            line = line[limit:]
        current.append(line)
        current_len += len(line)
    if current:
        chunks.append("".join(current).rstrip())
    return chunks
