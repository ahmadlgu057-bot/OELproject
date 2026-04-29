"""Unit tests for LendingModel (mocked DB)."""

import unittest
from unittest.mock import patch

from app.models.lending import LendingModel


class TestLendingModel(unittest.TestCase):

    @patch("app.models.lending.db")
    def test_create(self, mock_db):
        mock_db.execute_query.return_value = 1
        lid = LendingModel.create(1, 1, "2025-06-01")
        self.assertEqual(lid, 1)

    @patch("app.models.lending.db")
    def test_get_by_id(self, mock_db):
        mock_db.execute_read_one.return_value = {"id": 1}
        self.assertIsNotNone(LendingModel.get_by_id(1))

    @patch("app.models.lending.db")
    def test_get_active_lendings(self, mock_db):
        mock_db.execute_read.return_value = [{"id": 1}]
        self.assertEqual(len(LendingModel.get_active_lendings()), 1)

    @patch("app.models.lending.db")
    def test_get_overdue(self, mock_db):
        mock_db.execute_read.return_value = []
        self.assertEqual(len(LendingModel.get_overdue()), 0)

    @patch("app.models.lending.db")
    def test_mark_returned(self, mock_db):
        LendingModel.mark_returned(1, "2025-06-10", 5.0)
        mock_db.execute_query.assert_called_once()

    @patch("app.models.lending.db")
    def test_delete(self, mock_db):
        LendingModel.delete(1)
        mock_db.execute_query.assert_called_once()


if __name__ == "__main__":
    unittest.main()
