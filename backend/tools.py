from .db import connection

TOOLS = [
    {
        "name": "run_sql",
        "description": (
            "Execute a read-only SQL SELECT query against the manufacturing database. "
            "Use this for every factual question about the data. "
            "Only SELECT (or WITH...SELECT) is allowed. No semicolons. "
            "Results are capped at 200 rows."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A single SQL SELECT statement. Use the schema in the system prompt."
                }
            },
            "required": ["query"]
        }
    }
]


def execute_run_sql(query: str) -> dict:
    stripped = query.strip()
    upper = stripped.upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return {"error": "Only SELECT or WITH...SELECT queries are allowed."}
    if ";" in stripped:
        return {"error": "Semicolons are not allowed in queries."}
    try:
        cursor = connection.execute(stripped)
        rows = cursor.fetchmany(201)
        truncated = len(rows) > 200
        rows = rows[:200]
        return {
            "row_count": len(rows),
            "truncated": truncated,
            "rows": [dict(r) for r in rows],
        }
    except Exception as e:
        return {"error": str(e)}
