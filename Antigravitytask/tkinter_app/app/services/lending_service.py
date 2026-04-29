"""
Lending service.

Manages the book lending and return workflow, including availability
checks, stock adjustments, and fine calculation on return.
"""

from datetime import date, timedelta

from app.config import FINE_PER_DAY, LENDING_PERIOD_DAYS
from app.models.book import BookModel
from app.models.lending import LendingModel
from app.models.member import MemberModel


class LendingService:
    """Business logic for lending and returning books."""

    @staticmethod
    def lend_book(book_id: int, member_id: int) -> int:
        """
        Lend a book to a member.

        Checks availability, decrements the available count, and creates
        a lending record with a due date based on ``LENDING_PERIOD_DAYS``.

        Args:
            book_id:   ID of the book to lend.
            member_id: ID of the borrowing member.

        Returns:
            The new lending record's id.

        Raises:
            ValueError: If book/member not found or no copies available.
        """
        book = BookModel.get_by_id(book_id)
        if book is None:
            raise ValueError("Book not found.")

        member = MemberModel.get_by_id(member_id)
        if member is None:
            raise ValueError("Member not found.")

        if not member.get("is_active", True):
            raise ValueError("Member account is inactive.")

        if book["available"] <= 0:
            raise ValueError(
                f"No copies of '{book['title']}' are currently available."
            )

        due_date = (date.today() + timedelta(days=LENDING_PERIOD_DAYS)).isoformat()

        lending_id = LendingModel.create(book_id, member_id, due_date)
        BookModel.decrement_available(book_id)

        return lending_id

    @staticmethod
    def return_book(lending_id: int) -> dict:
        """
        Process a book return.

        Marks the lending as returned, increments available stock, and
        calculates any overdue fine.

        Args:
            lending_id: Primary key of the lending record.

        Returns:
            A dict with ``fine_amount`` and ``days_overdue``.

        Raises:
            ValueError: If lending not found or already returned.
        """
        lending = LendingModel.get_by_id(lending_id)
        if lending is None:
            raise ValueError("Lending record not found.")

        if lending["status"] == "returned":
            raise ValueError("This book has already been returned.")

        return_date = date.today()
        due_date = lending["due_date"]

        # Ensure due_date is a date object for comparison
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)

        days_overdue = max(0, (return_date - due_date).days)
        fine_amount = days_overdue * FINE_PER_DAY

        LendingModel.mark_returned(
            lending_id, return_date.isoformat(), fine_amount
        )
        BookModel.increment_available(lending["book_id"])

        return {
            "fine_amount": fine_amount,
            "days_overdue": days_overdue,
            "return_date": return_date.isoformat(),
        }

    @staticmethod
    def get_active_lendings() -> list[dict]:
        """Return all currently active (unreturned) lendings."""
        return LendingModel.get_active_lendings()

    @staticmethod
    def get_overdue_lendings() -> list[dict]:
        """Return all overdue lendings."""
        return LendingModel.get_overdue()

    @staticmethod
    def get_member_lendings(member_id: int) -> list[dict]:
        """Return all lendings (active and historical) for a member."""
        return LendingModel.get_by_member(member_id)

    @staticmethod
    def get_active_member_lendings(member_id: int) -> list[dict]:
        """Return only active lendings for a member."""
        return LendingModel.get_active_by_member(member_id)
