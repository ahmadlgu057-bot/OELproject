"""
Application entry point.

Creates the main Tk window, applies the dark theme, and manages
navigation between the login screen and the dashboard panels.
"""

import tkinter as tk
from tkinter import ttk

from app.config import APP_HEIGHT, APP_TITLE, APP_WIDTH
from app.utils.style import COLORS, configure_styles

from app.views.login import LoginView
from app.views.dashboard import DashboardView
from app.views.books import BooksView
from app.views.members import MembersView
from app.views.lending import LendingView
from app.views.returns import ReturnsView
from app.views.reports import ReportsView
from app.views.fines import FinesView


class LibraryApp:
    """Top‑level application controller."""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title(APP_TITLE)
        self._root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self._root.minsize(900, 550)

        # Centre the window on screen
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth() - APP_WIDTH) // 2
        y = (self._root.winfo_screenheight() - APP_HEIGHT) // 2
        self._root.geometry(f"+{x}+{y}")

        # Apply dark theme
        configure_styles(self._root)

        self._current_frame: ttk.Frame | None = None
        self._user: dict | None = None

        # Start with the login screen
        self._show_login()

    # ── Navigation ──────────────────────────────────────────────────────

    def _clear_frame(self):
        """Destroy the current top‑level frame."""
        if self._current_frame is not None:
            self._current_frame.destroy()
            self._current_frame = None

    def _show_login(self):
        """Display the login view."""
        self._clear_frame()
        self._user = None
        self._current_frame = LoginView(self._root, self._on_login_success)
        self._current_frame.pack(fill="both", expand=True)

    def _on_login_success(self, user: dict):
        """Callback when login succeeds — show dashboard."""
        self._user = user
        self._show_dashboard_view("dashboard")

    def _show_dashboard_view(self, view_name: str):
        """
        Show a dashboard panel identified by *view_name*.

        The dashboard is rebuilt each time so the sidebar stays visible
        and the content area swaps to the requested sub‑view.
        """
        if view_name == "logout":
            self._show_login()
            return

        self._clear_frame()

        # Outer container: sidebar (from DashboardView) + right content
        container = ttk.Frame(self._root, style="TFrame")
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        # Sidebar (reuse DashboardView just for its sidebar)
        sidebar_source = DashboardView(
            container, self._user, self._show_dashboard_view,
        )
        # We only want the sidebar from DashboardView, but it's simpler
        # to rebuild the whole thing and just use the navigate callback.

        # Actually, let's build a proper sidebar + content layout.
        container.destroy()

        self._clear_frame()
        outer = ttk.Frame(self._root, style="TFrame")
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=0)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(0, weight=1)

        # Sidebar
        self._build_sidebar(outer)

        # Content area
        content_wrapper = ttk.Frame(outer, style="TFrame")
        content_wrapper.grid(row=0, column=1, sticky="nsew", padx=20, pady=15)
        content_wrapper.columnconfigure(0, weight=1)
        content_wrapper.rowconfigure(0, weight=1)

        content_view = self._create_view(view_name, content_wrapper)
        content_view.grid(row=0, column=0, sticky="nsew")

        self._current_frame = outer

    def _build_sidebar(self, parent):
        """Build the navigation sidebar."""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", width=220)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        # Title
        title_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        title_frame.pack(fill="x", pady=(20, 10), padx=15)

        tk.Label(
            title_frame, text="📚", font=("Segoe UI Emoji", 24),
            bg=COLORS["sidebar_bg"], fg=COLORS["accent"],
        ).pack()

        ttk.Label(
            title_frame, text="LibraryMS", style="Sidebar.TLabel",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(5, 0))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=15, pady=10)

        # User info
        ttk.Label(
            sidebar, text=f"👤  {self._user['username']}",
            style="Sidebar.TLabel", font=("Segoe UI", 9),
        ).pack(padx=15, anchor="w")

        ttk.Label(
            sidebar, text=f"Role: {self._user['role'].title()}",
            style="Sidebar.TLabel", font=("Segoe UI", 9),
            foreground=COLORS["text_secondary"],
        ).pack(padx=15, anchor="w", pady=(2, 10))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=15, pady=5)

        # Nav items
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
                font=("Segoe UI", 12),
                bg=COLORS["sidebar_bg"], fg=COLORS["text_primary"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["text_primary"],
                bd=0, padx=20, pady=10, cursor="hand2",
                command=lambda v=view_name: self._show_dashboard_view(v),
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["sidebar_hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["sidebar_bg"]))

        # Logout at bottom
        spacer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        spacer.pack(fill="both", expand=True)

        logout_btn = tk.Button(
            sidebar, text="🚪  Logout", anchor="w",
            font=("Segoe UI", 12),
            bg=COLORS["danger"], fg="#ffffff",
            activebackground="#c0392b", activeforeground="#ffffff",
            bd=0, padx=20, pady=10, cursor="hand2",
            command=lambda: self._show_dashboard_view("logout"),
        )
        logout_btn.pack(fill="x", side="bottom", pady=(0, 15))

    def _create_view(self, view_name: str, parent) -> ttk.Frame:
        """Instantiate and return the requested view panel."""
        views = {
            "dashboard": lambda: DashboardContent(parent, self._user),
            "books":     lambda: BooksView(parent),
            "members":   lambda: MembersView(parent),
            "lending":   lambda: LendingView(parent),
            "returns":   lambda: ReturnsView(parent),
            "reports":   lambda: ReportsView(parent),
            "fines":     lambda: FinesView(parent),
        }

        factory = views.get(view_name, views["dashboard"])
        return factory()

    def run(self):
        """Start the Tkinter main loop."""
        self._root.mainloop()


class DashboardContent(ttk.Frame):
    """The dashboard home content (summary cards only, no sidebar)."""

    def __init__(self, parent, user: dict):
        super().__init__(parent, style="TFrame")
        self._user = user
        self._build_ui()

    def _build_ui(self):
        """Build summary cards for the dashboard home."""
        self.columnconfigure((0, 1, 2), weight=1)

        # Welcome
        ttk.Label(
            self, text=f"Welcome, {self._user['username'].title()}!",
            style="Heading.TLabel",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))

        ttk.Label(
            self, text="Library Management System — Dashboard Overview",
            foreground=COLORS["text_secondary"],
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 25))

        # Summary cards
        from app.services.report_service import ReportService
        try:
            summary = ReportService.get_inventory_summary()
        except Exception:
            summary = {
                "total_books": 0, "total_copies": 0, "available_copies": 0,
                "lent_copies": 0, "total_members": 0, "active_lendings": 0,
            }

        cards = [
            ("Total Books",      str(summary["total_books"]),      COLORS["accent"]),
            ("Available Copies", str(summary["available_copies"]), COLORS["success"]),
            ("Lent Out",         str(summary["lent_copies"]),      COLORS["warning"]),
            ("Active Members",   str(summary["total_members"]),    "#3498db"),
            ("Active Lendings",  str(summary["active_lendings"]),  "#9b59b6"),
            ("Total Copies",     str(summary["total_copies"]),     "#1abc9c"),
        ]

        from app.utils.style import create_card_frame, FONTS as _FONTS

        for idx, (label, value, color) in enumerate(cards):
            row = 2 + idx // 3
            col = idx % 3
            card = create_card_frame(self)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

            tk.Frame(card, bg=color, height=4).pack(fill="x", pady=(0, 12))

            tk.Label(card, text=value, font=_FONTS["card_value"],
                     bg=COLORS["card_bg"], fg=color).pack()

            tk.Label(card, text=label, font=_FONTS["card_label"],
                     bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(
                pady=(4, 0))


# ── Entry point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = LibraryApp()
    app.run()
