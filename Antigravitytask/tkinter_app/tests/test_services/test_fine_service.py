"""Unit tests for FineService."""

import unittest
from datetime import date, timedelta
from unittest.mock import patch

from app.config import FINE_PER_DAY
from app.services.fine_service import FineService


class TestFineService(unittest.TestCase):

    @patch("app.services.fine_service.LendingModel")
    def test_calculate_fine_returned(self, mock_lending):
        mock_lending.get_by_id.return_value = {
            "id": 1, "status": "returned", "fine_amount": 5.0,
            "due_date": "2025-01-01", "return_date": "2025-01-06",
            "book_title": "T", "member_name": "A",
        }
        result = FineService.calculate_fine(1)
        self.assertEqual(result["fine_amount"], 5.0)
        self.assertEqual(result["status"], "returned")

    @patch("app.services.fine_service.LendingModel")
    def test_calculate_fine_overdue(self, mock_lending):
        past = (date.today() - timedelta(days=3)).isoformat()
        mock_lending.get_by_id.return_value = {
            "id": 1, "status": "borrowed", "fine_amount": 0,
            "due_date": past, "return_date": None,
            "book_title": "T", "member_name": "A",
        }
        result = FineService.calculate_fine(1)
        self.assertEqual(result["fine_amount"], 3 * FINE_PER_DAY)
        self.assertEqual(result["status"], "overdue")

    @patch("app.services.fine_service.LendingModel")
    def test_calculate_fine_not_overdue(self, mock_lending):
        future = (date.today() + timedelta(days=5)).isoformat()
        mock_lending.get_by_id.return_value = {
            "id": 1, "status": "borrowed", "fine_amount": 0,
            "due_date": future, "return_date": None,
            "book_title": "T", "member_name": "A",
        }
        result = FineService.calculate_fine(1)
        self.assertEqual(result["fine_amount"], 0)
        self.assertEqual(result["status"], "borrowed")

    @patch("app.services.fine_service.LendingModel")
    def test_calculate_fine_not_found(self, mock_lending):
        mock_lending.get_by_id.return_value = None
        with self.assertRaises(ValueError):
            FineService.calculate_fine(999)

    @patch("app.services.fine_service.LendingModel")
    def test_get_all_outstanding(self, mock_lending):
        past = (date.today() - timedelta(days=2)).isoformat()
        mock_lending.get_overdue.return_value = [
            {"id": 1, "due_date": past, "book_title": "T", "member_name": "A"},
        ]
        fines = FineService.get_all_outstanding_fines()
        self.assertEqual(len(fines), 1)
        self.assertEqual(fines[0]["fine_amount"], 2 * FINE_PER_DAY)


if __name__ == "__main__":
    unittest.main()
