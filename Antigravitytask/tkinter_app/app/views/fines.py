"""
Fine calculation view.

Displays outstanding fines, allows searching fines by member,
and shows detailed fine breakdowns per lending record.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.services.fine_service import FineService
from app.services.member_service import MemberService
from app.utils.style import COLORS, FONTS, create_card_frame, create_styled_button


class FinesView(ttk.Frame):
    """Fine calculation and display UI panel."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self._load_data()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build the fines layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # Header
        ttk.Label(self, text="💰  Fine Management",
                  style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 15))

        # ── Member Lookup ──
        lookup_card = create_card_frame(self)
        lookup_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        lookup_card.columnconfigure(1, weight=1)

        ttk.Label(lookup_card, text="Search by Member:", style="Card.TLabel",
                  font=FONTS["body_bold"]).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=4)

        self._member_combo = ttk.Combobox(
            lookup_card, width=40, font=FONTS["entry"], state="readonly")
        self._member_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=4)

        create_styled_button(
            lookup_card, text="🔍 View Fines",
            command=self._show_member_fines,
        ).grid(row=0, column=2, padx=(4, 0), pady=4)

        create_styled_button(
            lookup_card, text="📋 All Outstanding",
            command=self._show_all_outstanding,
        ).grid(row=0, column=3, padx=4, pady=4)

        # ── Total Fine Display ──
        self._total_frame = create_card_frame(self)
        self._total_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self._total_label = tk.Label(
            self._total_frame, text="Total Fines: $0.00",
            font=FONTS["subheading"], bg=COLORS["card_bg"],
            fg=COLORS["warning"],
        )
        self._total_label.pack(anchor="w")

        self._summary_label = tk.Label(
            self._total_frame, text="Select a member or view all outstanding fines",
            font=FONTS["body"], bg=COLORS["card_bg"],
            fg=COLORS["text_secondary"],
        )
        self._summary_label.pack(anchor="w", pady=(4, 0))

        # ── Fines Table ──
        table_frame = ttk.Frame(self, style="TFrame")
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("lending_id", "book", "member", "due_date",
                    "days_overdue", "fine", "status")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse",
        )

        col_widths = {
            "lending_id": 70, "book": 200, "member": 150,
            "due_date": 110, "days_overdue": 100, "fine": 90, "status": 90,
        }
        for col in columns:
            heading = col.replace("_", " ").title()
            self._tree.heading(col, text=heading)
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
        """Load member dropdown and show outstanding fines."""
        try:
            members = MemberService.get_all_members()
            self._members_map = {
                f"{m['id']} — {m['name']}": m["id"] for m in members
            }
            self._member_combo["values"] = list(self._members_map.keys())
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load members: {exc}")

        self._show_all_outstanding()

    def _show_member_fines(self):
        """Display fines for the selected member."""
        member_key = self._member_combo.get()
        if not member_key:
            messagebox.showwarning("Missing", "Please select a member.")
            return

        member_id = self._members_map[member_key]
        member_name = member_key.split(" — ", 1)[1]

        try:
            fines = FineService.get_member_fines(member_id)
            total = FineService.get_total_fines_for_member(member_id)

            self._tree.delete(*self._tree.get_children())
            for fine in fines:
                self._tree.insert("", "end", values=(
                    fine["lending_id"],
                    fine["book_title"],
                    member_name,
                    fine["due_date"],
                    fine["days_overdue"],
                    f"${fine['fine_amount']:.2f}",
                    fine["status"].title(),
                ))

            self._total_label.config(text=f"Total Fines: ${total:.2f}")
            self._summary_label.config(
                text=f"Showing {len(fines)} fine record(s) for {member_name}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load fines: {exc}")

    def _show_all_outstanding(self):
        """Display all outstanding (unreturned overdue) fines."""
        try:
            fines = FineService.get_all_outstanding_fines()
            total = sum(f["fine_amount"] for f in fines)

            self._tree.delete(*self._tree.get_children())
            for fine in fines:
                self._tree.insert("", "end", values=(
                    fine["lending_id"],
                    fine["book_title"],
                    fine["member_name"],
                    fine["due_date"],
                    fine["days_overdue"],
                    f"${fine['fine_amount']:.2f}",
                    "Overdue",
                ))

            self._total_label.config(
                text=f"Total Outstanding Fines: ${total:.2f}")
            self._summary_label.config(
                text=f"Showing {len(fines)} outstanding fine(s)")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load fines: {exc}")

    def refresh(self):
        """Reload data."""
        self._load_data()
