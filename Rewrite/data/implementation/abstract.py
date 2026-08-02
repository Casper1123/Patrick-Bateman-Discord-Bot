import sqlite3 as _sql
from abc import ABC


class AbstractSQLDatabase(ABC):
    def __init__(self, db_path: str, schema_path: str) -> None:
        self.path = db_path
        with _sql.connect(db_path) as conn:
            with open(schema_path, "r") as f:
                conn.executescript(f.read())

    def _connection(self) -> _sql.Connection:
        conn = _sql.connect(self.path)
        conn.row_factory = _sql.Row
        return conn