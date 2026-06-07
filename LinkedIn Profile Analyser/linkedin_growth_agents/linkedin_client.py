from __future__ import annotations

from .config import Settings


class LinkedInClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def publish_text_post(self, content: str) -> str:
        if self.settings.dry_run or not self.settings.access_token or not self.settings.author_urn:
            return "dry-run:post-not-sent"

        import requests

        response = requests.post(
            "https://api.linkedin.com/rest/posts",
            headers={
                "Authorization": f"Bearer {self.settings.access_token}",
                "Linkedin-Version": self.settings.linkedin_version,
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
            },
            json={
                "author": self.settings.author_urn,
                "commentary": content,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": [],
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.headers.get("x-restli-id", "published:no-urn-returned")
