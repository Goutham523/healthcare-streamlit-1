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
        """Generate headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        return headers

    def get_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get chat history for a user."""
        url = f"{self.settings.base_url.rstrip('/')}/api/ai_chat/chats/{user_id}"
        try:
            r = self.session.get(url, headers=self._headers(), timeout=(5, 20))
            if r.status_code == 404:
                return []
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting chat history: {e}")
            return []

    def post_chat(self, user_id: int, message: str) -> Dict[str, Any]:
        """Send a chat message."""
        url = f"{self.settings.base_url.rstrip('/')}/api/v1/health-assistant/chat"
        payload = {"user_id": user_id, "user_message": message}
        try:
            r = self.session.post(
                url, json=payload, headers=self._headers(), timeout=(5, 60)
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error posting chat message: {e}")
            return {
                "error": str(e),
                "role": "assistant",
                "content": "Sorry, I encountered an error processing your request.",
            }

    def submit_cardset(self, user_id: int, answers: Dict[str, str]) -> Dict[str, Any]:
        """Submit a completed cardset."""
        url = f"{self.settings.base_url.rstrip('/')}/api/v1/health-assistant/cardset/submit"
        payload = {"user_id": user_id, "answers": answers}
        try:
            r = self.session.post(
                url, json=payload, headers=self._headers(), timeout=(5, 60)
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error submitting cardset: {e}")
            return {"status": "error", "message": f"Failed to submit cardset: {e}"}

    def delete_history(self, user_id: int):
        url = f"{self.settings.base_url.rstrip('/')}/api/ai_chat/chats/{user_id}"
        r = self.session.delete(url, headers=self._headers(), timeout=(5, 20))
        # If backend returns 404 for "no history", treat as already cleared
        if r.status_code == 404:
            return {"status": "ok", "message": "No history to delete"}
        r.raise_for_status()
        return r.json() if r.content else {"status": "ok"}
