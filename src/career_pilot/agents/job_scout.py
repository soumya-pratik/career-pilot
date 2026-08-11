from __future__ import annotations

from career_pilot.agents.backends.cursor import run_cursor_scout
from career_pilot.agents.backends.local import run_local_scout
from career_pilot.config import Settings, get_settings
from career_pilot.schemas import ScoutResult


def run(resume: str, projects: str, settings: Settings | None = None) -> ScoutResult:
    """Job Scout facade — dispatches to the configured backend."""
    cfg = settings or get_settings()
    backend = cfg.scout_backend

    if backend == "local":
        return run_local_scout(resume, projects, cfg)
    if backend == "cursor":
        return run_cursor_scout(resume, projects, cfg)

    raise ValueError(f"Unknown SCOUT_BACKEND: {backend!r} (expected 'local' or 'cursor')")
