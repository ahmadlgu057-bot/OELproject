"""
Member data model.

Provides CRUD operations for the ``members`` table, which stores
library patron information including contact details and membership status.
"""

from app.utils.database import db


class MemberModel:
    """Encapsulates all database operations for the *members* table."""

    # ── Create ──────────────────────────────────────────────────────────

    @staticmethod
    def create(name: str, email: str, phone: str = "",
               address: str = "") -> int:
        """
        Insert a new member and return the auto‑generated id.

        Args:
            name:    Full name.
            email:   Unique email address.
            phone:   Contact phone number.
            address: Postal address.

        Returns:
            The new member's primary‑key id.
        """
        query = """
            INSERT INTO members (name, email, phone, address)
            VALUES (%s, %s, %s, %s)
        """
        return db.execute_query(query, (name, email, phone, address))

    # ── Read ────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(member_id: int) -> dict | None:
        """Return a single member dict or ``None``."""
        return db.execute_read_one(
            "SELECT * FROM members WHERE id = %s", (member_id,)
        )

    @staticmethod
    def get_all() -> list[dict]:
        """Return all active members ordered by name."""
        return db.execute_read(
            "SELECT * FROM members WHERE is_active = TRUE ORDER BY name"
        )

    @staticmethod
    def get_all_including_inactive() -> list[dict]:
        """Return every member regardless of active status."""
        return db.execute_read("SELECT * FROM members ORDER BY name")

    @staticmethod
    def search(keyword: str) -> list[dict]:
        """
        Search members by name, email, or phone.

        Args:
            keyword: Partial match term.

        Returns:
            Matching member rows.
        """
        like = f"%{keyword}%"
        query = """
            SELECT * FROM members
            WHERE (name LIKE %s OR email LIKE %s OR phone LIKE %s)
              AND is_active = TRUE
            ORDER BY name
        """
        return db.execute_read(query, (like, like, like))

    # ── Update ──────────────────────────────────────────────────────────

    @staticmethod
    def update(member_id: int, **fields) -> None:
        """
        Update one or more columns for a member.

        Args:
            member_id: Primary key.
            **fields:  Column / value pairs to update.
        """
        if not fields:
            return
        set_clause = ", ".join(f"{key} = %s" for key in fields)
        values = tuple(fields.values()) + (member_id,)
        query = f"UPDATE members SET {set_clause} WHERE id = %s"
        db.execute_query(query, values)

    # ── Delete / Deactivate ─────────────────────────────────────────────

    @staticmethod
    def deactivate(member_id: int) -> None:
        """Soft‑delete a member by setting ``is_active`` to ``FALSE``."""
        db.execute_query(
            "UPDATE members SET is_active = FALSE WHERE id = %s",
            (member_id,),
        )

    @staticmethod
    def delete(member_id: int) -> None:
        """Hard‑delete a member row (use with caution)."""
        db.execute_query("DELETE FROM members WHERE id = %s", (member_id,))
