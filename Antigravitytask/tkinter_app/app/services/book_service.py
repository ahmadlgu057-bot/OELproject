"""
Book management service.

Validates inputs and orchestrates CRUD operations on the books inventory,
enforcing business rules such as preventing deletion of actively‑lent books.
"""

from app.models.book import BookModel
from app.models.lending import LendingModel
from app.utils.validators import validate_isbn, validate_required_fields


class BookService:
    """Business logic for managing the book catalogue."""

    @staticmethod
    def add_book(title: str, author: str, isbn: str = "",
                 genre: str = "", quantity: int = 1) -> int:
        """
        Add a new book to the library after validation.

        Args:
            title:    Book title.
            author:   Author name.
            isbn:     ISBN string (optional).
            genre:    Genre/category.
            quantity: Number of copies.

        Returns:
            The new book's id.

        Raises:
            ValueError: On missing required fields or invalid ISBN.
        """
        missing = validate_required_fields({"Title": title, "Author": author})
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        if isbn and not validate_isbn(isbn):
            raise ValueError("Invalid ISBN format. Use ISBN-10 or ISBN-13.")

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        return BookModel.create(title, author, isbn, genre, quantity)

    @staticmethod
    def update_book(book_id: int, **fields) -> None:
        """
        Update book details.

        Args:
            book_id:  Primary key of the book.
            **fields: Columns to update.

        Raises:
            ValueError: If the book does not exist.
        """
        book = BookModel.get_by_id(book_id)
        if book is None:
            raise ValueError("Book not found.")

        if "isbn" in fields and fields["isbn"]:
            if not validate_isbn(fields["isbn"]):
                raise ValueError("Invalid ISBN format.")

        BookModel.update(book_id, **fields)

    @staticmethod
    def remove_book(book_id: int) -> None:
        """
        Delete a book, blocking removal if copies are currently lent out.

        Args:
            book_id: Primary key of the book.

        Raises:
            ValueError: If the book has active lendings or does not exist.
        """
        book = BookModel.get_by_id(book_id)
        if book is None:
            raise ValueError("Book not found.")

        active_lendings = LendingModel.get_active_for_book(book_id)
        if active_lendings:
            raise ValueError(
                "Cannot delete: this book has active lending records. "
                "All copies must be returned first."
            )

        BookModel.delete(book_id)

    @staticmethod
    def search_books(keyword: str) -> list[dict]:
        """Search books by title, author, or ISBN."""
        if not keyword.strip():
            return BookModel.get_all()
        return BookModel.search(keyword)

    @staticmethod
    def get_all_books() -> list[dict]:
        """Return every book in the catalogue."""
        return BookModel.get_all()

    @staticmethod
    def get_book(book_id: int) -> dict | None:
        """Return a single book by id."""
        return BookModel.get_by_id(book_id)
