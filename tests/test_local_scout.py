from __future__ import annotations

from unittest.mock import MagicMock, patch

from career_pilot.agents.backends.local import run_local_scout
from career_pilot.config import Settings
from career_pilot.schemas import JobMatch


def test_local_scout_skips_jobs_without_jsearch_key() -> None:
    settings = Settings(
        OPENAI_API_KEY="test-key",
        JSEARCH_API_KEY="",
        DISCORD_WEBHOOK_URL="",
        MAX_ROLES=3,
        MAX_JOBS=5,
        JOBS_PER_ROLE=2,
    )
    fake_llm = MagicMock()
    fake_llm.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=(
                        '{"roles":[{"title":"Backend Engineer","rationale":"Python",'
                        '"search_queries":["python backend remote"]}],'
                        '"summary":"Strong backend fit."}'
                    )
                )
            )
        ]
    )

    with patch("career_pilot.agents.backends.local.OpenAI", return_value=fake_llm):
        result = run_local_scout("resume text", "projects text", settings)

    assert len(result.suggested_roles) == 1
    assert result.suggested_roles[0].title == "Backend Engineer"
    assert result.jobs == []
    assert any("JSEARCH_API_KEY" in e for e in result.errors)


def test_local_scout_dedupes_and_caps_jobs() -> None:
    settings = Settings(
        OPENAI_API_KEY="test-key",
        JSEARCH_API_KEY="js-key",
        DISCORD_WEBHOOK_URL="",
        MAX_ROLES=2,
        MAX_JOBS=2,
        JOBS_PER_ROLE=5,
        JOB_LOCATION="Remote",
    )
    fake_llm = MagicMock()
    fake_llm.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=(
                        '{"roles":[{"title":"Backend Engineer","rationale":"Python",'
                        '"search_queries":["python backend"]}],'
                        '"summary":"Fit."}'
                    )
                )
            )
        ]
    )
    jobs = [
        JobMatch(
            title="A",
            company="C1",
            url="https://example.com/a",
            location="Remote",
        ),
        JobMatch(
            title="B",
            company="C2",
            url="https://example.com/a",  # duplicate URL
            location="Remote",
        ),
        JobMatch(
            title="C",
            company="C3",
            url="https://example.com/c",
            location="Remote",
        ),
        JobMatch(
            title="D",
            company="C4",
            url="https://example.com/d",
            location="Remote",
        ),
    ]

    with (
        patch("career_pilot.agents.backends.local.OpenAI", return_value=fake_llm),
        patch(
            "career_pilot.agents.backends.local.search_jobs",
            return_value=jobs,
        ) as search_mock,
    ):
        result = run_local_scout("resume", "projects", settings)

    assert search_mock.called
    assert len(result.jobs) == 2
    urls = [j.url for j in result.jobs]
    assert urls == ["https://example.com/a", "https://example.com/c"]
    assert all(j.matched_role == "Backend Engineer" for j in result.jobs)
