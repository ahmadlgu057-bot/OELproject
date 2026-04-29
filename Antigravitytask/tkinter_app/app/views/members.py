"""
Member registration and management view.

Provides CRUD interface for library members: register, search,
edit details, and deactivate memberships.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.services.member_service import MemberService
from app.utils.style import COLORS, FONTS, create_card_frame, create_styled_button


class MembersView(ttk.Frame):
    """Member registration and management UI panel."""

    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build_ui()
        self._load_members()

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Build the members management layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header
        ttk.Label(self, text="👥  Member Management",
                  style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 15))

        # ── Registration Form ──
        form_card = create_card_frame(self)
        form_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        form_card.columnconfigure((1, 3), weight=1)

        ttk.Label(form_card, text="Register New Member", style="Card.TLabel",
                  font=FONTS["subheading"]).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        self._entries = {}
        fields = [
            ("Name:", "name", 1, 0),
            ("Email:", "email", 1, 2),
            ("Phone:", "phone", 2, 0),
            ("Address:", "address", 2, 2),
        ]

        for label, key, row, col in fields:
            ttk.Label(form_card, text=label, style="Card.TLabel",
                      font=FONTS["body_bold"]).grid(
                row=row, column=col, sticky="w", padx=(0, 5), pady=4)
            entry = ttk.Entry(form_card, width=25, font=FONTS["entry"])
            entry.grid(row=row, column=col + 1, sticky="ew", padx=(0, 15), pady=4)
            self._entries[key] = entry

        btn_frame = ttk.Frame(form_card, style="Card.TFrame")
        btn_frame.grid(row=3, column=0, columnspan=4, sticky="e", pady=(10, 0))

        create_styled_button(
            btn_frame, text="➕ Register", command=self._register_member,
            style_name="Success.TButton",
        ).pack(side="left", padx=4)

        create_styled_button(
            btn_frame, text="🔄 Clear", command=self._clear_form,
        ).pack(side="left", padx=4)

        # ── Search Bar ──
        search_bar = ttk.Frame(self, style="TFrame")
        search_bar.grid(row=1, column=0, sticky="se", pady=(0, 5))

        ttk.Label(search_bar, text="🔍", font=("Segoe UI Emoji", 14)).pack(
            side="left", padx=(0, 5))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._search_members())
        ttk.Entry(search_bar, textvariable=self._search_var,
                  width=30, font=FONTS["entry"]).pack(side="left")

        # ── Members Table ──
        table_frame = ttk.Frame(self, style="TFrame")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "name", "email", "phone", "address", "membership_date", "status")
        self._tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse",
        )

        col_widths = {"id": 50, "name": 160, "email": 180, "phone": 120,
                      "address": 160, "membership_date": 110, "status": 80}
        for col in columns:
            self._tree.heading(col, text=col.replace("_", " ").title())
            self._tree.column(col, width=col_widths.get(col, 100), anchor="center")

        self._tree.column("name", anchor="w")
        self._tree.column("email", anchor="w")
        self._tree.column("address", anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Action buttons
        action_frame = ttk.Frame(self, style="TFrame")
        action_frame.grid(row=3, column=0, sticky="e", pady=(10, 0))

        create_styled_button(
            action_frame, text="✏️ Edit", command=self._edit_member,
        ).pack(side="left", padx=4)

        create_styled_button(
            action_frame, text="🚫 Deactivate", command=self._deactivate_member,
            style_name="Danger.TButton",
        ).pack(side="left", padx=4)

        create_styled_button(
            action_frame, text="🔄 Refresh", command=self._load_members,
        ).pack(side="left", padx=4)

    # ── Data operations ─────────────────────────────────────────────────

    def _load_members(self):
        """Fetch and display all members."""
        self._tree.delete(*self._tree.get_children())
        try:
            members = MemberService.get_all_members()
            for member in members:
                status = "Active" if member.get("is_active", True) else "Inactive"
                self._tree.insert("", "end", values=(
                    member["id"], member["name"], member["email"],
                    member.get("phone", ""), member.get("address", ""),
                    str(member.get("membership_date", "")), status,
                ))
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load members: {exc}")

    def _search_members(self):
        """Filter members by search query."""
        keyword = self._search_var.get().strip()
        self._tree.delete(*self._tree.get_children())
        try:
            members = MemberService.search_members(keyword)
            for member in members:
                status = "Active" if member.get("is_active", True) else "Inactive"
                self._tree.insert("", "end", values=(
                    member["id"], member["name"], member["email"],
                    member.get("phone", ""), member.get("address", ""),
                    str(member.get("membership_date", "")), status,
                ))
        except Exception as exc:
            messagebox.showerror("Error", f"Search failed: {exc}")

    def _register_member(self):
        """Register a new member from form inputs."""
        try:
            name = self._entries["name"].get().strip()
            email = self._entries["email"].get().strip()
            phone = self._entries["phone"].get().strip()
            address = self._entries["address"].get().strip()

            MemberService.register_member(name, email, phone, address)
            messagebox.showinfo("Success", f"Member '{name}' registered!")
            self._clear_form()
            self._load_members()
        except ValueError as ve:
            messagebox.showwarning("Validation Error", str(ve))
        except Exception as exc:
            messagebox.showerror("Error", f"Registration failed: {exc}")

    def _edit_member(self):
        """Open edit dialog for the selected member."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a member to edit.")
            return

        values = self._tree.item(selected[0], "values")
        member_id = int(values[0])
        self._open_edit_dialog(member_id, values)

    def _open_edit_dialog(self, member_id: int, current_values):
        """Show a top‑level edit window for the member."""
        dialog = tk.Toplevel(self)
        dialog.title("Edit Member")
        dialog.geometry("450x320")
        dialog.configure(bg=COLORS["bg_dark"])
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Edit Member", style="Subheading.TLabel").pack(
            pady=(15, 10))

        form = ttk.Frame(dialog, style="TFrame")
        form.pack(padx=30, fill="x")

        labels = ["Name", "Email", "Phone", "Address"]
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
                    "name": entries["name"].get().strip(),
                    "email": entries["email"].get().strip(),
                    "phone": entries["phone"].get().strip(),
                    "address": entries["address"].get().strip(),
                }
                MemberService.update_member(member_id, **fields)
                messagebox.showinfo("Success", "Member updated!")
                dialog.destroy()
                self._load_members()
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

    def _deactivate_member(self):
        """Deactivate the selected member after confirmation."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a member.")
            return

        values = self._tree.item(selected[0], "values")
        member_id = int(values[0])
        name = values[1]

        if not messagebox.askyesno("Confirm",
                                    f"Deactivate member '{name}'?"):
            return

        try:
            MemberService.deactivate_member(member_id)
            messagebox.showinfo("Done", f"Member '{name}' deactivated.")
            self._load_members()
        except ValueError as ve:
            messagebox.showwarning("Error", str(ve))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _clear_form(self):
        """Clear all form entries."""
        for entry in self._entries.values():
            entry.delete(0, tk.END)

    def refresh(self):
        """Reload member table."""
        self._load_members()
