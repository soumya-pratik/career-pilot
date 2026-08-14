from __future__ import annotations

from typing import Any

import httpx

from career_pilot.schemas import JobMatch

JSEARCH_HOST = "jsearch.p.rapidapi.com"
JSEARCH_URL = f"https://{JSEARCH_HOST}/search-v2"


def search_jobs(
    query: str,
    *,
    api_key: str,
    location: str = "Remote",
    num_pages: int = 1,
    country: str = "us",
    date_posted: str = "all",
    timeout: float = 30.0,
) -> list[JobMatch]:
    """Search job postings via JSearch search-v2 (RapidAPI).

    Raises ValueError if api_key is missing.
    Raises httpx.HTTPError on transport/HTTP failures.
    """
    if not api_key:
        raise ValueError("JSEARCH_API_KEY is not set")

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": JSEARCH_HOST,
    }
    params: dict[str, Any] = {
        "query": query if not location else f"{query} in {location}",
        "num_pages": str(num_pages),
        "country": country,
        "date_posted": date_posted,
    }

    with httpx.Client(timeout=timeout) as client:
        response = client.get(JSEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        payload = response.json()

    results = _extract_jobs(payload)
    jobs: list[JobMatch] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        apply_link = item.get("job_apply_link") or item.get("job_google_link") or ""
        if not apply_link:
            continue
        jobs.append(
            JobMatch(
                title=str(item.get("job_title") or "Untitled"),
                company=str(item.get("employer_name") or "Unknown"),
                location=_format_location(item),
                url=str(apply_link),
                source="jsearch",
                why_fit="",
                matched_role="",
            )
        )
    return jobs


def _extract_jobs(payload: dict[str, Any]) -> list[Any]:
    """Support both legacy list `data` and search-v2 `{jobs: [...]}` shapes."""
    data = payload.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        jobs = data.get("jobs")
        if isinstance(jobs, list):
            return jobs
    return []


def _format_location(item: dict[str, Any]) -> str:
    city = item.get("job_city") or ""
    state = item.get("job_state") or ""
    country = item.get("job_country") or ""
    parts = [p for p in (city, state, country) if p]
    if item.get("job_is_remote"):
        parts.append("Remote")
    return ", ".join(parts) if parts else "Not specified"
