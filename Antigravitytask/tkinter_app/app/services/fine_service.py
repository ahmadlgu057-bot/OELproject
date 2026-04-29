"""
Fine calculation service.

Computes overdue fines based on the configured daily rate and provides
aggregate fine queries for members and the entire library.
"""

from datetime import date

from app.config import FINE_PER_DAY
from app.models.lending import LendingModel


class FineService:
    """Business logic for fine calculation and queries."""

    @staticmethod
    def calculate_fine(lending_id: int) -> dict:
        """
        Calculate the fine for a specific lending record.

        Args:
            lending_id: Primary key of the lending.

        Returns:
            Dict with ``days_overdue``, ``fine_amount``, ``due_date``,
            ``status``, and lending details.

        Raises:
            ValueError: If the lending record is not found.
        """
        lending = LendingModel.get_by_id(lending_id)
        if lending is None:
            raise ValueError("Lending record not found.")

        # Already returned — use stored fine
        if lending["status"] == "returned":
            return {
                "lending_id": lending_id,
                "book_title": lending["book_title"],
                "member_name": lending["member_name"],
                "due_date": str(lending["due_date"]),
                "return_date": str(lending["return_date"]),
                "days_overdue": 0,
                "fine_amount": float(lending["fine_amount"]),
                "status": "returned",
            }

        # Still borrowed — compute live fine
        due_date = lending["due_date"]
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)

        days_overdue = max(0, (date.today() - due_date).days)
        fine_amount = days_overdue * FINE_PER_DAY

        return {
            "lending_id": lending_id,
            "book_title": lending["book_title"],
            "member_name": lending["member_name"],
            "due_date": str(lending["due_date"]),
            "return_date": None,
            "days_overdue": days_overdue,
            "fine_amount": fine_amount,
            "status": "overdue" if days_overdue > 0 else "borrowed",
        }

    @staticmethod
    def get_member_fines(member_id: int) -> list[dict]:
        """
        Get all fines (current and historical) for a member.

        Returns a list of dicts, each with fine details per lending.
        """
        lendings = LendingModel.get_by_member(member_id)
        fines = []

        for lending in lendings:
            due_date = lending["due_date"]
            if isinstance(due_date, str):
                due_date = date.fromisoformat(due_date)

            if lending["status"] == "returned":
                fine_amount = float(lending["fine_amount"])
                days_overdue = 0  # historical
            else:
                days_overdue = max(0, (date.today() - due_date).days)
                fine_amount = days_overdue * FINE_PER_DAY

            if fine_amount > 0:
                fines.append({
                    "lending_id": lending["id"],
                    "book_title": lending["book_title"],
                    "due_date": str(lending["due_date"]),
                    "return_date": str(lending.get("return_date", "")),
                    "days_overdue": days_overdue,
                    "fine_amount": fine_amount,
                    "status": lending["status"],
                })

        return fines

    @staticmethod
    def get_all_outstanding_fines() -> list[dict]:
        """
        Get all currently outstanding (unreturned + overdue) fines.

        Returns fines for books that are overdue and still not returned.
        """
        overdue_lendings = LendingModel.get_overdue()
        fines = []

        for lending in overdue_lendings:
            due_date = lending["due_date"]
            if isinstance(due_date, str):
                due_date = date.fromisoformat(due_date)

            days_overdue = max(0, (date.today() - due_date).days)
            fine_amount = days_overdue * FINE_PER_DAY

            fines.append({
                "lending_id": lending["id"],
                "book_title": lending["book_title"],
                "member_name": lending["member_name"],
                "due_date": str(lending["due_date"]),
                "days_overdue": days_overdue,
                "fine_amount": fine_amount,
            })

        return fines

    @staticmethod
    def get_total_fines_for_member(member_id: int) -> float:
        """Return the sum of all fines for a member."""
        fines = FineService.get_member_fines(member_id)
        return sum(f["fine_amount"] for f in fines)
