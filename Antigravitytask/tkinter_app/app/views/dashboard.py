"""
Dashboard window.

Serves as the main navigation hub after login. Displays a sidebar with
links to every management panel and a summary of key library metrics.
"""

import tkinter as tk
from tkinter import ttk

from app.services.report_service import ReportService
from app.utils.style import COLORS, FONTS, create_card_frame


class DashboardView(ttk.Frame):
    """Main dashboard with sidebar navigation and summary cards."""

    def __init__(self, parent, user: dict, navigate_callback):
        """
        Args:
            parent:            Parent Tk widget.
            user:              Authenticated user dict.
            navigate_callback: ``fn(view_name: str)`` to switch panels.
        """
        super().__init__(parent, style="TFrame")
        self._user = user
        self._navigate = navigate_callback
        self._build_ui()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build sidebar + content area."""
        self.columnconfigure(0, weight=0)  # sidebar
        self.columnconfigure(1, weight=1)  # content
        self.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()

    def _build_sidebar(self):
        """Build the dark navigation sidebar."""
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=220)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        # App title
        title_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        title_frame.pack(fill="x", pady=(20, 10), padx=15)

        tk.Label(
            title_frame, text="📚", font=("Segoe UI Emoji", 24),
            bg=COLORS["sidebar_bg"], fg=COLORS["accent"],
        ).pack()

        ttk.Label(
            title_frame, text="LibraryMS", style="Sidebar.TLabel",
            font=FONTS["subheading"],
        ).pack(pady=(5, 0))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=15, pady=10)

        # User info
        ttk.Label(
            sidebar, text=f"👤  {self._user['username']}",
            style="Sidebar.TLabel", font=FONTS["small"],
        ).pack(padx=15, anchor="w")

        ttk.Label(
            sidebar, text=f"Role: {self._user['role'].title()}",
            style="Sidebar.TLabel", font=FONTS["small"],
            foreground=COLORS["text_secondary"],
        ).pack(padx=15, anchor="w", pady=(2, 10))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=15, pady=5)

        # Navigation buttons
        nav_items = [
            ("🏠  Dashboard",   "dashboard"),
            ("📖  Books",       "books"),
            ("👥  Members",     "members"),
            ("📤  Lend Book",   "lending"),
            ("📥  Return Book", "returns"),
            ("📊  Reports",     "reports"),
            ("💰  Fines",       "fines"),
        ]

        for text, view_name in nav_items:
            btn = tk.Button(
                sidebar, text=text, anchor="w",
                font=FONTS["sidebar"],
                bg=COLORS["sidebar_bg"], fg=COLORS["text_primary"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["text_primary"],
                bd=0, padx=20, pady=10, cursor="hand2",
                command=lambda v=view_name: self._navigate(v),
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["sidebar_hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["sidebar_bg"]))

        # Spacer + Logout
        spacer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        spacer.pack(fill="both", expand=True)

        logout_btn = tk.Button(
            sidebar, text="🚪  Logout", anchor="w",
            font=FONTS["sidebar"],
            bg=COLORS["danger"], fg="#ffffff",
            activebackground="#c0392b", activeforeground="#ffffff",
            bd=0, padx=20, pady=10, cursor="hand2",
            command=lambda: self._navigate("logout"),
        )
        logout_btn.pack(fill="x", side="bottom", pady=(0, 15))

    def _build_content(self):
        """Build the main content area with summary cards."""
        content = ttk.Frame(self, style="TFrame")
        content.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        content.columnconfigure((0, 1, 2), weight=1)

        # Welcome header
        ttk.Label(
            content, text=f"Welcome, {self._user['username'].title()}!",
            style="Heading.TLabel",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))

        ttk.Label(
            content, text="Library Management System — Dashboard Overview",
            foreground=COLORS["text_secondary"],
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 25))

        # Summary cards
        try:
            summary = ReportService.get_inventory_summary()
        except Exception:
            summary = {
                "total_books": 0, "total_copies": 0, "available_copies": 0,
                "lent_copies": 0, "total_members": 0, "active_lendings": 0,
            }

        cards_data = [
            ("Total Books",      str(summary["total_books"]),      COLORS["accent"]),
            ("Available Copies", str(summary["available_copies"]), COLORS["success"]),
            ("Lent Out",         str(summary["lent_copies"]),      COLORS["warning"]),
            ("Active Members",   str(summary["total_members"]),    "#3498db"),
            ("Active Lendings",  str(summary["active_lendings"]),  "#9b59b6"),
            ("Total Copies",     str(summary["total_copies"]),     "#1abc9c"),
        ]

        for idx, (label, value, color) in enumerate(cards_data):
            row = 2 + idx // 3
            col = idx % 3
            card = create_card_frame(content)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

            # Coloured accent bar
            accent_bar = tk.Frame(card, bg=color, height=4)
            accent_bar.pack(fill="x", pady=(0, 12))

            tk.Label(
                card, text=value, font=FONTS["card_value"],
                bg=COLORS["card_bg"], fg=color,
            ).pack()

            tk.Label(
                card, text=label, font=FONTS["card_label"],
                bg=COLORS["card_bg"], fg=COLORS["text_secondary"],
            ).pack(pady=(4, 0))

    def refresh(self):
        """Rebuild content area to update metrics."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
