"""
Unit tests for BookService.

Tests add, update, remove, and search operations with mocked models.
"""

import unittest
from unittest.mock import patch

from app.services.book_service import BookService


class TestBookService(unittest.TestCase):
    """Test suite for BookService."""

    # ── Add book ────────────────────────────────────────────────────────

    @patch("app.services.book_service.BookModel")
    def test_add_book_success(self, mock_model):
        """add_book should create a book and return its id."""
        mock_model.create.return_value = 10
        book_id = BookService.add_book("Python 101", "John", "978-0-13-468599-1", "Tech", 3)
        self.assertEqual(book_id, 10)
        mock_model.create.assert_called_once()

    def test_add_book_missing_title(self):
        """add_book should raise ValueError when title is empty."""
        with self.assertRaises(ValueError) as ctx:
            BookService.add_book("", "Author")
        self.assertIn("Title", str(ctx.exception))

    def test_add_book_missing_author(self):
        """add_book should raise ValueError when author is empty."""
        with self.assertRaises(ValueError) as ctx:
            BookService.add_book("Title", "")
        self.assertIn("Author", str(ctx.exception))

    def test_add_book_invalid_isbn(self):
        """add_book should reject invalid ISBN formats."""
        with self.assertRaises(ValueError) as ctx:
            BookService.add_book("Title", "Author", isbn="123")
        self.assertIn("ISBN", str(ctx.exception))

    def test_add_book_zero_quantity(self):
        """add_book should reject quantity less than 1."""
        with self.assertRaises(ValueError) as ctx:
            BookService.add_book("Title", "Author", quantity=0)
        self.assertIn("Quantity", str(ctx.exception))

    # ── Update book ─────────────────────────────────────────────────────

    @patch("app.services.book_service.BookModel")
    def test_update_book_success(self, mock_model):
        """update_book should call model update when book exists."""
        mock_model.get_by_id.return_value = {"id": 1, "title": "Old"}
        BookService.update_book(1, title="New Title")
        mock_model.update.assert_called_once_with(1, title="New Title")

    @patch("app.services.book_service.BookModel")
    def test_update_book_not_found(self, mock_model):
        """update_book should raise ValueError for nonexistent book."""
        mock_model.get_by_id.return_value = None
        with self.assertRaises(ValueError):
            BookService.update_book(999, title="X")

    # ── Remove book ─────────────────────────────────────────────────────

    @patch("app.services.book_service.LendingModel")
    @patch("app.services.book_service.BookModel")
    def test_remove_book_success(self, mock_book, mock_lending):
        """remove_book should delete when no active lendings."""
        mock_book.get_by_id.return_value = {"id": 1}
        mock_lending.get_active_for_book.return_value = []
        BookService.remove_book(1)
        mock_book.delete.assert_called_once_with(1)

    @patch("app.services.book_service.LendingModel")
    @patch("app.services.book_service.BookModel")
    def test_remove_book_with_active_lending(self, mock_book, mock_lending):
        """remove_book should block deletion if copies are lent out."""
        mock_book.get_by_id.return_value = {"id": 1}
        mock_lending.get_active_for_book.return_value = [{"id": 10}]
        with self.assertRaises(ValueError) as ctx:
            BookService.remove_book(1)
        self.assertIn("active lending", str(ctx.exception))

    # ── Search ──────────────────────────────────────────────────────────

    @patch("app.services.book_service.BookModel")
    def test_search_books_with_keyword(self, mock_model):
        """search_books should call model.search for non‑empty query."""
        mock_model.search.return_value = [{"id": 1, "title": "Python"}]
        results = BookService.search_books("Python")
        self.assertEqual(len(results), 1)
        mock_model.search.assert_called_once_with("Python")

    @patch("app.services.book_service.BookModel")
    def test_search_books_empty_returns_all(self, mock_model):
        """search_books with empty string should return all books."""
        mock_model.get_all.return_value = [{"id": 1}, {"id": 2}]
        results = BookService.search_books("")
        self.assertEqual(len(results), 2)
        mock_model.get_all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
