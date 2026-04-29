"""
Book data model.

Provides CRUD operations for the ``books`` table, which stores
library inventory including title, author, ISBN, genre, and stock levels.
"""

from app.utils.database import db


class BookModel:
    """Encapsulates all database operations for the *books* table."""

    # ── Create ──────────────────────────────────────────────────────────

    @staticmethod
    def create(title: str, author: str, isbn: str = "",
               genre: str = "", quantity: int = 1) -> int:
        """
        Insert a new book and return its auto‑generated id.

        Args:
            title:    Book title.
            author:   Author name.
            isbn:     ISBN‑10 or ISBN‑13 (optional).
            genre:    Genre/category label.
            quantity: Total copies in stock.

        Returns:
            The new book's primary‑key id.
        """
        query = """
            INSERT INTO books (title, author, isbn, genre, quantity, available)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(
            query, (title, author, isbn, genre, quantity, quantity)
        )

    # ── Read ────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(book_id: int) -> dict | None:
        """Return a single book dict or ``None``."""
        return db.execute_read_one(
            "SELECT * FROM books WHERE id = %s", (book_id,)
        )

    @staticmethod
    def get_all() -> list[dict]:
        """Return every book row ordered by title."""
        return db.execute_read("SELECT * FROM books ORDER BY title")

    @staticmethod
    def search(keyword: str) -> list[dict]:
        """
        Search books by title, author, or ISBN containing *keyword*.

        Args:
            keyword: The search term (case‑insensitive partial match).

        Returns:
            Matching book rows.
        """
        like = f"%{keyword}%"
        query = """
            SELECT * FROM books
            WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s
            ORDER BY title
        """
        return db.execute_read(query, (like, like, like))

    # ── Update ──────────────────────────────────────────────────────────

    @staticmethod
    def update(book_id: int, **fields) -> None:
        """
        Update one or more columns for a book.

        Args:
            book_id: Primary key.
            **fields: Column / value pairs to update.
        """
        if not fields:
            return
        set_clause = ", ".join(f"{key} = %s" for key in fields)
        values = tuple(fields.values()) + (book_id,)
        query = f"UPDATE books SET {set_clause} WHERE id = %s"
        db.execute_query(query, values)

    # ── Delete ──────────────────────────────────────────────────────────

    @staticmethod
    def delete(book_id: int) -> None:
        """Remove a book by primary key."""
        db.execute_query("DELETE FROM books WHERE id = %s", (book_id,))

    # ── Stock helpers ───────────────────────────────────────────────────

    @staticmethod
    def decrement_available(book_id: int) -> None:
        """Decrease the available count by one (used when lending)."""
        db.execute_query(
            "UPDATE books SET available = available - 1 WHERE id = %s AND available > 0",
            (book_id,),
        )

    @staticmethod
    def increment_available(book_id: int) -> None:
        """Increase the available count by one (used when returning)."""
        db.execute_query(
            "UPDATE books SET available = available + 1 WHERE id = %s",
            (book_id,),
        )
