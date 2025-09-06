"""Database connection management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union


class DatabaseConnection:
    """Manages SQLite database connection."""

    def __init__(self, db_path: Path) -> None:
        """Initialize database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Establish database connection."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute(
        self, query: str, params: Union[Tuple[Any, ...], Dict[str, Any]] = ()
    ) -> List[Dict[str, Any]]:
        """Execute a query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")

        cursor = self.connection.cursor()
        if isinstance(params, dict):
            cursor.execute(query, params)
        else:
            cursor.execute(query, params)

        if cursor.description:
            return [dict(row) for row in cursor.fetchall()]
        return []

    def execute_many(
        self, query: str, params_list: Sequence[Union[Tuple[Any, ...], Dict[str, Any]]]
    ) -> None:
        """Execute a query multiple times with different parameters.

        Args:
            query: SQL query to execute
            params_list: List of parameter sets
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")

        cursor = self.connection.cursor()
        cursor.executemany(query, params_list)

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Context manager for database transactions.

        Yields:
            None

        Raises:
            Exception: Re-raises any exception after rollback
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")

        try:
            yield
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def commit(self) -> None:
        """Commit current transaction."""
        if self.connection:
            self.connection.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        if self.connection:
            self.connection.rollback()
