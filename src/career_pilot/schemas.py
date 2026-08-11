from __future__ import annotations

from pydantic import BaseModel, Field


class SuggestedRole(BaseModel):
    title: str
    rationale: str
    search_queries: list[str] = Field(default_factory=list)


class JobMatch(BaseModel):
    title: str
    company: str
    location: str = ""
    url: str
    source: str = "jsearch"
    why_fit: str = ""
    matched_role: str = ""


class ScoutResult(BaseModel):
    suggested_roles: list[SuggestedRole] = Field(default_factory=list)
    jobs: list[JobMatch] = Field(default_factory=list)
    summary: str = ""
    errors: list[str] = Field(default_factory=list)
