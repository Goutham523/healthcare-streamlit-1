import json
from typing import Any, Dict, List, Optional
import requests
from dataclasses import dataclass


@dataclass
class Settings:
    base_url: str
    api_key: str = ""


def load_settings() -> Settings:
    """Load settings from environment variables or configuration."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    return Settings(
        base_url=os.getenv("API_BASE_URL", "https://healthcare-ai.goshoppie.com"),
        api_key=os.getenv("API_KEY", ""),
    )


class APIClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        return headers

    # -------------------------
    # CHAT HISTORY
    # -------------------------
    def get_history(self, user_id: int) -> List[Dict[str, Any]]:
        url = f"{self.settings.base_url.rstrip('/')}/api/v2/chats/{user_id}"
        r = self.session.get(url, headers=self._headers(), timeout=(5, 20))
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return r.json()

    def delete_history(self, user_id: int) -> Dict[str, Any]:
        url = f"{self.settings.base_url.rstrip('/')}/api/v2/chats/delete/{user_id}"
        r = self.session.delete(url, headers=self._headers(), timeout=(5, 20))
        if r.status_code == 404:
            return {"success": True}
        r.raise_for_status()
        return r.json()

    # -------------------------
    # MAIN CHAT STREAM
    # -------------------------
    def post_chat(self, user_id: int, message: str) -> Dict[str, Any]:
        url = f"{self.settings.base_url.rstrip('/')}/api/v2/chats/stream"
        payload = {
            "user_id": user_id,
            "user_message": message,
        }
        r = self.session.post(
            url, json=payload, headers=self._headers(), timeout=(5, 60)
        )
        r.raise_for_status()
        return r.json()

    # -------------------------
    # CARDSET SUBMIT
    # -------------------------
    def submit_cardset(
        self,
        user_id: int,
        session_id: int,
        answers: Dict[str, str],
    ) -> Dict[str, Any]:
        url = f"{self.settings.base_url.rstrip('/')}/api/v2/chats/cardset/submit"
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "answers": answers,
        }
        r = self.session.post(
            url, json=payload, headers=self._headers(), timeout=(5, 60)
        )
        r.raise_for_status()
        return r.json()
