from __future__ import annotations

import asyncio
import sqlite3 as _sql
from abc import ABC
from pathlib import Path

from data.implementation.utilities.caching import RecursiveCacheHandler


class AbstractSQLDatabase(ABC):
    _METADATA_SCHEMA_VERSION = 1

    def __init__(
        self,
        db_path: str,
        schema_name: str,
        schema_version: int = 1,
    ) -> None:
        """
        :param db_path: Path to target database file
        :param schema_name: Name of schema. Example: fact for fact.sql
        :param schema_version: Target version of schema.
        """
        self.path = db_path

        schema_path = Path(f'data/schemas/{schema_name}.sql')

        if not schema_path.is_file():
            raise FileNotFoundError(
                f"Schema at {schema_path} does not exist"
            )

        with _sql.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            self._ensure_metadata(conn)
            self._update_schema(
                conn,
                schema_path,
                schema_name,
                schema_version,
            )

    def _ensure_metadata(self, conn: _sql.Connection) -> None:
        version = conn.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        if version == 0:
            with open(f'data/schemas/metadata.sql', 'r') as f:
                conn.executescript(f.read())

            version = conn.execute(
                "PRAGMA user_version"
            ).fetchone()[0]

        if version > self._METADATA_SCHEMA_VERSION:
            raise RuntimeError(
                f"Database metadata version {version} is newer than "
                f"supported version {self._METADATA_SCHEMA_VERSION}"
            )
        elif version == self._METADATA_SCHEMA_VERSION:
            return

        # Needs updates
        migrations_path = Path('data/schemas/migrations/metadata')

        for new_version in range(
                version + 1,
                self._METADATA_SCHEMA_VERSION + 1,
        ):
            migration_path = migrations_path / f"{new_version:03d}.sql"

            if not migration_path.is_file():
                raise FileNotFoundError(
                    f"Migration for schema 'metadata' "
                    f"version {new_version} does not exist at "
                    f"{migration_path}"
                )

            with migration_path.open("r") as f:
                conn.executescript(f.read())

            version = conn.execute(
                "PRAGMA user_version"
            ).fetchone()[0]

            if version != new_version:
                raise ValueError(f'Attempted to update metadata to version {new_version} but found finalized version at {version} instead')

            print(f'Migrated metadata for to version {new_version}')

    def _update_schema(
        self,
        conn: _sql.Connection,
        schema_path: Path,
        schema_name: str,
        target_version: int,
    ) -> None:
        row = self._get_schema_version(conn, schema_name)

        if row is None:
            current_version = 0
        else:
            current_version = row

        if current_version > target_version:
            raise RuntimeError(
                f"Schema '{schema_name}' is at version "
                f"{current_version}, but this implementation only "
                f"supports version {target_version}"
            )

        if current_version == 0:
            # Load and create initial schema
            with schema_path.open("r") as f:
                conn.executescript(f.read())

            conn.execute(
                """
                INSERT INTO SchemaVersions (SchemaName, Version)
                VALUES (?, ?)
                """,
                (schema_name, 1),
            )
            print(f'Inserted schema {schema_name} into database.')

            current_version = 1 # Continue updating and applying.

        if current_version < target_version:
            migrations_path = (
                schema_path.parent / "migrations" / schema_name
            )

            for version in range(
                current_version + 1,
                target_version + 1,
            ):
                migration_path = migrations_path / f"{version:03d}.sql"

                if not migration_path.is_file():
                    raise FileNotFoundError(
                        f"Migration for schema '{schema_name}' "
                        f"version {version} does not exist at "
                        f"{migration_path}"
                    )

                with migration_path.open("r") as f:
                    conn.executescript(f.read())

                # Ensure the script did the right thing.
                row = self._get_schema_version(conn, schema_name)

                if row is None:
                    raise IndexError(f'No version set for {schema_name} target version {version}')
                else:
                    current_version = row
                    if not current_version == version:
                        raise ValueError(f'Migration script for {schema_name} target version {version} set version to {current_version} instead.')

                print(f'Migrated {schema_name} to version {version}')

    def _get_schema_version(
            self,
            conn: _sql.Connection,
            schema_name: str,
    ) -> int | None:
        row = conn.execute(
            """
            SELECT Version
            FROM SchemaVersions
            WHERE SchemaName = ?
            """,
            (schema_name,),
        ).fetchone()

        return None if row is None else row[0]


    def _connection(self) -> _sql.Connection:
        conn = _sql.connect(self.path)
        conn.row_factory = _sql.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

class CachedAbstractSQLDatabase(AbstractSQLDatabase, ABC):
    def __init__(self, db_path: str, schema_name: str, schema_version: int, default_cache_timeout: float) -> None:
        super().__init__(
            db_path=db_path,
            schema_name=schema_name,
            schema_version=schema_version,
        )

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