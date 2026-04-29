"""
Unit tests for LendingService.

Tests lending, returning, fine calculation, and error conditions.
"""

import unittest
from datetime import date, timedelta
from unittest.mock import patch

from app.config import FINE_PER_DAY
from app.services.lending_service import LendingService


class TestLendingService(unittest.TestCase):
    """Test suite for LendingService."""

    @patch("app.services.lending_service.BookModel")
    @patch("app.services.lending_service.MemberModel")
    @patch("app.services.lending_service.LendingModel")
    def test_lend_book_success(self, mock_lending, mock_member, mock_book):
        mock_book.get_by_id.return_value = {"id": 1, "title": "T", "available": 3}
        mock_member.get_by_id.return_value = {"id": 1, "name": "A", "is_active": True}
        mock_lending.create.return_value = 100
        self.assertEqual(LendingService.lend_book(1, 1), 100)
        mock_book.decrement_available.assert_called_once_with(1)

    @patch("app.services.lending_service.BookModel")
    def test_lend_book_not_found(self, mock_book):
        mock_book.get_by_id.return_value = None
        with self.assertRaises(ValueError):
            LendingService.lend_book(999, 1)

    @patch("app.services.lending_service.BookModel")
    @patch("app.services.lending_service.MemberModel")
    def test_lend_no_copies(self, mock_member, mock_book):
        mock_book.get_by_id.return_value = {"id": 1, "title": "B", "available": 0}
        mock_member.get_by_id.return_value = {"id": 1, "name": "X", "is_active": True}
        with self.assertRaises(ValueError):
            LendingService.lend_book(1, 1)

    @patch("app.services.lending_service.BookModel")
    @patch("app.services.lending_service.LendingModel")
    def test_return_on_time(self, mock_lending, mock_book):
        future = (date.today() + timedelta(days=5)).isoformat()
        mock_lending.get_by_id.return_value = {
            "id": 1, "book_id": 10, "due_date": future,
            "status": "borrowed", "book_title": "T", "member_name": "A",
        }
        result = LendingService.return_book(1)
        self.assertEqual(result["fine_amount"], 0)

    @patch("app.services.lending_service.BookModel")
    @patch("app.services.lending_service.LendingModel")
    def test_return_overdue(self, mock_lending, mock_book):
        past = (date.today() - timedelta(days=5)).isoformat()
        mock_lending.get_by_id.return_value = {
            "id": 1, "book_id": 10, "due_date": past,
            "status": "borrowed", "book_title": "T", "member_name": "A",
        }
        result = LendingService.return_book(1)
        self.assertEqual(result["fine_amount"], 5 * FINE_PER_DAY)

    @patch("app.services.lending_service.LendingModel")
    def test_return_already_returned(self, mock_lending):
        mock_lending.get_by_id.return_value = {
            "id": 1, "status": "returned", "book_title": "X", "member_name": "Y",
        }
        with self.assertRaises(ValueError):
            LendingService.return_book(1)


if __name__ == "__main__":
    unittest.main()
