"""
Lending data model.

Provides CRUD operations for the ``lendings`` table, which tracks
book borrows, returns, due dates, and fines.
"""

from app.utils.database import db


class LendingModel:
    """Encapsulates all database operations for the *lendings* table."""

    # ── Create ──────────────────────────────────────────────────────────

    @staticmethod
    def create(book_id: int, member_id: int, due_date: str) -> int:
        """
        Record a new book lending.

        Args:
            book_id:   ID of the book being lent.
            member_id: ID of the borrowing member.
            due_date:  Expected return date (``YYYY-MM-DD``).

        Returns:
            The new lending record's primary‑key id.
        """
        query = """
            INSERT INTO lendings (book_id, member_id, due_date)
            VALUES (%s, %s, %s)
        """
        return db.execute_query(query, (book_id, member_id, due_date))

    # ── Read ────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(lending_id: int) -> dict | None:
        """Return a single lending record or ``None``."""
        query = """
            SELECT l.*, b.title AS book_title, m.name AS member_name
            FROM lendings l
            JOIN books b ON l.book_id = b.id
            JOIN members m ON l.member_id = m.id
            WHERE l.id = %s
        """
        return db.execute_read_one(query, (lending_id,))

    @staticmethod
    def get_active_lendings() -> list[dict]:
        """Return all currently‑borrowed (not yet returned) lendings."""
        query = """
            SELECT l.*, b.title AS book_title, m.name AS member_name
            FROM lendings l
            JOIN books b ON l.book_id = b.id
            JOIN members m ON l.member_id = m.id
            WHERE l.status = 'borrowed'
            ORDER BY l.due_date
        """
        return db.execute_read(query)

    @staticmethod
    def get_overdue() -> list[dict]:
        """Return lendings that are past their due date and not returned."""
        query = """
            SELECT l.*, b.title AS book_title, m.name AS member_name
            FROM lendings l
            JOIN books b ON l.book_id = b.id
            JOIN members m ON l.member_id = m.id
            WHERE l.status = 'borrowed' AND l.due_date < CURDATE()
            ORDER BY l.due_date
        """
        return db.execute_read(query)

    @staticmethod
    def get_by_member(member_id: int) -> list[dict]:
        """Return all lendings for a specific member."""
        query = """
            SELECT l.*, b.title AS book_title, m.name AS member_name
            FROM lendings l
            JOIN books b ON l.book_id = b.id
            JOIN members m ON l.member_id = m.id
            WHERE l.member_id = %s
            ORDER BY l.lend_date DESC
        """
        return db.execute_read(query, (member_id,))

    @staticmethod
    def get_active_by_member(member_id: int) -> list[dict]:
        """Return active (unreturned) lendings for a member."""
        query = """
            SELECT l.*, b.title AS book_title, m.name AS member_name
            FROM lendings l
            JOIN books b ON l.book_id = b.id
            JOIN members m ON l.member_id = m.id
            WHERE l.member_id = %s AND l.status = 'borrowed'
            ORDER BY l.due_date
        """
        return db.execute_read(query, (member_id,))

    @staticmethod
    def get_active_for_book(book_id: int) -> list[dict]:
        """Return active lendings for a specific book."""
        query = """
            SELECT l.* FROM lendings l
            WHERE l.book_id = %s AND l.status = 'borrowed'
        """
        return db.execute_read(query, (book_id,))

    @staticmethod
    def get_all() -> list[dict]:
        """Return all lendings with book and member info."""
        query = """
            SELECT l.*, b.title AS book_title, m.name AS member_name
            FROM lendings l
            JOIN books b ON l.book_id = b.id
            JOIN members m ON l.member_id = m.id
            ORDER BY l.lend_date DESC
        """
        return db.execute_read(query)

    # ── Update ──────────────────────────────────────────────────────────

    @staticmethod
    def mark_returned(lending_id: int, return_date: str,
                      fine_amount: float = 0.0) -> None:
        """
        Mark a lending as returned.

        Args:
            lending_id:  Primary key of the lending.
            return_date: Actual return date (``YYYY-MM-DD``).
            fine_amount: Calculated overdue fine.
        """
        query = """
            UPDATE lendings
            SET return_date = %s, fine_amount = %s, status = 'returned'
            WHERE id = %s
        """
        db.execute_query(query, (return_date, fine_amount, lending_id))

    @staticmethod
    def update_status(lending_id: int, status: str) -> None:
        """Update just the status column."""
        db.execute_query(
            "UPDATE lendings SET status = %s WHERE id = %s",
            (status, lending_id),
        )

    # ── Delete ──────────────────────────────────────────────────────────

    @staticmethod
    def delete(lending_id: int) -> None:
        """Remove a lending record by primary key."""
        db.execute_query("DELETE FROM lendings WHERE id = %s", (lending_id,))
