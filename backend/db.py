import sqlite3
import os

_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "seed.db")

def _connect():
    uri = f"file:{_DB_PATH}?mode=ro"
    con = sqlite3.connect(uri, uri=True, check_same_thread=False)
    con.execute("PRAGMA query_only = ON")
    con.row_factory = sqlite3.Row
    return con

connection = _connect()
