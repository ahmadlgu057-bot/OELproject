"""
Inventory reports view.

Displays library metrics, most‑borrowed books, genre distribution,
and overdue book listings in an organised report layout.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.services.report_service import ReportService
from app.utils.style import COLORS, FONTS, create_card_frame, create_styled_button


class ReportsView(ttk.Frame):
    """Inventory reports UI panel."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build the reports layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # Header
        header = ttk.Frame(self, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="📊  Inventory Reports",
                  style="Heading.TLabel").pack(side="left")

        create_styled_button(
            header, text="🔄 Refresh", command=self._load_reports,
        ).pack(side="right")

        # ── Summary Cards ──
        cards_frame = ttk.Frame(self, style="TFrame")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self._card_labels = {}
        card_defs = [
            ("total_books",      "Total Books",      COLORS["accent"]),
            ("available_copies", "Available",         COLORS["success"]),
            ("lent_copies",      "Lent Out",          COLORS["warning"]),
            ("total_members",    "Members",           "#3498db"),
        ]

        for idx, (key, label, color) in enumerate(card_defs):
            card = create_card_frame(cards_frame)
            card.grid(row=0, column=idx, sticky="nsew", padx=6, pady=4)

            accent = tk.Frame(card, bg=color, height=4)
            accent.pack(fill="x", pady=(0, 8))

            value_lbl = tk.Label(card, text="0", font=FONTS["card_value"],
                                  bg=COLORS["card_bg"], fg=color)
            value_lbl.pack()

            tk.Label(card, text=label, font=FONTS["card_label"],
                     bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(
                pady=(2, 0))

            self._card_labels[key] = value_lbl

        # ── Two‑panel area: Most Borrowed + Overdue ──
        panels = ttk.Frame(self, style="TFrame")
        panels.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        panels.columnconfigure(0, weight=1)
        panels.columnconfigure(1, weight=1)

        # Most Borrowed Books
        left = create_card_frame(panels)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ttk.Label(left, text="🏆 Most Borrowed Books", style="Card.TLabel",
                  font=FONTS["subheading"]).pack(anchor="w", pady=(0, 8))

        cols_borrow = ("title", "author", "count")
        self._borrow_tree = ttk.Treeview(
            left, columns=cols_borrow, show="headings", height=6)
        for col in cols_borrow:
            self._borrow_tree.heading(col, text=col.title())
            self._borrow_tree.column(col, width=140, anchor="center")
        self._borrow_tree.column("title", anchor="w", width=180)
        self._borrow_tree.column("author", anchor="w", width=140)
        self._borrow_tree.column("count", width=80)
        self._borrow_tree.pack(fill="both", expand=True)

        # Overdue Books
        right = create_card_frame(panels)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ttk.Label(right, text="⚠️ Overdue Books", style="Card.TLabel",
                  font=FONTS["subheading"]).pack(anchor="w", pady=(0, 8))

        cols_overdue = ("book", "member", "due_date")
        self._overdue_tree = ttk.Treeview(
            right, columns=cols_overdue, show="headings", height=6)
        for col in cols_overdue:
            self._overdue_tree.heading(col, text=col.replace("_", " ").title())
            self._overdue_tree.column(col, width=140, anchor="center")
        self._overdue_tree.column("book", anchor="w", width=180)
        self._overdue_tree.column("member", anchor="w", width=140)
        self._overdue_tree.pack(fill="both", expand=True)

        # ── Genre Distribution ──
        genre_frame = create_card_frame(self)
        genre_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 0))

        ttk.Label(genre_frame, text="📚 Genre Distribution", style="Card.TLabel",
                  font=FONTS["subheading"]).pack(anchor="w", pady=(0, 8))

        cols_genre = ("genre", "count")
        self._genre_tree = ttk.Treeview(
            genre_frame, columns=cols_genre, show="headings", height=5)
        for col in cols_genre:
            self._genre_tree.heading(col, text=col.title())
            self._genre_tree.column(col, width=200, anchor="center")
        self._genre_tree.column("genre", anchor="w")
        self._genre_tree.pack(fill="both", expand=True)

        # Load data
        self._load_reports()

    # ── Data loading ────────────────────────────────────────────────────

    def _load_reports(self):
        """Fetch and display all report data."""
        try:
            # Summary cards
            summary = ReportService.get_inventory_summary()
            for key, lbl in self._card_labels.items():
                lbl.config(text=str(summary.get(key, 0)))

            # Most borrowed
            self._borrow_tree.delete(*self._borrow_tree.get_children())
            for book in ReportService.get_most_borrowed_books(10):
                self._borrow_tree.insert("", "end", values=(
                    book["title"], book["author"], book["borrow_count"],
                ))

            # Overdue
            self._overdue_tree.delete(*self._overdue_tree.get_children())
            for lending in ReportService.get_overdue_books():
                self._overdue_tree.insert("", "end", values=(
                    lending["book_title"], lending["member_name"],
                    str(lending["due_date"]),
                ))

            # Genre
            self._genre_tree.delete(*self._genre_tree.get_children())
            for genre in ReportService.get_genre_distribution():
                self._genre_tree.insert("", "end", values=(
                    genre["genre"], genre["count"],
                ))
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load reports: {exc}")

    def refresh(self):
        """Reload report data."""
        self._load_reports()
