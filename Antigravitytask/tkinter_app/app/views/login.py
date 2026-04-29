"""
Login window.

Provides the authentication screen with username/password fields
and a styled login form that gates access to the main dashboard.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.services.auth import AuthService
from app.utils.style import COLORS, FONTS, create_styled_button


class LoginView(ttk.Frame):
    """Login screen — the first view users see on launch."""

    def __init__(self, parent, on_login_success):
        """
        Args:
            parent:           The parent Tk widget.
            on_login_success: Callback receiving the authenticated user dict.
        """
        super().__init__(parent, style="TFrame")
        self._on_login_success = on_login_success
        self._build_ui()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build the login form layout."""
        # Centre container
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, style="TFrame")
        container.grid(row=0, column=0)

        # ── Logo / Title area ──
        title_frame = ttk.Frame(container, style="TFrame")
        title_frame.pack(pady=(0, 30))

        # Book icon using Unicode
        icon_label = tk.Label(
            title_frame, text="📚", font=("Segoe UI Emoji", 48),
            bg=COLORS["bg_dark"], fg=COLORS["accent"],
        )
        icon_label.pack()

        title_label = ttk.Label(
            title_frame, text="Library Management System",
            style="Heading.TLabel",
        )
        title_label.pack(pady=(10, 0))

        subtitle = ttk.Label(
            title_frame, text="Sign in to your account",
            foreground=COLORS["text_secondary"],
        )
        subtitle.pack(pady=(5, 0))

        # ── Login card ──
        card = ttk.Frame(container, style="Card.TFrame")
        card.pack(padx=40, pady=10, ipadx=30, ipady=20)

        # Username
        ttk.Label(card, text="Username", style="Card.TLabel",
                  font=FONTS["body_bold"]).pack(anchor="w", padx=5, pady=(15, 4))
        self._username_entry = ttk.Entry(card, width=35, font=FONTS["entry"])
        self._username_entry.pack(padx=5, pady=(0, 8))

        # Password
        ttk.Label(card, text="Password", style="Card.TLabel",
                  font=FONTS["body_bold"]).pack(anchor="w", padx=5, pady=(8, 4))
        self._password_entry = ttk.Entry(
            card, width=35, font=FONTS["entry"], show="•"
        )
        self._password_entry.pack(padx=5, pady=(0, 15))

        # Login button
        login_btn = create_styled_button(
            card, text="  Sign In  ", command=self._handle_login,
        )
        login_btn.pack(pady=(10, 5), ipadx=20)

        # Status label
        self._status_label = ttk.Label(
            card, text="", style="Card.TLabel",
            foreground=COLORS["danger"],
        )
        self._status_label.pack(pady=(5, 5))

        # Bind Enter key
        self._username_entry.bind("<Return>", lambda e: self._handle_login())
        self._password_entry.bind("<Return>", lambda e: self._handle_login())

        # Auto‑focus username
        self._username_entry.focus_set()

    # ── Event handlers ──────────────────────────────────────────────────

    def _handle_login(self):
        """Validate credentials and invoke the success callback."""
        username = self._username_entry.get().strip()
        password = self._password_entry.get().strip()

        if not username or not password:
            self._status_label.config(text="Please enter username and password.")
            return

        try:
            user = AuthService.login(username, password)
            if user:
                self._on_login_success(user)
            else:
                self._status_label.config(text="Invalid username or password.")
                self._password_entry.delete(0, tk.END)
        except Exception as exc:
            messagebox.showerror("Login Error", str(exc))
