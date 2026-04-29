"""
Books management view.

Provides a full CRUD interface for the book catalogue: add, search,
edit, and delete books displayed in a sortable Treeview table.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.services.book_service import BookService
from app.utils.style import COLORS, FONTS, create_card_frame, create_styled_button


class BooksView(ttk.Frame):
    """Add / Remove / Edit / Search books UI panel."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self._load_books()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build the books management layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header
        header = ttk.Frame(self, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="📖  Book Management",
                  style="Heading.TLabel").grid(row=0, column=0, sticky="w")

        # ── Add Book Form ──
        form_card = create_card_frame(self)
        form_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        form_card.columnconfigure((1, 3, 5), weight=1)

        ttk.Label(form_card, text="Add New Book", style="Card.TLabel",
                  font=FONTS["subheading"]).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 12))

        # Row 1: Title, Author, ISBN
        fields_row1 = [("Title:", "title"), ("Author:", "author"), ("ISBN:", "isbn")]
        self._entries = {}
        for idx, (label, key) in enumerate(fields_row1):
            col = idx * 2
            ttk.Label(form_card, text=label, style="Card.TLabel",
                      font=FONTS["body_bold"]).grid(
                row=1, column=col, sticky="w", padx=(0, 5), pady=4)
            entry = ttk.Entry(form_card, width=20, font=FONTS["entry"])
            entry.grid(row=1, column=col + 1, sticky="ew", padx=(0, 15), pady=4)
            self._entries[key] = entry

        # Row 2: Genre, Quantity, Add button
        ttk.Label(form_card, text="Genre:", style="Card.TLabel",
                  font=FONTS["body_bold"]).grid(
            row=2, column=0, sticky="w", padx=(0, 5), pady=4)
        self._entries["genre"] = ttk.Entry(form_card, width=20, font=FONTS["entry"])
        self._entries["genre"].grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=4)

        ttk.Label(form_card, text="Qty:", style="Card.TLabel",
                  font=FONTS["body_bold"]).grid(
            row=2, column=2, sticky="w", padx=(0, 5), pady=4)
        self._entries["quantity"] = ttk.Entry(form_card, width=8, font=FONTS["entry"])
        self._entries["quantity"].grid(row=2, column=3, sticky="w", padx=(0, 15), pady=4)
        self._entries["quantity"].insert(0, "1")

        btn_frame = ttk.Frame(form_card, style="Card.TFrame")
        btn_frame.grid(row=2, column=4, columnspan=2, sticky="e", pady=4)

        create_styled_button(
            btn_frame, text="➕ Add Book", command=self._add_book,
            style_name="Success.TButton",
        ).pack(side="left", padx=4)

        create_styled_button(
            btn_frame, text="🔄 Clear", command=self._clear_form,
        ).pack(side="left", padx=4)

        # ── Search Bar ──
        search_frame = ttk.Frame(self, style="TFrame")
        search_frame.grid(row=1, column=0, sticky="ne", pady=5, padx=5)

        # Actually place search above the table
        search_bar = ttk.Frame(self, style="TFrame")
        search_bar.grid(row=1, column=0, sticky="se", pady=(0, 5))

        ttk.Label(search_bar, text="🔍", font=("Segoe UI Emoji", 14)).pack(
            side="left", padx=(0, 5))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._search_books())
        search_entry = ttk.Entry(search_bar, textvariable=self._search_var,
                                  width=30, font=FONTS["entry"])
        search_entry.pack(side="left")

        # ── Books Table ──
        table_frame = ttk.Frame(self, style="TFrame")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "title", "author", "isbn", "genre", "quantity", "available")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse",
        )

        col_widths = {"id": 50, "title": 220, "author": 160, "isbn": 130,
                      "genre": 100, "quantity": 70, "available": 80}
        for col in columns:
            self._tree.heading(col, text=col.replace("_", " ").title())
            self._tree.column(col, width=col_widths.get(col, 100), anchor="center")

        self._tree.column("title", anchor="w")
        self._tree.column("author", anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Action buttons below table
        action_frame = ttk.Frame(self, style="TFrame")
        action_frame.grid(row=3, column=0, sticky="e", pady=(10, 0))

        create_styled_button(
            action_frame, text="✏️ Edit Selected", command=self._edit_book,
        ).pack(side="left", padx=4)

        create_styled_button(
            action_frame, text="🗑️ Delete Selected", command=self._delete_book,
            style_name="Danger.TButton",
        ).pack(side="left", padx=4)

        create_styled_button(
            action_frame, text="🔄 Refresh", command=self._load_books,
        ).pack(side="left", padx=4)

    # ── Data operations ─────────────────────────────────────────────────

    def _load_books(self):
        """Fetch all books and populate the table."""
        self._tree.delete(*self._tree.get_children())
        try:
            books = BookService.get_all_books()
            for book in books:
                self._tree.insert("", "end", values=(
                    book["id"], book["title"], book["author"],
                    book.get("isbn", ""), book.get("genre", ""),
                    book["quantity"], book["available"],
                ))
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load books: {exc}")

    def _search_books(self):
        """Filter table based on search input."""
        keyword = self._search_var.get().strip()
        self._tree.delete(*self._tree.get_children())
        try:
            books = BookService.search_books(keyword)
            for book in books:
                self._tree.insert("", "end", values=(
                    book["id"], book["title"], book["author"],
                    book.get("isbn", ""), book.get("genre", ""),
                    book["quantity"], book["available"],
                ))
        except Exception as exc:
            messagebox.showerror("Error", f"Search failed: {exc}")

    def _add_book(self):
        """Add a new book from form inputs."""
        try:
            title = self._entries["title"].get().strip()
            author = self._entries["author"].get().strip()
            isbn = self._entries["isbn"].get().strip()
            genre = self._entries["genre"].get().strip()
            qty_str = self._entries["quantity"].get().strip()
            quantity = int(qty_str) if qty_str else 1

            BookService.add_book(title, author, isbn, genre, quantity)
            messagebox.showinfo("Success", f"Book '{title}' added successfully!")
            self._clear_form()
            self._load_books()
        except ValueError as ve:
            messagebox.showwarning("Validation Error", str(ve))
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to add book: {exc}")

    def _edit_book(self):
        """Open an edit dialog for the selected book."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book to edit.")
            return

        values = self._tree.item(selected[0], "values")
        book_id = int(values[0])
        self._open_edit_dialog(book_id, values)

    def _open_edit_dialog(self, book_id: int, current_values):
        """Show a top‑level edit window for the book."""
        dialog = tk.Toplevel(self)
        dialog.title("Edit Book")
        dialog.geometry("450x350")
        dialog.configure(bg=COLORS["bg_dark"])
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Edit Book", style="Subheading.TLabel").pack(
            pady=(15, 10))

        form = ttk.Frame(dialog, style="TFrame")
        form.pack(padx=30, fill="x")

        labels = ["Title", "Author", "ISBN", "Genre", "Quantity"]
        entries = {}
        for idx, label in enumerate(labels):
            ttk.Label(form, text=f"{label}:").grid(
                row=idx, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=30, font=FONTS["entry"])
            entry.grid(row=idx, column=1, sticky="ew", pady=5, padx=(10, 0))
            entry.insert(0, current_values[idx + 1])
            entries[label.lower()] = entry
        form.columnconfigure(1, weight=1)

        def save():
            try:
                fields = {
                    "title": entries["title"].get().strip(),
                    "author": entries["author"].get().strip(),
                    "isbn": entries["isbn"].get().strip(),
                    "genre": entries["genre"].get().strip(),
                    "quantity": int(entries["quantity"].get().strip() or 1),
                }
                BookService.update_book(book_id, **fields)
                messagebox.showinfo("Success", "Book updated successfully!")
                dialog.destroy()
                self._load_books()
            except ValueError as ve:
                messagebox.showwarning("Validation Error", str(ve))
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        btn_frame = ttk.Frame(dialog, style="TFrame")
        btn_frame.pack(pady=15)
        create_styled_button(btn_frame, text="💾 Save", command=save,
                              style_name="Success.TButton").pack(side="left", padx=5)
        create_styled_button(btn_frame, text="Cancel",
                              command=dialog.destroy).pack(side="left", padx=5)

    def _delete_book(self):
        """Delete the selected book after confirmation."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book to delete.")
            return

        values = self._tree.item(selected[0], "values")
        book_id = int(values[0])
        title = values[1]

        if not messagebox.askyesno("Confirm Delete",
                                    f"Delete '{title}'? This cannot be undone."):
            return

        try:
            BookService.remove_book(book_id)
            messagebox.showinfo("Deleted", f"Book '{title}' has been removed.")
            self._load_books()
        except ValueError as ve:
            messagebox.showwarning("Cannot Delete", str(ve))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _clear_form(self):
        """Clear all form entry fields."""
        for key, entry in self._entries.items():
            entry.delete(0, tk.END)
        self._entries["quantity"].insert(0, "1")

    def refresh(self):
        """Reload the book table data."""
        self._load_books()
