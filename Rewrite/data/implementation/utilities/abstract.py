from __future__ import annotations

import asyncio
from time import monotonic
import sqlite3 as _sql
from abc import ABC
import os
from typing import TypeVar

class AbstractSQLDatabase(ABC):
    def __init__(self, db_path: str, schema_path: str) -> None:
        self.path = db_path

        if not os.path.isfile(schema_path):
            raise FileNotFoundError(f"Schema at {schema_path} does not exist")

        with _sql.connect(db_path) as conn:
            with open(schema_path, "r") as f:
                conn.executescript(f.read())

    def _connection(self) -> _sql.Connection:
        conn = _sql.connect(self.path)
        conn.row_factory = _sql.Row
        return conn