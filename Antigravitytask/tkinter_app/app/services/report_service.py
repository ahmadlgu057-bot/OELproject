"""
Reporting service.

Generates inventory summaries, borrowing statistics, overdue lists,
and member activity reports for the Inventory Reports UI.
"""

from app.models.book import BookModel
from app.models.lending import LendingModel
from app.models.member import MemberModel
from app.utils.database import db


class ReportService:
    """Business logic for generating library reports."""

    @staticmethod
    def get_inventory_summary() -> dict:
        """
        Return an overview of the library's inventory.

        Returns:
            Dict with ``total_books``, ``total_copies``, ``available_copies``,
            ``lent_copies``, ``total_members``, and ``active_lendings``.
        """
        books = BookModel.get_all()
        total_books = len(books)
        total_copies = sum(b["quantity"] for b in books)
        available_copies = sum(b["available"] for b in books)
        lent_copies = total_copies - available_copies

        members = MemberModel.get_all()
        active_lendings = LendingModel.get_active_lendings()

        return {
            "total_books": total_books,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "lent_copies": lent_copies,
            "total_members": len(members),
            "active_lendings": len(active_lendings),
        }

    @staticmethod
    def get_most_borrowed_books(limit: int = 10) -> list[dict]:
        """
        Return the most frequently borrowed books.

        Args:
            limit: Maximum number of results.

        Returns:
            List of dicts with ``title``, ``author``, and ``borrow_count``.
        """
        query = """
            SELECT b.title, b.author, COUNT(l.id) AS borrow_count
            FROM lendings l
            JOIN books b ON l.book_id = b.id
            GROUP BY l.book_id, b.title, b.author
            ORDER BY borrow_count DESC
            LIMIT %s
        """
        return db.execute_read(query, (limit,))

    @staticmethod
    def get_overdue_books() -> list[dict]:
        """Return all currently overdue lendings with book and member info."""
        return LendingModel.get_overdue()

    @staticmethod
    def get_member_activity(member_id: int) -> dict:
        """
        Summarise a member's borrowing activity.

        Args:
            member_id: The member's primary key.

        Returns:
            Dict with ``member_info``, ``total_borrows``, ``active_borrows``,
            and ``lending_history``.
        """
        member = MemberModel.get_by_id(member_id)
        all_lendings = LendingModel.get_by_member(member_id)
        active = LendingModel.get_active_by_member(member_id)

        return {
            "member_info": member,
            "total_borrows": len(all_lendings),
            "active_borrows": len(active),
            "lending_history": all_lendings,
        }

    @staticmethod
    def get_genre_distribution() -> list[dict]:
        """
        Return book counts grouped by genre.

        Returns:
            List of dicts with ``genre`` and ``count``.
        """
        query = """
            SELECT COALESCE(genre, 'Uncategorized') AS genre,
                   COUNT(*) AS count
            FROM books
            GROUP BY genre
            ORDER BY count DESC
        """
        return db.execute_read(query)
