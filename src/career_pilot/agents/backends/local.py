from __future__ import annotations

import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from career_pilot.config import Settings
from career_pilot.prompts.job_scout import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from career_pilot.schemas import JobMatch, ScoutResult, SuggestedRole
from career_pilot.tools.job_search import search_jobs


class _RoleSuggestion(BaseModel):
    title: str
    rationale: str
    search_queries: list[str] = Field(default_factory=list)


class _LLMRoleResponse(BaseModel):
    roles: list[_RoleSuggestion] = Field(default_factory=list)
    summary: str = ""


def run_local_scout(resume: str, projects: str, settings: Settings) -> ScoutResult:
    """MVP Job Scout: LLM role suggestions + JSearch job lookups."""
    errors: list[str] = []
    roles: list[SuggestedRole] = []
    summary = ""

    try:
        llm_result = _suggest_roles(resume, projects, settings)
        roles = [
            SuggestedRole(
                title=r.title.strip(),
                rationale=r.rationale.strip(),
                search_queries=[q.strip() for q in r.search_queries if q.strip()]
                or [r.title.strip()],
            )
            for r in llm_result.roles[: settings.max_roles]
            if r.title.strip()
        ]
        summary = llm_result.summary.strip()
    except Exception as exc:  # noqa: BLE001 — fail soft for Master digest
        errors.append(f"Role suggestion failed: {exc}")
        return ScoutResult(
            suggested_roles=[],
            jobs=[],
            summary="Could not generate role suggestions.",
            errors=errors,
        )

    jobs: list[JobMatch] = []
    if not settings.jsearch_api_key:
        errors.append("JSEARCH_API_KEY is not set; skipped job search.")
    else:
        seen_urls: set[str] = set()
        for role in roles:
            if len(jobs) >= settings.max_jobs:
                break
            queries = role.search_queries or [role.title]
            for query in queries:
                if len(jobs) >= settings.max_jobs:
                    break
                try:
                    found = search_jobs(
                        query,
                        api_key=settings.jsearch_api_key,
                        location=settings.job_location,
                    )
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"Job search failed for '{query}': {exc}")
                    continue

                for job in found[: settings.jobs_per_role]:
                    if job.url in seen_urls:
                        continue
                    seen_urls.add(job.url)
                    job.matched_role = role.title
                    job.why_fit = (
                        f"Matches suggested role '{role.title}'. {role.rationale}"
                    )[:500]
                    jobs.append(job)
                    if len(jobs) >= settings.max_jobs:
                        break

    if not summary and roles:
        titles = ", ".join(r.title for r in roles)
        summary = f"Suggested roles based on your resume and projects: {titles}."

    return ScoutResult(
        suggested_roles=roles,
        jobs=jobs,
        summary=summary,
        errors=errors,
    )


def _suggest_roles(
    resume: str, projects: str, settings: Settings
) -> _LLMRoleResponse:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    client_kwargs: dict[str, Any] = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        client_kwargs["base_url"] = settings.openai_base_url
    client = OpenAI(**client_kwargs)

    system = SYSTEM_PROMPT.format(max_roles=settings.max_roles)
    user = USER_PROMPT_TEMPLATE.format(
        resume=resume.strip(),
        projects=projects.strip(),
        location=settings.job_location,
        max_roles=settings.max_roles,
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    content = response.choices[0].message.content or "{}"
    return _parse_role_response(content)


def _parse_role_response(content: str) -> _LLMRoleResponse:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc
    try:
        return _LLMRoleResponse.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"LLM JSON did not match schema: {exc}") from exc
