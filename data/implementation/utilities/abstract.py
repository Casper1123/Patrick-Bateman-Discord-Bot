from __future__ import annotations

import asyncio
import os
import sqlite3 as _sql
from abc import ABC

from data.implementation.utilities.caching import RecursiveCacheHandler


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

class CachedAbstractSQLDatabase(AbstractSQLDatabase, ABC):
    def __init__(self, db_path: str, schema_path: str, default_cache_timeout: float) -> None:
        super().__init__(db_path, schema_path)

        self._default_cache_timeout = default_cache_timeout
        self._cache: RecursiveCacheHandler = RecursiveCacheHandler() # Root node.

    def get_cache_task(self) -> asyncio.Task:
        return asyncio.create_task(
            name=f'Cache maintenance of {type(self).__name__}',
            coro=self._cache.maintenance_loop(
                timeout=self._default_cache_timeout,
                clean_empty_nodes=True,
            )
        )