from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # Keep local analysis usable before dependencies are installed.
    def load_dotenv() -> None:
        return None


@dataclass(frozen=True)
class Settings:
    access_token: str
    author_urn: str
    linkedin_version: str
    database_path: str
    dry_run: bool


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        access_token=os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip(),
        author_urn=os.getenv("LINKEDIN_AUTHOR_URN", "").strip(),
        linkedin_version=os.getenv("LINKEDIN_VERSION", "202603").strip(),
        database_path=os.getenv("LINKEDIN_AGENT_DB", "linkedin_agents.sqlite3").strip(),
        dry_run=os.getenv("LINKEDIN_DRY_RUN", "true").strip().lower() in {"1", "true", "yes", "on"},
    )
