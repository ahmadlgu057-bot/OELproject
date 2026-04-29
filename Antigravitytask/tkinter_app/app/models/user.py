"""
User data model.

Provides CRUD operations for the ``users`` table, which stores
administrator and librarian accounts with hashed passwords.
"""

from app.utils.database import db


class UserModel:
    """Encapsulates all database operations for the *users* table."""

    # ── Create ──────────────────────────────────────────────────────────

    @staticmethod
    def create(username: str, password_hash: str, role: str = "librarian") -> int:
        """
        Insert a new user and return the auto‑generated id.

        Args:
            username:      Unique login name.
            password_hash: bcrypt‑hashed password string.
            role:          ``'admin'`` or ``'librarian'``.

        Returns:
            The new user's primary‑key id.
        """
        query = """
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
        """
        return db.execute_query(query, (username, password_hash, role))

    # ── Read ────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(user_id: int) -> dict | None:
        """Return a single user dict or ``None``."""
        query = "SELECT * FROM users WHERE id = %s"
        return db.execute_read_one(query, (user_id,))

    @staticmethod
    def get_by_username(username: str) -> dict | None:
        """Look up a user by their unique username."""
        query = "SELECT * FROM users WHERE username = %s"
        return db.execute_read_one(query, (username,))

    @staticmethod
    def get_all() -> list[dict]:
        """Return every user row as a list of dicts."""
        return db.execute_read("SELECT * FROM users ORDER BY id")

    # ── Update ──────────────────────────────────────────────────────────

    @staticmethod
    def update(user_id: int, **fields) -> None:
        """
        Update one or more columns for the given user.

        Args:
            user_id: Primary key.
            **fields: Column‑name / value pairs to update
                      (e.g. ``username="new_name"``).
        """
        if not fields:
            return
        set_clause = ", ".join(f"{key} = %s" for key in fields)
        values = tuple(fields.values()) + (user_id,)
        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        db.execute_query(query, values)

    # ── Delete ──────────────────────────────────────────────────────────

    @staticmethod
    def delete(user_id: int) -> None:
        """Remove a user by primary key."""
        db.execute_query("DELETE FROM users WHERE id = %s", (user_id,))
