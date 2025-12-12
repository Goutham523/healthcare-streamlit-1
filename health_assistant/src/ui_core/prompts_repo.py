from typing import Any, Dict, List, Optional
import json
from psycopg2.extras import DictCursor


def list_prompts(conn) -> List[Dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, updated_at FROM ai_prompts ORDER BY updated_at DESC"
        )
        rows = cur.fetchall()
        return [{"id": r[0], "name": r[1], "updated_at": str(r[2])} for r in rows]


def get_prompt(conn, name: str) -> Optional[Dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, prompt, meta, updated_at FROM ai_prompts WHERE name = %s",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "prompt": row[2],
            "meta": row[3],
            "updated_at": str(row[4]),
        }


def update_prompt(conn, name: str, prompt: str, meta: Dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE ai_prompts SET prompt = %s, meta = %s WHERE name = %s",
            (prompt, json.dumps(meta), name),  # keep it parameterized. [web:377]
        )
        conn.commit()
