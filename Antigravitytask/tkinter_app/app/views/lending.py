"""
Book lending view.

Allows librarians to lend books to members by selecting a member
and an available book, then creating a lending record.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.services.book_service import BookService
from app.services.lending_service import LendingService
from app.services.member_service import MemberService
from app.utils.style import COLORS, FONTS, create_card_frame, create_styled_button


class LendingView(ttk.Frame):
    """Book lending UI panel."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self._load_data()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build the lending layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header
        ttk.Label(self, text="📤  Lend a Book",
                  style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 15))

        # ── Lending Form ──
        form_card = create_card_frame(self)
        form_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        form_card.columnconfigure(1, weight=1)
        form_card.columnconfigure(3, weight=1)

        ttk.Label(form_card, text="New Lending", style="Card.TLabel",
                  font=FONTS["subheading"]).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        # Member selection
        ttk.Label(form_card, text="Member:", style="Card.TLabel",
                  font=FONTS["body_bold"]).grid(
            row=1, column=0, sticky="w", padx=(0, 5), pady=4)
        self._member_combo = ttk.Combobox(
            form_card, width=35, font=FONTS["entry"], state="readonly")
        self._member_combo.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=4)

        # Book selection
        ttk.Label(form_card, text="Book:", style="Card.TLabel",
                  font=FONTS["body_bold"]).grid(
            row=1, column=2, sticky="w", padx=(0, 5), pady=4)
        self._book_combo = ttk.Combobox(
            form_card, width=35, font=FONTS["entry"], state="readonly")
        self._book_combo.grid(row=1, column=3, sticky="ew", padx=(0, 15), pady=4)

        # Lend button
        btn_frame = ttk.Frame(form_card, style="Card.TFrame")
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="e", pady=(10, 0))

        create_styled_button(
            btn_frame, text="📤 Lend Book", command=self._lend_book,
            style_name="Success.TButton",
        ).pack(side="left", padx=4)

        create_styled_button(
            btn_frame, text="🔄 Refresh Lists", command=self._load_data,
        ).pack(side="left", padx=4)

        # ── Active Lendings Table ──
        ttk.Label(self, text="Active Lendings",
                  style="Subheading.TLabel").grid(
            row=1, column=0, sticky="sw", pady=(40, 5))

        table_frame = ttk.Frame(self, style="TFrame")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "book", "member", "lend_date", "due_date", "status")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse",
        )

        col_widths = {"id": 50, "book": 220, "member": 160,
                      "lend_date": 120, "due_date": 120, "status": 100}
        for col in columns:
            self._tree.heading(col, text=col.replace("_", " ").title())
            self._tree.column(col, width=col_widths.get(col, 100), anchor="center")
        self._tree.column("book", anchor="w")
        self._tree.column("member", anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    # ── Data operations ─────────────────────────────────────────────────

    def _load_data(self):
        """Refresh member/book combo boxes and active lendings table."""
        self._load_combos()
        self._load_active_lendings()

    def _load_combos(self):
        """Populate the member and book dropdowns."""
        try:
            members = MemberService.get_all_members()
            self._members_map = {
                f"{m['id']} — {m['name']}": m["id"] for m in members
            }
            self._member_combo["values"] = list(self._members_map.keys())

            books = BookService.get_all_books()
            self._books_map = {
                f"{b['id']} — {b['title']} (Avail: {b['available']})": b["id"]
                for b in books if b["available"] > 0
            }
            self._book_combo["values"] = list(self._books_map.keys())
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load data: {exc}")

    def _load_active_lendings(self):
        """Fetch and display active lendings."""
        self._tree.delete(*self._tree.get_children())
        try:
            lendings = LendingService.get_active_lendings()
            for lending in lendings:
                self._tree.insert("", "end", values=(
                    lending["id"],
                    lending["book_title"],
                    lending["member_name"],
                    str(lending["lend_date"]),
                    str(lending["due_date"]),
                    lending["status"].title(),
                ))
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load lendings: {exc}")

    def _lend_book(self):
        """Process a book lending."""
        member_key = self._member_combo.get()
        book_key = self._book_combo.get()

        if not member_key:
            messagebox.showwarning("Missing", "Please select a member.")
            return
        if not book_key:
            messagebox.showwarning("Missing", "Please select a book.")
            return

        member_id = self._members_map[member_key]
        book_id = self._books_map[book_key]

        try:
            LendingService.lend_book(book_id, member_id)
            messagebox.showinfo("Success", "Book lent successfully!")
            self._load_data()
        except ValueError as ve:
            messagebox.showwarning("Cannot Lend", str(ve))
        except Exception as exc:
            messagebox.showerror("Error", f"Lending failed: {exc}")

    def refresh(self):
        """Reload all data."""
        self._load_data()
