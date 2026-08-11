from __future__ import annotations

import json
from pathlib import Path

from career_pilot.agents import job_scout
from career_pilot.config import Settings, get_settings
from career_pilot.schemas import ScoutResult
from career_pilot.tools.discord_notify import format_digest, post_webhook


def run(
    *,
    settings: Settings | None = None,
    notify: bool = True,
    persist: bool = True,
) -> ScoutResult:
    """Master agent: run Job Scout, persist findings, optionally notify Discord."""
    cfg = settings or get_settings()
    resume = _read_text(cfg.resume_path)
    projects = _read_text(cfg.projects_path)

    result = job_scout.run(resume, projects, cfg)

    if persist:
        _persist_result(result, cfg.output_dir)

    if notify:
        _notify_discord(result, cfg)

    return result


def _read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


def _persist_result(result: ScoutResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "latest_run.json"
    out_path.write_text(
        result.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return out_path


def _notify_discord(result: ScoutResult, settings: Settings) -> None:
    role_lines = [
        f"- **{role.title}** — {role.rationale}"
        for role in result.suggested_roles
    ]
    job_lines = [
        (
            f"- **{job.title}** @ {job.company}"
            f" ({job.location or 'n/a'})"
            f" — role: {job.matched_role or 'n/a'}"
            f"\n  {job.url}"
        )
        for job in result.jobs
    ]
    content = format_digest(
        summary=result.summary,
        role_lines=role_lines,
        job_lines=job_lines,
        errors=result.errors or None,
    )
    post_webhook(settings.discord_webhook_url, content)


def result_to_pretty_json(result: ScoutResult) -> str:
    return json.dumps(result.model_dump(), indent=2)
