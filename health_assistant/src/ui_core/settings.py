# src/ui_core/settings.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import os
import streamlit as st


@dataclass(frozen=True)
class Settings:
    # For chat APIs
    base_url: str  # e.g. https://healthcare-ai.goshoppie.com

    # For direct DB prompt editing
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    db_sslmode: str = "require"


def _get_secret(path: str, default: Optional[Any] = None) -> Any:
    """
    Read st.secrets with dotted paths like:
      database.host
      database.port
    """
    cur: Any = st.secrets
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def load_settings() -> Settings:
    base_url = (
        _get_secret("BASE_URL")
        or os.getenv("BASE_URL")
        or "https://healthcare-ai.goshoppie.com"
    )

    db_host = (
        _get_secret("database.host")
        or os.getenv("HEALTHCARE_AI_DB_HOST")
        or "shoppie-server-do.postgres.database.azure.com"
    )
    db_port = int(
        _get_secret("database.port", 5432) or os.getenv("HEALTHCARE_AI_DB_PORT", "5432")
    )
    db_user = (
        _get_secret("database.user") or os.getenv("HEALTHCARE_AI_DB_USER") or "doadmin"
    )
    db_password = (
        _get_secret("database.password")
        or os.getenv("HEALTHCARE_AI_DB_PASS")
        or "Wb9!Dn6uY^kRe3Xs"
    )
    db_name = (
        _get_secret("database.dbname")
        or os.getenv("HEALTHCARE_AI_DB_BASE")
        or "healthcare-ai"
    )
    db_sslmode = _get_secret("database.sslmode", "require") or os.getenv(
        "HEALTHCARE_AI_DB_SSLMODE", "require"
    )

    return Settings(
        base_url=base_url,
        db_host=db_host,
        db_port=db_port,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        db_sslmode=db_sslmode,
    )
