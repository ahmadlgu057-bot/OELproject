"""
Database connection manager.

Provides a centralised helper for obtaining MySQL connections and
executing queries with automatic commit / rollback semantics.
"""

import mysql.connector
from mysql.connector import Error as MySQLError

from app.config import DB_CONFIG


class DatabaseManager:
    """Manages MySQL database connections and query execution."""

    def __init__(self, config: dict | None = None):
        """
        Initialise with optional config override.

        Args:
            config: Dictionary with host, port, user, password, database keys.
                    Falls back to ``DB_CONFIG`` from *config.py*.
        """
        self._config = config or DB_CONFIG

    # ── Connection helpers ──────────────────────────────────────────────

    def get_connection(self):
        """Return a new MySQL connection using the stored config."""
        try:
            connection = mysql.connector.connect(**self._config)
            return connection
        except MySQLError as err:
            raise ConnectionError(
                f"Failed to connect to MySQL: {err}"
            ) from err

    # ── Query execution ─────────────────────────────────────────────────

    def execute_query(self, query: str, params: tuple = ()) -> int | None:
        """
        Execute a write query (INSERT / UPDATE / DELETE) and return the
        last‑inserted row id (or ``None`` for non‑INSERT statements).

        Args:
            query:  SQL statement with ``%s`` placeholders.
            params: Tuple of parameter values.

        Returns:
            The ``lastrowid`` for INSERT statements, else ``None``.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            return cursor.lastrowid
        except MySQLError as err:
            connection.rollback()
            raise RuntimeError(f"Query execution failed: {err}") from err
        finally:
            cursor.close()
            connection.close()

    def execute_read(self, query: str, params: tuple = ()) -> list[dict]:
        """
        Execute a SELECT query and return rows as a list of dictionaries.

        Args:
            query:  SQL SELECT statement with ``%s`` placeholders.
            params: Tuple of parameter values.

        Returns:
            List of dicts, one per row, keyed by column name.
        """
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except MySQLError as err:
            raise RuntimeError(f"Read query failed: {err}") from err
        finally:
            cursor.close()
            connection.close()

    def execute_read_one(self, query: str, params: tuple = ()) -> dict | None:
        """
        Execute a SELECT query and return the first row as a dictionary,
        or ``None`` if the result set is empty.
        """
        rows = self.execute_read(query, params)
        return rows[0] if rows else None


# ── Module‑level singleton for convenience ──────────────────────────────
db = DatabaseManager()
