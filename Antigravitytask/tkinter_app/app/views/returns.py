"""
Book return view.

Allows librarians to process book returns by selecting an active lending
record and marking it as returned, with automatic fine calculation.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.services.lending_service import LendingService
from app.services.member_service import MemberService
from app.utils.style import COLORS, FONTS, create_card_frame, create_styled_button


class ReturnsView(ttk.Frame):
    """Book return processing UI panel."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self._load_members()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build the returns layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header
        ttk.Label(self, text="📥  Return a Book",
                  style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 15))

        # ── Member lookup ──
        lookup_card = create_card_frame(self)
        lookup_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        lookup_card.columnconfigure(1, weight=1)

        ttk.Label(lookup_card, text="Select Member:", style="Card.TLabel",
                  font=FONTS["body_bold"]).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=4)

        self._member_combo = ttk.Combobox(
            lookup_card, width=40, font=FONTS["entry"], state="readonly")
        self._member_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=4)
        self._member_combo.bind("<<ComboboxSelected>>", self._on_member_selected)

        create_styled_button(
            lookup_card, text="🔍 Show Lendings",
            command=self._show_member_lendings,
        ).grid(row=0, column=2, padx=4, pady=4)

        # ── Active Lendings for Selected Member ──
        ttk.Label(self, text="Active Lendings",
                  style="Subheading.TLabel").grid(
            row=1, column=0, sticky="sw", pady=(50, 5))

        table_frame = ttk.Frame(self, style="TFrame")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "book", "lend_date", "due_date", "status")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse",
        )

        col_widths = {"id": 60, "book": 280, "lend_date": 130,
                      "due_date": 130, "status": 100}
        for col in columns:
            self._tree.heading(col, text=col.replace("_", " ").title())
            self._tree.column(col, width=col_widths.get(col, 100), anchor="center")
        self._tree.column("book", anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Action buttons
        action_frame = ttk.Frame(self, style="TFrame")
        action_frame.grid(row=3, column=0, sticky="e", pady=(10, 0))

        create_styled_button(
            action_frame, text="📥 Return Selected Book",
            command=self._return_book, style_name="Success.TButton",
        ).pack(side="left", padx=4)

        # Fine display area
        self._fine_label = ttk.Label(
            self, text="", style="Warning.TLabel", font=FONTS["subheading"],
        )
        self._fine_label.grid(row=4, column=0, sticky="w", pady=(15, 0))

    # ── Data operations ─────────────────────────────────────────────────

    def _load_members(self):
        """Populate the member dropdown."""
        try:
            members = MemberService.get_all_members()
            self._members_map = {
                f"{m['id']} — {m['name']}": m["id"] for m in members
            }
            self._member_combo["values"] = list(self._members_map.keys())
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load members: {exc}")

    def _on_member_selected(self, _event=None):
        """Triggered when a member is selected from the combo box."""
        self._show_member_lendings()

    def _show_member_lendings(self):
        """Show active lendings for the selected member."""
        member_key = self._member_combo.get()
        if not member_key:
            messagebox.showwarning("Missing", "Please select a member.")
            return

        member_id = self._members_map[member_key]
        self._tree.delete(*self._tree.get_children())
        self._fine_label.config(text="")

        try:
            lendings = LendingService.get_active_member_lendings(member_id)
            if not lendings:
                messagebox.showinfo("Info", "No active lendings for this member.")
                return

            for lending in lendings:
                self._tree.insert("", "end", values=(
                    lending["id"],
                    lending["book_title"],
                    str(lending["lend_date"]),
                    str(lending["due_date"]),
                    lending["status"].title(),
                ))
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load lendings: {exc}")

    def _return_book(self):
        """Process the return of the selected lending."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("No Selection",
                                    "Please select a lending to return.")
            return

        values = self._tree.item(selected[0], "values")
        lending_id = int(values[0])
        book_title = values[1]

        if not messagebox.askyesno("Confirm Return",
                                    f"Return '{book_title}'?"):
            return

        try:
            result = LendingService.return_book(lending_id)
            fine = result["fine_amount"]
            days = result["days_overdue"]

            if fine > 0:
                self._fine_label.config(
                    text=f"⚠️  Fine: ${fine:.2f} ({days} days overdue)",
                )
                messagebox.showwarning(
                    "Fine Applied",
                    f"Book returned with a fine of ${fine:.2f} "
                    f"({days} days overdue).",
                )
            else:
                self._fine_label.config(text="✅  Book returned on time!")
                messagebox.showinfo("Success", "Book returned successfully!")

            self._show_member_lendings()
        except ValueError as ve:
            messagebox.showwarning("Error", str(ve))
        except Exception as exc:
            messagebox.showerror("Error", f"Return failed: {exc}")

    def refresh(self):
        """Reload member list."""
        self._load_members()
        self._tree.delete(*self._tree.get_children())
        self._fine_label.config(text="")
