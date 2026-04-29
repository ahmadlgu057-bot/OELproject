"""Unit tests for BookModel (mocked DB)."""

import unittest
from unittest.mock import patch

from app.models.book import BookModel


class TestBookModel(unittest.TestCase):

    @patch("app.models.book.db")
    def test_create(self, mock_db):
        mock_db.execute_query.return_value = 1
        bid = BookModel.create("Title", "Author", "1234567890", "Fiction", 2)
        self.assertEqual(bid, 1)

    @patch("app.models.book.db")
    def test_get_by_id(self, mock_db):
        mock_db.execute_read_one.return_value = {"id": 1, "title": "T"}
        self.assertIsNotNone(BookModel.get_by_id(1))

    @patch("app.models.book.db")
    def test_get_all(self, mock_db):
        mock_db.execute_read.return_value = [{"id": 1}]
        self.assertEqual(len(BookModel.get_all()), 1)

    @patch("app.models.book.db")
    def test_search(self, mock_db):
        mock_db.execute_read.return_value = [{"id": 1, "title": "Python"}]
        results = BookModel.search("Python")
        self.assertEqual(len(results), 1)

    @patch("app.models.book.db")
    def test_update(self, mock_db):
        BookModel.update(1, title="New")
        mock_db.execute_query.assert_called_once()

    @patch("app.models.book.db")
    def test_delete(self, mock_db):
        BookModel.delete(1)
        mock_db.execute_query.assert_called_once()

    @patch("app.models.book.db")
    def test_decrement_available(self, mock_db):
        BookModel.decrement_available(1)
        mock_db.execute_query.assert_called_once()

    @patch("app.models.book.db")
    def test_increment_available(self, mock_db):
        BookModel.increment_available(1)
        mock_db.execute_query.assert_called_once()


if __name__ == "__main__":
    unittest.main()
