"""Future Cursor SDK Job Scout backend.

Set SCOUT_BACKEND=cursor once implemented. The facade in
`career_pilot.agents.job_scout` already dispatches on this name.
"""

from __future__ import annotations

from career_pilot.config import Settings
from career_pilot.schemas import ScoutResult


def run_cursor_scout(resume: str, projects: str, settings: Settings) -> ScoutResult:
    raise NotImplementedError(
        "SCOUT_BACKEND=cursor is reserved for a future Cursor SDK integration. "
        "Use SCOUT_BACKEND=local for the MVP."
    )
