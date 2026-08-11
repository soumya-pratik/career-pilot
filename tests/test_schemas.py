from __future__ import annotations

from career_pilot.schemas import JobMatch, ScoutResult, SuggestedRole


def test_scout_result_roundtrip() -> None:
    result = ScoutResult(
        suggested_roles=[
            SuggestedRole(
                title="Backend Engineer",
                rationale="Strong Python APIs",
                search_queries=["python backend engineer remote"],
            )
        ],
        jobs=[
            JobMatch(
                title="Backend Engineer",
                company="Acme",
                location="Remote",
                url="https://example.com/job/1",
                matched_role="Backend Engineer",
                why_fit="Python + APIs",
            )
        ],
        summary="Good backend fit.",
        errors=[],
    )
    restored = ScoutResult.model_validate_json(result.model_dump_json())
    assert restored.suggested_roles[0].title == "Backend Engineer"
    assert restored.jobs[0].url.endswith("/1")
