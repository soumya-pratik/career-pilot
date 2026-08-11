from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: .../career-pilot (parent of src/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")

    jsearch_api_key: str = Field(default="", alias="JSEARCH_API_KEY")

    discord_webhook_url: str = Field(default="", alias="DISCORD_WEBHOOK_URL")

    scout_backend: Literal["local", "cursor"] = Field(
        default="local", alias="SCOUT_BACKEND"
    )

    resume_path: Path = Field(
        default=PROJECT_ROOT / "data" / "resume.md", alias="RESUME_PATH"
    )
    projects_path: Path = Field(
        default=PROJECT_ROOT / "data" / "projects.md", alias="PROJECTS_PATH"
    )
    output_dir: Path = Field(default=PROJECT_ROOT / "output", alias="OUTPUT_DIR")

    job_location: str = Field(default="Remote", alias="JOB_LOCATION")
    jobs_per_role: int = Field(default=3, alias="JOBS_PER_ROLE")
    max_roles: int = Field(default=5, alias="MAX_ROLES")
    max_jobs: int = Field(default=10, alias="MAX_JOBS")


def get_settings() -> Settings:
    return Settings()
